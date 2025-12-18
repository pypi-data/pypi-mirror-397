"""OpenAPI specification generator from Router."""

from dataclasses import dataclass, field
from typing import Any
import logging
import re

from django.http import HttpResponseBase
from django.urls import reverse
import pydantic

from ..routing import HttpMethod, RegisteredView, Route, RouteMap, Router
from ..status import Status
from .introspection import ViewTypeInfo, infer_view_types, is_empty_model
from .models import (
    Components,
    Info,
    MediaType,
    OpenAPI,
    Operation,
    Parameter,
    PathItem,
    Reference,
    RequestBody,
    Response,
    Server,
)
from .path_parser import (
    PathParam,
    get_placeholder_kwargs,
    parse_django_path_params,
    replace_placeholders_with_openapi_params,
)

logger = logging.getLogger(__name__)


@dataclass
class OpenAPIGeneratorConfig:
    """Configuration for OpenAPI spec generation."""

    title: str
    version: str
    description: str | None = None
    servers: list[Server] = field(default_factory=list)
    auth_security_scheme: str | None = None
    default_success_status: Status = Status.HTTP_200_OK
    include_validation_errors: bool = True


class OpenAPIGenerator:
    """Generates OpenAPI 3.1 specifications from Router instances."""

    def __init__(
        self,
        config: OpenAPIGeneratorConfig,
    ) -> None:
        self.config = config
        self._schemas: dict[str, dict[str, Any]] = {}
        self._schema_refs: dict[str, str] = {}

    def generate(
        self,
        router: Router,
        namespace: str | None = None,
    ) -> OpenAPI:
        """Generate a complete OpenAPI spec from a Router."""
        return self.generate_from_routes(router.routes, namespace)

    def generate_from_routes(
        self,
        routes: RouteMap,
        namespace: str | None = None,
    ) -> OpenAPI:
        """Generate a complete OpenAPI spec from a RouteMap."""
        # Reset schema cache for this generation
        self._schemas = {}
        self._schema_refs = {}

        # Build paths
        paths: dict[str, PathItem] = {}
        for pattern, route in routes.items():
            # Resolve full path using reverse() if namespace is available
            openapi_path = self._resolve_openapi_path(pattern, route, namespace)
            path_item = self._build_path_item(pattern, route)
            paths[openapi_path] = path_item

        # Build components
        components = None
        if self._schemas:
            components = Components(schemas=self._schemas)

        return OpenAPI(
            info=Info(
                title=self.config.title,
                version=self.config.version,
                description=self.config.description,
            ),
            servers=self.config.servers if self.config.servers else None,
            paths=paths,
            components=components,
        )

    def _resolve_openapi_path(
        self,
        pattern: str,
        route: Route,
        namespace: str | None = None,
    ) -> str:
        """Resolve the full OpenAPI path for a route."""
        # Get placeholder kwargs for any path parameters
        placeholder_kwargs = get_placeholder_kwargs(pattern)
        qualified_name = f"{namespace}:{route.name}" if namespace else route.name
        full_url = reverse(qualified_name, kwargs=placeholder_kwargs or None)
        return replace_placeholders_with_openapi_params(full_url, placeholder_kwargs)

    def _build_path_item(self, pattern: str, route: Route) -> PathItem:
        """Build a PathItem from a Route."""
        path_params = parse_django_path_params(pattern)

        operations: dict[str, Operation | None] = {
            "get": None,
            "post": None,
            "put": None,
            "patch": None,
            "delete": None,
        }

        for view in route.views:
            for method in view.methods:
                operation = self._build_operation(method, view, path_params)
                method_name = method.value.lower()
                operations[method_name] = operation

        return PathItem(
            get=operations["get"],
            post=operations["post"],
            put=operations["put"],
            patch=operations["patch"],
            delete=operations["delete"],
        )

    def _build_operation(
        self,
        method: HttpMethod,
        view: RegisteredView[[], HttpResponseBase],
        path_params: list[PathParam],
    ) -> Operation:
        """Build an Operation from a RegisteredView."""
        view_info = infer_view_types(view.fn)

        # Build parameters (path + query)
        parameters = self._build_parameters(view_info, path_params)

        # Build request body
        request_body = None
        if view_info.body_model is not None:
            request_body = self._build_request_body(view_info.body_model)

        # Build responses
        responses = self._build_responses(view_info.response_model)

        # Security
        security: list[dict[str, list[str]]] | None = None
        if view_info.requires_auth and self.config.auth_security_scheme:
            security = [{self.config.auth_security_scheme: []}]

        # Operation ID from function name
        operation_id = view.fn.__name__

        params_list: list[Parameter | Reference] | None = (
            list(parameters) if parameters else None
        )
        responses_dict: dict[str, Response | Reference] = dict(responses)

        return Operation(
            operationId=operation_id,
            parameters=params_list,
            requestBody=request_body,
            responses=responses_dict,
            security=security,
        )

    def _build_parameters(
        self,
        view_info: ViewTypeInfo,
        path_params: list[PathParam],
    ) -> list[Parameter]:
        """Build Parameter objects from query model and path params."""
        parameters: list[Parameter] = []

        # Path parameters
        for param in path_params:
            schema: dict[str, Any] = {"type": param.openapi_type}
            if param.openapi_format:
                schema["format"] = param.openapi_format

            parameters.append(
                Parameter(
                    name=param.name,
                    param_in="path",
                    required=True,
                    param_schema=schema,
                )
            )

        # Query parameters from model
        if view_info.querystring_model is not None:
            # Get the JSON schema for the query model
            # Note: We call _get_or_create_schema_ref for side effects (populates _schemas)
            # but query params are expanded inline, not as a $ref
            self._get_or_create_schema_ref(view_info.querystring_model)
            # For query parameters, we reference the schema
            # Individual fields become query params
            json_schema = view_info.querystring_model.model_json_schema()
            properties = json_schema.get("properties", {})
            required_fields = set(json_schema.get("required", []))

            for field_name, field_schema in properties.items():
                parameters.append(
                    Parameter(
                        name=field_name,
                        param_in="query",
                        required=field_name in required_fields,
                        param_schema=field_schema,
                    )
                )

        return parameters

    def _build_request_body(self, body_model: type[pydantic.BaseModel]) -> RequestBody:
        """Build RequestBody from body model."""
        ref = self._get_or_create_schema_ref(body_model)

        return RequestBody(
            content={
                "application/json": MediaType(
                    media_type_schema=ref,
                ),
            },
            required=True,
        )

    def _build_responses(
        self,
        response_model: type[pydantic.BaseModel] | None,
    ) -> dict[str, Response]:
        """Build Response objects from response model."""
        responses: dict[str, Response] = {}
        success_status_key = str(self.config.default_success_status.value)

        if response_model is not None and not is_empty_model(response_model):
            ref = self._get_or_create_schema_ref(response_model)
            responses[success_status_key] = Response(
                description="Successful response",
                content={
                    "application/json": MediaType(
                        media_type_schema=ref,
                    ),
                },
            )
        else:
            responses[success_status_key] = Response(
                description="Successful response",
            )

        # Add validation error response
        if self.config.include_validation_errors:
            responses[str(Status.HTTP_400_BAD_REQUEST.value)] = Response(
                description="Validation error",
            )

        return responses

    def _get_or_create_schema_ref(
        self,
        model: type[pydantic.BaseModel],
    ) -> Reference:
        """Get or create a component schema reference for a Pydantic model."""
        # Get a unique name for this model
        model_name = self._sanitize_schema_name(self._get_model_name(model))

        if model_name in self._schema_refs:
            return Reference(ref=self._schema_refs[model_name])

        # Generate JSON Schema
        try:
            schema = model.model_json_schema(
                ref_template="#/components/schemas/{model}",
                mode="serialization",
            )
        except (
            pydantic.PydanticSchemaGenerationError,
            pydantic.PydanticUserError,
        ) as e:
            # Fallback for generic types that can't generate schema
            logger.warning(
                "Failed to generate JSON schema for model %s: %s. Using fallback.",
                model_name,
                e,
            )
            schema = {"type": "object"}

        # Extract $defs if present and merge into components
        # Sanitize all $def names to comply with OpenAPI schema naming rules
        defs = schema.pop("$defs", {})
        for def_name, def_schema in defs.items():
            sanitized_name = self._sanitize_schema_name(def_name)
            if sanitized_name not in self._schemas:
                # Update any internal $ref references to use sanitized names
                sanitized_schema = self._sanitize_schema_refs(def_schema)
                self._schemas[sanitized_name] = sanitized_schema

        # Handle allOf references that point to $defs
        if "allOf" in schema and len(schema["allOf"]) == 1:
            ref_obj = schema["allOf"][0]
            if "$ref" in ref_obj:
                # The schema is just a reference to a $def
                ref_name = ref_obj["$ref"].split("/")[-1]
                sanitized_ref_name = self._sanitize_schema_name(ref_name)
                if sanitized_ref_name in self._schemas:
                    # Use the existing schema name
                    ref_path = f"#/components/schemas/{sanitized_ref_name}"
                    self._schema_refs[model_name] = ref_path
                    return Reference(ref=ref_path)

        # Sanitize any refs in the main schema
        schema = self._sanitize_schema_refs(schema)

        # Store the main schema
        self._schemas[model_name] = schema

        ref_path = f"#/components/schemas/{model_name}"
        self._schema_refs[model_name] = ref_path

        return Reference(ref=ref_path)

    def _get_model_name(self, model: type[pydantic.BaseModel]) -> str:
        """Get a unique name for a Pydantic model."""
        if hasattr(model, "__name__"):
            return model.__name__

        # For generic types like ListOf[T], create a descriptive name
        return str(model)

    def _sanitize_schema_name(self, name: str) -> str:
        """Sanitize a schema name to comply with OpenAPI naming rules."""
        # Replace any character not in the allowed set with underscore
        result = re.sub(r"[^a-zA-Z0-9._-]", "_", name)
        # Remove any trailing underscores
        result = result.rstrip("_")
        # Ensure we have a valid name (fallback for edge cases)
        if not result:
            return "UnnamedSchema"
        return result

    def _sanitize_schema_refs(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Recursively sanitize $ref paths in a schema to use sanitized names."""
        if not isinstance(schema, dict):
            return schema

        result: dict[str, Any] = {}
        for key, value in schema.items():
            if key == "$ref" and isinstance(value, str):
                # Extract and sanitize the reference name
                if value.startswith("#/components/schemas/"):
                    ref_name = value.split("/")[-1]
                    sanitized_name = self._sanitize_schema_name(ref_name)
                    result[key] = f"#/components/schemas/{sanitized_name}"
                else:
                    result[key] = value
            elif isinstance(value, dict):
                result[key] = self._sanitize_schema_refs(value)
            elif isinstance(value, list):
                result[key] = [
                    self._sanitize_schema_refs(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[key] = value

        return result


def generate_openapi(
    router: Router,
    title: str,
    version: str,
    description: str | None = None,
    servers: list[Server] | None = None,
    namespace: str | None = None,
) -> OpenAPI:
    """Generate OpenAPI 3.1 spec from a Router with minimal configuration."""
    config = OpenAPIGeneratorConfig(
        title=title,
        version=version,
        description=description,
        servers=servers or [],
    )
    generator = OpenAPIGenerator(config)
    return generator.generate(router, namespace)
