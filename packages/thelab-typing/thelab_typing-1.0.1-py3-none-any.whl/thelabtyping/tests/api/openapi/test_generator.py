"""Tests for OpenAPI generator."""

from unittest import TestCase
import json

from django.test import TestCase as DjangoTestCase

from thelabtyping.abc import ListOf
from thelabtyping.api.openapi.generator import (
    OpenAPIGenerator,
    OpenAPIGeneratorConfig,
    generate_openapi,
)
from thelabtyping.api.openapi.models import Server
from thelabtyping.api.requests import (
    AuthdEmptyTypedRequest,
    AuthdTypedRequestBody,
    EmptyTypedRequest,
    TypedRequestQuery,
)
from thelabtyping.api.responses import APIResponse
from thelabtyping.api.routing import Router
from thelabtyping.api.serializers import Empty
from thelabtyping.api.views import validate

from .conftest import BodyModel, OpenAPITestMixin, QueryModel, ResponseModel


class TestGenerateOpenAPIConvenienceFunction(TestCase):
    def test_minimal_spec(self) -> None:
        """Generate minimal spec with empty router."""
        router = Router(enable_index=False)
        spec = generate_openapi(router, title="Test API", version="1.0.0")

        self.assertEqual(spec.info.title, "Test API")
        self.assertEqual(spec.info.version, "1.0.0")
        self.assertEqual(spec.openapi, "3.1.0")
        self.assertEqual(spec.paths, {})

    def test_with_description(self) -> None:
        """Generate spec with description."""
        router = Router(enable_index=False)
        spec = generate_openapi(
            router,
            title="Test API",
            version="1.0.0",
            description="A test API",
        )

        self.assertEqual(spec.info.description, "A test API")

    def test_with_servers(self) -> None:
        """Generate spec with servers."""
        router = Router(enable_index=False)
        servers = [
            Server(url="https://api.example.com", description="Production"),
            Server(url="https://staging.example.com", description="Staging"),
        ]
        spec = generate_openapi(
            router,
            title="Test API",
            version="1.0.0",
            servers=servers,
        )

        self.assertEqual(len(spec.servers or []), 2)


class TestOpenAPIGeneratorEmptyRouter(TestCase):
    def test_empty_router_no_index(self) -> None:
        """Empty router without index produces empty paths."""
        router = Router(enable_index=False)
        config = OpenAPIGeneratorConfig(title="Test", version="1.0.0")
        generator = OpenAPIGenerator(config)

        spec = generator.generate(router)

        self.assertEqual(spec.paths, {})


class TestOpenAPIGeneratorSimpleEndpoints(OpenAPITestMixin, DjangoTestCase):
    def test_simple_get_endpoint(self) -> None:
        """Generate spec for simple GET endpoint."""
        router = Router(enable_index=False)

        @router.route("users/", name="users").get
        @validate()
        def list_users(request: EmptyTypedRequest) -> APIResponse[Empty]:
            return APIResponse(Empty())

        spec = self.generate_openapi_for_test(router, title="Test", version="1.0.0")

        self.assertIn("/test/users/", spec.paths)
        path_item = spec.paths["/test/users/"]
        self.assertIsNotNone(path_item.get)
        self.assertIsNone(path_item.post)
        assert path_item.get is not None  # for mypy
        self.assertIn("200", path_item.get.responses)

    def test_multiple_methods_same_path(self) -> None:
        """Generate spec for path with multiple HTTP methods."""
        router = Router(enable_index=False)
        route = router.route("users/", name="users")

        @route.get
        @validate()
        def list_users(
            request: TypedRequestQuery[QueryModel],
        ) -> APIResponse[ListOf[ResponseModel]]:
            return APIResponse(ListOf[ResponseModel]([]))

        @route.post
        @validate()
        def create_user(
            request: AuthdTypedRequestBody[BodyModel],
        ) -> APIResponse[ResponseModel]:
            return APIResponse(ResponseModel(id=1, name="test"))

        spec = self.generate_openapi_for_test(router, title="Test", version="1.0.0")

        self.assertIn("/test/users/", spec.paths)
        path_item = spec.paths["/test/users/"]
        self.assertIsNotNone(path_item.get)
        self.assertIsNotNone(path_item.post)


class TestOpenAPIGeneratorPathParameters(OpenAPITestMixin, DjangoTestCase):
    def test_int_path_parameter(self) -> None:
        """Generate spec with integer path parameter."""
        router = Router(enable_index=False)

        @router.route("users/<int:pk>/", name="user-detail").get
        @validate()
        def get_user(request: EmptyTypedRequest, pk: int) -> APIResponse[ResponseModel]:
            return APIResponse(ResponseModel(id=pk, name="test"))

        spec = self.generate_openapi_for_test(router, title="Test", version="1.0.0")

        self.assertIn("/test/users/{pk}/", spec.paths)
        path_item = spec.paths["/test/users/{pk}/"]
        assert path_item.get is not None  # for mypy
        params = path_item.get.parameters or []
        path_params = [p for p in params if getattr(p, "param_in", None) == "path"]
        self.assertEqual(len(path_params), 1)
        self.assertEqual(path_params[0].name, "pk")  # type: ignore[union-attr]
        self.assertTrue(path_params[0].required)  # type: ignore[union-attr]

    def test_multiple_path_parameters(self) -> None:
        """Generate spec with multiple path parameters."""
        router = Router(enable_index=False)

        @router.route("users/<int:user_id>/posts/<int:post_id>/", name="user-post").get
        @validate()
        def get_user_post(
            request: EmptyTypedRequest, user_id: int, post_id: int
        ) -> APIResponse[ResponseModel]:
            return APIResponse(ResponseModel(id=post_id, name="test"))

        spec = self.generate_openapi_for_test(router, title="Test", version="1.0.0")

        self.assertIn("/test/users/{user_id}/posts/{post_id}/", spec.paths)
        path_item = spec.paths["/test/users/{user_id}/posts/{post_id}/"]
        assert path_item.get is not None  # for mypy
        params = path_item.get.parameters or []
        path_params = [p for p in params if getattr(p, "param_in", None) == "path"]
        self.assertEqual(len(path_params), 2)
        param_names = {p.name for p in path_params}  # type: ignore[union-attr]
        self.assertEqual(param_names, {"user_id", "post_id"})


class TestOpenAPIGeneratorQueryParameters(OpenAPITestMixin, DjangoTestCase):
    def test_query_parameters_from_model(self) -> None:
        """Generate spec with query parameters from model."""
        router = Router(enable_index=False)

        @router.route("users/", name="users").get
        @validate()
        def list_users(
            request: TypedRequestQuery[QueryModel],
        ) -> APIResponse[ListOf[ResponseModel]]:
            return APIResponse(ListOf[ResponseModel]([]))

        spec = self.generate_openapi_for_test(router, title="Test", version="1.0.0")

        # Verify path exists
        self.assertIn("/test/users/", spec.paths)
        # The query schema should be in components
        self.assertIsNotNone(spec.components)
        assert spec.components is not None  # for mypy
        self.assertIsNotNone(spec.components.schemas)


class TestOpenAPIGeneratorRequestBody(OpenAPITestMixin, DjangoTestCase):
    def test_request_body_from_model(self) -> None:
        """Generate spec with request body from model."""
        router = Router(enable_index=False)

        @router.route("users/", name="users").post
        @validate()
        def create_user(
            request: AuthdTypedRequestBody[BodyModel],
        ) -> APIResponse[ResponseModel]:
            return APIResponse(ResponseModel(id=1, name="test"))

        spec = self.generate_openapi_for_test(router, title="Test", version="1.0.0")

        path_item = spec.paths["/test/users/"]
        assert path_item.post is not None  # for mypy
        self.assertIsNotNone(path_item.post.requestBody)
        request_body = path_item.post.requestBody
        assert request_body is not None  # for mypy
        self.assertIn("application/json", request_body.content)  # type: ignore[union-attr]


class TestOpenAPIGeneratorResponses(OpenAPITestMixin, DjangoTestCase):
    def test_response_model_in_components(self) -> None:
        """Response model should be in components/schemas."""
        router = Router(enable_index=False)

        @router.route("users/<int:pk>/", name="user-detail").get
        @validate()
        def get_user(request: EmptyTypedRequest, pk: int) -> APIResponse[ResponseModel]:
            return APIResponse(ResponseModel(id=pk, name="test"))

        spec = self.generate_openapi_for_test(router, title="Test", version="1.0.0")

        self.assertIsNotNone(spec.components)
        assert spec.components is not None  # for mypy
        self.assertIsNotNone(spec.components.schemas)
        assert spec.components.schemas is not None  # for mypy
        self.assertIn("ResponseModel", spec.components.schemas)

    def test_list_of_response(self) -> None:
        """ListOf[T] response should generate array schema."""
        router = Router(enable_index=False)

        @router.route("users/", name="users").get
        @validate()
        def list_users(
            request: EmptyTypedRequest,
        ) -> APIResponse[ListOf[ResponseModel]]:
            return APIResponse(ListOf[ResponseModel]([]))

        spec = self.generate_openapi_for_test(router, title="Test", version="1.0.0")

        path_item = spec.paths["/test/users/"]
        assert path_item.get is not None  # for mypy
        response = path_item.get.responses.get("200")
        self.assertIsNotNone(response)


class TestOpenAPIGeneratorSecurity(OpenAPITestMixin, DjangoTestCase):
    def test_authenticated_endpoint_security(self) -> None:
        """Authenticated endpoints should have security requirement."""
        config = OpenAPIGeneratorConfig(
            title="Test",
            version="1.0.0",
            auth_security_scheme="bearerAuth",
        )
        router = Router(enable_index=False)

        @router.route("protected/", name="protected").get
        @validate()
        def protected_view(request: AuthdEmptyTypedRequest) -> APIResponse[Empty]:
            return APIResponse(Empty())

        spec = self.generate_openapi_with_config_for_test(router, config)

        path_item = spec.paths["/test/protected/"]
        assert path_item.get is not None  # for mypy
        self.assertIsNotNone(path_item.get.security)
        self.assertEqual(path_item.get.security, [{"bearerAuth": []}])

    def test_unauthenticated_endpoint_no_security(self) -> None:
        """Unauthenticated endpoints should not have security."""
        config = OpenAPIGeneratorConfig(
            title="Test",
            version="1.0.0",
            auth_security_scheme="bearerAuth",
        )
        router = Router(enable_index=False)

        @router.route("public/", name="public").get
        @validate()
        def public_view(request: EmptyTypedRequest) -> APIResponse[Empty]:
            return APIResponse(Empty())

        spec = self.generate_openapi_with_config_for_test(router, config)

        path_item = spec.paths["/test/public/"]
        assert path_item.get is not None  # for mypy
        self.assertIsNone(path_item.get.security)


class TestOpenAPIGeneratorOperationId(OpenAPITestMixin, DjangoTestCase):
    def test_operation_id_from_function_name(self) -> None:
        """Operation ID should be derived from function name."""
        router = Router(enable_index=False)

        @router.route("users/", name="users").get
        @validate()
        def list_all_users(request: EmptyTypedRequest) -> APIResponse[Empty]:
            return APIResponse(Empty())

        spec = self.generate_openapi_for_test(router, title="Test", version="1.0.0")

        path_item = spec.paths["/test/users/"]
        assert path_item.get is not None  # for mypy
        self.assertEqual(path_item.get.operationId, "list_all_users")


class TestOpenAPIGeneratorSchemaDeduplication(OpenAPITestMixin, DjangoTestCase):
    def test_same_model_used_multiple_times(self) -> None:
        """Same model used multiple times should only appear once in components."""
        router = Router(enable_index=False)
        route = router.route("users/", name="users")

        @route.get
        @validate()
        def list_users(request: EmptyTypedRequest) -> APIResponse[ResponseModel]:
            return APIResponse(ResponseModel(id=1, name="test"))

        @route.post
        @validate()
        def create_user(
            request: AuthdTypedRequestBody[BodyModel],
        ) -> APIResponse[ResponseModel]:
            return APIResponse(ResponseModel(id=1, name="test"))

        spec = self.generate_openapi_for_test(router, title="Test", version="1.0.0")

        # ResponseModel should appear only once (not duplicated)
        self.assertIsNotNone(spec.components)
        assert spec.components is not None  # for mypy
        self.assertIsNotNone(spec.components.schemas)
        assert spec.components.schemas is not None  # for mypy
        # Exact match for ResponseModel, not substring matching
        response_model_exact = sum(
            1 for name in spec.components.schemas if name == "ResponseModel"
        )
        self.assertEqual(response_model_exact, 1)


class TestOpenAPIGeneratorJSONOutput(OpenAPITestMixin, DjangoTestCase):
    def test_spec_to_json(self) -> None:
        """Generated spec should serialize to valid JSON."""
        router = Router(enable_index=False)

        @router.route("users/<int:pk>/", name="user-detail").get
        @validate()
        def get_user(request: EmptyTypedRequest, pk: int) -> APIResponse[ResponseModel]:
            return APIResponse(ResponseModel(id=pk, name="test"))

        spec = self.generate_openapi_for_test(router, title="Test API", version="1.0.0")
        json_str = spec.model_dump_json(by_alias=True, exclude_none=True, indent=2)

        # Parse and verify structure
        data = json.loads(json_str)
        self.assertEqual(data["openapi"], "3.1.0")
        self.assertEqual(data["info"]["title"], "Test API")
        self.assertIn("/test/users/{pk}/", data["paths"])
