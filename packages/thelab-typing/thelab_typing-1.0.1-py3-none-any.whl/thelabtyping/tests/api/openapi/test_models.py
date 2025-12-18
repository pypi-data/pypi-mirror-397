"""Tests for OpenAPI Pydantic models."""

from unittest import TestCase
import json

from thelabtyping.api.openapi.models import (
    Components,
    Contact,
    ExternalDocumentation,
    Info,
    License,
    MediaType,
    OpenAPI,
    Operation,
    Parameter,
    PathItem,
    Reference,
    RequestBody,
    Response,
    SecurityScheme,
    Server,
    Tag,
)


class TestInfo(TestCase):
    def test_minimal_info(self) -> None:
        """Info with only required fields serializes correctly."""
        info = Info(title="Test API", version="1.0.0")
        data = info.model_dump(by_alias=True, exclude_none=True)

        self.assertEqual(data["title"], "Test API")
        self.assertEqual(data["version"], "1.0.0")
        self.assertNotIn("description", data)
        self.assertNotIn("contact", data)

    def test_full_info(self) -> None:
        """Info with all fields serializes correctly."""
        info = Info(
            title="Test API",
            version="1.0.0",
            summary="A test API",
            description="This is a test API for testing purposes.",
            termsOfService="https://example.com/terms",  # type: ignore[arg-type]
            contact=Contact(
                name="API Support",
                url="https://example.com/support",  # type: ignore[arg-type]
                email="support@example.com",
            ),
            license=License(
                name="MIT",
                identifier="MIT",
                url="https://opensource.org/licenses/MIT",  # type: ignore[arg-type]
            ),
        )
        data = info.model_dump(by_alias=True, exclude_none=True)

        self.assertEqual(data["title"], "Test API")
        self.assertEqual(data["summary"], "A test API")
        self.assertEqual(data["contact"]["name"], "API Support")
        self.assertEqual(data["license"]["name"], "MIT")


class TestReference(TestCase):
    def test_reference_alias(self) -> None:
        """Reference uses $ref alias correctly."""
        ref = Reference(ref="#/components/schemas/User")
        data = ref.model_dump(by_alias=True, exclude_none=True)

        self.assertEqual(data["$ref"], "#/components/schemas/User")
        self.assertNotIn("ref", data)


class TestParameter(TestCase):
    def test_query_parameter(self) -> None:
        """Query parameter serializes correctly."""
        param = Parameter(
            name="limit",
            param_in="query",
            description="Maximum number of items to return",
            required=False,
            param_schema={"type": "integer", "minimum": 1, "maximum": 100},
        )
        data = param.model_dump(by_alias=True, exclude_none=True)

        self.assertEqual(data["name"], "limit")
        self.assertEqual(data["in"], "query")
        self.assertEqual(data["schema"]["type"], "integer")
        self.assertNotIn("param_in", data)

    def test_path_parameter(self) -> None:
        """Path parameter serializes correctly."""
        param = Parameter(
            name="pk",
            param_in="path",
            required=True,
            param_schema={"type": "integer"},
        )
        data = param.model_dump(by_alias=True, exclude_none=True)

        self.assertEqual(data["name"], "pk")
        self.assertEqual(data["in"], "path")
        self.assertTrue(data["required"])


class TestRequestBody(TestCase):
    def test_json_request_body(self) -> None:
        """Request body with JSON content serializes correctly."""
        body = RequestBody(
            description="User to create",
            content={
                "application/json": MediaType(
                    media_type_schema=Reference(
                        ref="#/components/schemas/User",
                    ),
                ),
            },
            required=True,
        )
        data = body.model_dump(by_alias=True, exclude_none=True)

        self.assertEqual(data["description"], "User to create")
        self.assertTrue(data["required"])
        self.assertIn("application/json", data["content"])
        self.assertEqual(
            data["content"]["application/json"]["schema"]["$ref"],
            "#/components/schemas/User",
        )


class TestResponse(TestCase):
    def test_response_with_content(self) -> None:
        """Response with content serializes correctly."""
        response = Response(
            description="Successful response",
            content={
                "application/json": MediaType(
                    media_type_schema=Reference(
                        ref="#/components/schemas/User",
                    ),
                ),
            },
        )
        data = response.model_dump(by_alias=True, exclude_none=True)

        self.assertEqual(data["description"], "Successful response")
        self.assertIn("application/json", data["content"])

    def test_response_without_content(self) -> None:
        """Response without content (e.g., 204) serializes correctly."""
        response = Response(description="No content")
        data = response.model_dump(by_alias=True, exclude_none=True)

        self.assertEqual(data["description"], "No content")
        self.assertNotIn("content", data)


class TestOperation(TestCase):
    def test_minimal_operation(self) -> None:
        """Operation with only required fields serializes correctly."""
        operation = Operation(
            responses={"200": Response(description="Success")},
        )
        data = operation.model_dump(by_alias=True, exclude_none=True)

        self.assertIn("200", data["responses"])
        self.assertEqual(data["responses"]["200"]["description"], "Success")

    def test_full_operation(self) -> None:
        """Operation with all common fields serializes correctly."""
        operation = Operation(
            tags=["users"],
            summary="List users",
            description="Returns a list of users",
            operationId="listUsers",
            parameters=[
                Parameter(
                    name="limit",
                    param_in="query",
                    param_schema={"type": "integer"},
                ),
            ],
            responses={
                "200": Response(
                    description="Success",
                    content={
                        "application/json": MediaType(
                            media_type_schema=Reference(
                                ref="#/components/schemas/UserList",
                            ),
                        ),
                    },
                ),
                "400": Response(description="Bad request"),
            },
            security=[{"bearerAuth": []}],
        )
        data = operation.model_dump(by_alias=True, exclude_none=True)

        self.assertEqual(data["tags"], ["users"])
        self.assertEqual(data["summary"], "List users")
        self.assertEqual(data["operationId"], "listUsers")
        self.assertEqual(len(data["parameters"]), 1)
        self.assertIn("200", data["responses"])
        self.assertEqual(data["security"], [{"bearerAuth": []}])


class TestPathItem(TestCase):
    def test_path_item_with_operations(self) -> None:
        """PathItem with multiple operations serializes correctly."""
        path_item = PathItem(
            summary="User operations",
            get=Operation(
                summary="List users",
                responses={"200": Response(description="Success")},
            ),
            post=Operation(
                summary="Create user",
                requestBody=RequestBody(
                    content={
                        "application/json": MediaType(
                            media_type_schema=Reference(
                                ref="#/components/schemas/User",
                            ),
                        ),
                    },
                ),
                responses={"201": Response(description="Created")},
            ),
        )
        data = path_item.model_dump(by_alias=True, exclude_none=True)

        self.assertEqual(data["summary"], "User operations")
        self.assertIn("get", data)
        self.assertIn("post", data)
        self.assertEqual(data["get"]["summary"], "List users")
        self.assertEqual(data["post"]["summary"], "Create user")


class TestComponents(TestCase):
    def test_components_with_schemas(self) -> None:
        """Components with schemas serializes correctly."""
        components = Components(
            schemas={
                "User": {
                    "type": "object",
                    "properties": {
                        "username": {"type": "string"},
                        "email": {"type": "string", "format": "email"},
                    },
                    "required": ["username", "email"],
                },
            },
        )
        data = components.model_dump(by_alias=True, exclude_none=True)

        self.assertIn("User", data["schemas"])
        self.assertEqual(data["schemas"]["User"]["type"], "object")

    def test_components_with_security_schemes(self) -> None:
        """Components with security schemes serializes correctly."""
        components = Components(
            securitySchemes={
                "bearerAuth": SecurityScheme(
                    type="http",
                    scheme="bearer",
                    bearerFormat="JWT",
                ),
            },
        )
        data = components.model_dump(by_alias=True, exclude_none=True)

        self.assertIn("bearerAuth", data["securitySchemes"])
        self.assertEqual(data["securitySchemes"]["bearerAuth"]["type"], "http")
        self.assertEqual(data["securitySchemes"]["bearerAuth"]["scheme"], "bearer")


class TestOpenAPI(TestCase):
    def test_minimal_openapi(self) -> None:
        """OpenAPI document with minimal fields serializes correctly."""
        spec = OpenAPI(
            info=Info(title="Test API", version="1.0.0"),
            paths={},
        )
        data = spec.model_dump(by_alias=True, exclude_none=True)

        self.assertEqual(data["openapi"], "3.1.0")
        self.assertEqual(data["info"]["title"], "Test API")
        self.assertEqual(data["paths"], {})

    def test_full_openapi(self) -> None:
        """OpenAPI document with all major sections serializes correctly."""
        spec = OpenAPI(
            info=Info(
                title="Test API",
                version="1.0.0",
                description="A test API",
            ),
            servers=[
                Server(url="https://api.example.com", description="Production"),
                Server(url="https://staging.example.com", description="Staging"),
            ],
            paths={
                "/users": PathItem(
                    get=Operation(
                        summary="List users",
                        responses={"200": Response(description="Success")},
                    ),
                ),
            },
            components=Components(
                schemas={
                    "User": {"type": "object"},
                },
            ),
            tags=[
                Tag(name="users", description="User operations"),
            ],
        )
        data = spec.model_dump(by_alias=True, exclude_none=True)

        self.assertEqual(data["openapi"], "3.1.0")
        self.assertEqual(len(data["servers"]), 2)
        self.assertIn("/users", data["paths"])
        self.assertIn("User", data["components"]["schemas"])
        self.assertEqual(data["tags"][0]["name"], "users")

    def test_openapi_to_json(self) -> None:
        """OpenAPI document serializes to valid JSON."""
        spec = OpenAPI(
            info=Info(title="Test API", version="1.0.0"),
            paths={
                "/users/{pk}": PathItem(
                    parameters=[
                        Parameter(
                            name="pk",
                            param_in="path",
                            required=True,
                            param_schema={"type": "integer"},
                        ),
                    ],
                    get=Operation(
                        operationId="getUser",
                        responses={"200": Response(description="Success")},
                    ),
                ),
            },
        )
        json_str = spec.model_dump_json(by_alias=True, exclude_none=True, indent=2)

        # Verify it's valid JSON
        parsed = json.loads(json_str)
        self.assertEqual(parsed["openapi"], "3.1.0")
        self.assertIn("/users/{pk}", parsed["paths"])


class TestServer(TestCase):
    def test_server_serialization(self) -> None:
        """Server serializes correctly."""
        server = Server(
            url="https://api.example.com/v1",
            description="Production server",
        )
        data = server.model_dump(by_alias=True, exclude_none=True)

        self.assertEqual(data["url"], "https://api.example.com/v1")
        self.assertEqual(data["description"], "Production server")


class TestTag(TestCase):
    def test_tag_with_docs(self) -> None:
        """Tag with external docs serializes correctly."""
        tag = Tag(
            name="users",
            description="User management",
            externalDocs=ExternalDocumentation(
                url="https://docs.example.com/users",  # type: ignore[arg-type]
                description="User documentation",
            ),
        )
        data = tag.model_dump(by_alias=True, exclude_none=True)

        self.assertEqual(data["name"], "users")
        self.assertEqual(
            str(data["externalDocs"]["url"]), "https://docs.example.com/users"
        )


class TestSecurityScheme(TestCase):
    def test_bearer_auth(self) -> None:
        """Bearer authentication scheme serializes correctly."""
        scheme = SecurityScheme(
            type="http",
            scheme="bearer",
            bearerFormat="JWT",
        )
        data = scheme.model_dump(by_alias=True, exclude_none=True)

        self.assertEqual(data["type"], "http")
        self.assertEqual(data["scheme"], "bearer")
        self.assertEqual(data["bearerFormat"], "JWT")

    def test_api_key(self) -> None:
        """API key authentication scheme serializes correctly."""
        scheme = SecurityScheme(
            type="apiKey",
            name="X-API-Key",
            security_scheme_in="header",
        )
        data = scheme.model_dump(by_alias=True, exclude_none=True)

        self.assertEqual(data["type"], "apiKey")
        self.assertEqual(data["name"], "X-API-Key")
        self.assertEqual(data["in"], "header")
        self.assertNotIn("security_scheme_in", data)
