"""End-to-end tests for OpenAPI generation with sample app."""

from typing import Any, ClassVar
from unittest import TestCase
import json
import urllib.request

from django.test import TestCase as DjangoTestCase
import jsonschema

from thelabtyping.abc import ListOf
from thelabtyping.api.openapi.generator import (
    OpenAPIGenerator,
    OpenAPIGeneratorConfig,
    generate_openapi,
)
from thelabtyping.api.requests import (
    AuthdTypedRequestBody,
    EmptyTypedRequest,
    TypedRequestQuery,
)
from thelabtyping.api.responses import APIResponse
from thelabtyping.api.routing import Router
from thelabtyping.api.serializers import Empty
from thelabtyping.api.views import validate
from thelabtyping.tests.sampleapp.views import router

from .conftest import BodyModel, OpenAPITestMixin, QueryModel, ResponseModel


class TestSampleAppOpenAPIGeneration(TestCase):
    def test_generate_spec_from_sample_router(self) -> None:
        """Generate OpenAPI spec from the sample app router."""
        spec = generate_openapi(
            router,
            title="Sample App API",
            version="1.0.0",
            description="Test API from sample app",
            namespace="sampleapp",
        )

        # Verify basic structure
        self.assertEqual(spec.openapi, "3.1.0")
        self.assertEqual(spec.info.title, "Sample App API")
        self.assertEqual(spec.info.version, "1.0.0")

    def test_sample_app_paths_exist(self) -> None:
        """Sample app routes are present in the generated spec."""
        spec = generate_openapi(
            router,
            title="Test",
            version="1.0.0",
            namespace="sampleapp",
        )

        # Check for expected paths
        self.assertIn("/api/router/users/", spec.paths)
        self.assertIn("/api/router/users/{pk}/", spec.paths)

    def test_users_list_endpoint(self) -> None:
        """Users list endpoint has GET and POST operations."""
        spec = generate_openapi(
            router,
            title="Test",
            version="1.0.0",
            namespace="sampleapp",
        )
        path_item = spec.paths["/api/router/users/"]
        self.assertIsNotNone(path_item.get)
        self.assertIsNotNone(path_item.post)

        # GET should have query parameters
        get_op = path_item.get
        assert get_op is not None  # for mypy
        self.assertIsNotNone(get_op.parameters)

        # POST should have request body and security (requires auth)
        post_op = path_item.post
        assert post_op is not None  # for mypy
        self.assertIsNotNone(post_op.requestBody)

    def test_user_detail_endpoint(self) -> None:
        """User detail endpoint has GET operation with path parameter."""
        spec = generate_openapi(
            router,
            title="Test",
            version="1.0.0",
            namespace="sampleapp",
        )

        path_item = spec.paths["/api/router/users/{pk}/"]
        self.assertIsNotNone(path_item.get)

        # Should have pk path parameter
        get_op = path_item.get
        assert get_op is not None  # for mypy
        self.assertIsNotNone(get_op.parameters)
        assert get_op.parameters is not None  # for mypy
        path_params = [
            p for p in get_op.parameters if getattr(p, "param_in", None) == "path"
        ]
        self.assertEqual(len(path_params), 1)
        self.assertEqual(path_params[0].name, "pk")  # type: ignore[union-attr]

    def test_components_schemas_generated(self) -> None:
        """Component schemas are generated for Pydantic models."""
        spec = generate_openapi(
            router,
            title="Test",
            version="1.0.0",
            namespace="sampleapp",
        )

        self.assertIsNotNone(spec.components)
        assert spec.components is not None  # for mypy
        self.assertIsNotNone(spec.components.schemas)
        assert spec.components.schemas is not None  # for mypy

        # Should have schemas for the sample app models
        schema_names = list(spec.components.schemas.keys())
        self.assertTrue(len(schema_names) > 0)

    def test_spec_serializes_to_valid_json(self) -> None:
        """Generated spec serializes to valid JSON."""
        spec = generate_openapi(
            router,
            title="Sample App API",
            version="1.0.0",
            description="Test API",
            namespace="sampleapp",
        )

        json_str = spec.model_dump_json(by_alias=True, exclude_none=True, indent=2)

        # Parse and verify
        data = json.loads(json_str)
        self.assertEqual(data["openapi"], "3.1.0")
        self.assertIn("paths", data)
        self.assertIn("components", data)

    def test_index_endpoint_included(self) -> None:
        """Router index endpoint is included if enabled."""
        spec = generate_openapi(
            router,
            title="Test",
            version="1.0.0",
            namespace="sampleapp",
        )

        # The sample app router has enable_index=True by default
        self.assertIn("/api/router/", spec.paths)


class TestOpenAPISpecStructure(TestCase):
    def test_responses_have_descriptions(self) -> None:
        """All responses have descriptions (required by OpenAPI)."""
        spec = generate_openapi(
            router,
            title="Test",
            version="1.0.0",
            namespace="sampleapp",
        )

        for path, path_item in spec.paths.items():
            for method in ["get", "post", "put", "patch", "delete"]:
                operation = getattr(path_item, method, None)
                if operation is not None:
                    for status_code, response in operation.responses.items():
                        self.assertIsNotNone(
                            response.description,
                            f"Response {status_code} for {method.upper()} {path} "
                            "has no description",
                        )

    def test_path_parameters_are_required(self) -> None:
        """Path parameters are marked as required."""
        spec = generate_openapi(
            router,
            title="Test",
            version="1.0.0",
            namespace="sampleapp",
        )

        for path, path_item in spec.paths.items():
            if "{" not in path:
                continue

            for method in ["get", "post", "put", "patch", "delete"]:
                operation = getattr(path_item, method, None)
                if operation is not None and operation.parameters:
                    path_params = [
                        p
                        for p in operation.parameters
                        if getattr(p, "param_in", None) == "path"
                    ]
                    for param in path_params:
                        self.assertTrue(
                            param.required,
                            f"Path parameter {param.name} in {path} should be required",
                        )

    def test_operation_ids_are_unique(self) -> None:
        """All operation IDs are unique across the spec."""
        spec = generate_openapi(
            router,
            title="Test",
            version="1.0.0",
            namespace="sampleapp",
        )

        operation_ids: list[str] = []
        for path_item in spec.paths.values():
            for method in ["get", "post", "put", "patch", "delete"]:
                operation = getattr(path_item, method, None)
                if operation is not None and operation.operationId:
                    operation_ids.append(operation.operationId)

        # Check for uniqueness
        self.assertEqual(
            len(operation_ids),
            len(set(operation_ids)),
            f"Duplicate operation IDs found: {operation_ids}",
        )


class TestOpenAPISchemaValidation(OpenAPITestMixin, DjangoTestCase):
    """Validate generated OpenAPI specs against the official OpenAPI 3.1 JSON schema."""

    OPENAPI_31_SCHEMA_URL = (
        "https://schemas.sourcemeta.com/openapi/v3.1/schema/2025-09-15.json"
    )
    _schema: ClassVar[dict[str, Any] | None] = None

    @classmethod
    def setUpClass(cls) -> None:
        """Fetch OpenAPI 3.1 JSON schema once for all tests."""
        super().setUpClass()
        with urllib.request.urlopen(cls.OPENAPI_31_SCHEMA_URL, timeout=30) as response:
            cls._schema = json.loads(response.read().decode())

    def _validate_spec(self, spec_data: dict[str, Any]) -> None:
        """Validate spec data against the OpenAPI 3.1 JSON schema."""
        assert self._schema is not None
        jsonschema.validate(spec_data, self._schema)

    def _generate_and_validate(self, test_router: Router, **kwargs: Any) -> None:
        """Generate OpenAPI spec from router and validate it."""
        spec = generate_openapi(
            test_router,
            title=kwargs.get("title", "Test API"),
            version=kwargs.get("version", "1.0.0"),
            description=kwargs.get("description"),
            servers=kwargs.get("servers"),
            namespace="sampleapp",
        )
        spec_data = json.loads(spec.model_dump_json(by_alias=True, exclude_none=True))
        self._validate_spec(spec_data)

    def test_sample_app_spec_validates(self) -> None:
        """Generated spec from sample app validates against OpenAPI 3.1 schema."""
        self._generate_and_validate(router)

    def test_minimal_spec_validates(self) -> None:
        """Minimal spec with empty router validates."""
        empty_router = Router(enable_index=False)
        self._generate_and_validate(empty_router)

    def test_spec_with_path_parameters_validates(self) -> None:
        """Spec with path parameters validates."""
        test_router = Router(enable_index=False)

        @test_router.route("users/<int:pk>/", name="user-detail").get
        @validate()
        def get_user(request: EmptyTypedRequest, pk: int) -> APIResponse[ResponseModel]:
            return APIResponse(ResponseModel(id=pk, name="test"))

        assert self._schema is not None
        self.validate_spec_for_test(test_router, self._schema)

    def test_spec_with_query_parameters_validates(self) -> None:
        """Spec with query parameters validates."""
        test_router = Router(enable_index=False)

        @test_router.route("search/", name="search").get
        @validate()
        def search(
            request: TypedRequestQuery[QueryModel],
        ) -> APIResponse[ListOf[ResponseModel]]:
            return APIResponse(ListOf[ResponseModel]([]))

        assert self._schema is not None
        self.validate_spec_for_test(test_router, self._schema)

    def test_spec_with_request_body_validates(self) -> None:
        """Spec with request body validates."""
        test_router = Router(enable_index=False)

        @test_router.route("users/", name="create-user").post
        @validate()
        def create_user(
            request: AuthdTypedRequestBody[BodyModel],
        ) -> APIResponse[ResponseModel]:
            return APIResponse(ResponseModel(id=1, name="test"))

        assert self._schema is not None
        self.validate_spec_for_test(test_router, self._schema)

    def test_spec_with_security_scheme_validates(self) -> None:
        """Spec with security scheme validates."""
        test_router = Router(enable_index=False)

        @test_router.route("protected/", name="protected").get
        @validate()
        def protected_view(
            request: AuthdTypedRequestBody[BodyModel],
        ) -> APIResponse[Empty]:
            return APIResponse(Empty())

        config = OpenAPIGeneratorConfig(
            title="Test API",
            version="1.0.0",
            auth_security_scheme="bearerAuth",
        )
        spec = self.generate_openapi_with_config_for_test(test_router, config)
        spec_data = json.loads(spec.model_dump_json(by_alias=True, exclude_none=True))
        self._validate_spec(spec_data)

    def test_spec_with_all_features_validates(self) -> None:
        """Spec with all features combined validates."""
        test_router = Router(enable_index=False)
        route = test_router.route("items/<int:item_id>/", name="item")

        @route.get
        @validate()
        def get_item(
            request: TypedRequestQuery[QueryModel], item_id: int
        ) -> APIResponse[ResponseModel]:
            return APIResponse(ResponseModel(id=item_id, name="test"))

        @route.put
        @validate()
        def update_item(
            request: AuthdTypedRequestBody[BodyModel], item_id: int
        ) -> APIResponse[ResponseModel]:
            return APIResponse(ResponseModel(id=item_id, name="updated"))

        @route.delete
        @validate()
        def delete_item(request: EmptyTypedRequest, item_id: int) -> APIResponse[Empty]:
            return APIResponse(Empty())

        config = OpenAPIGeneratorConfig(
            title="Full Feature API",
            version="2.0.0",
            description="API with all features",
            auth_security_scheme="bearerAuth",
            include_validation_errors=True,
        )
        spec = self.generate_openapi_with_config_for_test(test_router, config)
        spec_data = json.loads(spec.model_dump_json(by_alias=True, exclude_none=True))
        self._validate_spec(spec_data)


class TestOpenAPIPathResolutionWithNamespace(TestCase):
    """Tests that verify full path resolution with Django URL namespaces."""

    def test_generator_with_namespace_uses_full_paths(self) -> None:
        """Generator with namespace resolves full paths including base URL."""
        # This test verifies that when a namespace is provided,
        # the generator uses reverse() to get full paths
        config = OpenAPIGeneratorConfig(
            title="Test API",
            version="1.0.0",
        )
        # Use the sample app's namespace to test full path resolution
        generator = OpenAPIGenerator(config)
        spec = generator.generate(router, namespace="sampleapp")

        # Paths should include the full base path (/api/router/...)
        # when reverse() succeeds
        path_keys = list(spec.paths.keys())
        self.assertTrue(len(path_keys) > 0)

        # At least one path should have been resolved with the base path
        # The sample app router is included at /api/router/
        has_full_path = any(path.startswith("/api/router/") for path in path_keys)
        self.assertTrue(
            has_full_path,
            f"Expected paths to include base path /api/router/, got: {path_keys}",
        )

    def test_spec_paths_have_correct_parameter_syntax(self) -> None:
        """Paths in spec use OpenAPI parameter syntax {param}."""
        config = OpenAPIGeneratorConfig(
            title="Test API",
            version="1.0.0",
        )
        generator = OpenAPIGenerator(config)
        spec = generator.generate(router, namespace="sampleapp")

        # Find paths with parameters
        param_paths = [p for p in spec.paths.keys() if "{" in p]
        self.assertTrue(len(param_paths) > 0)

        # All parameter placeholders should use OpenAPI syntax
        for path in param_paths:
            # Should have {pk} format, not Django's <int:pk> format
            self.assertNotIn("<", path)
            self.assertNotIn(">", path)
            self.assertIn("{", path)
            self.assertIn("}", path)
