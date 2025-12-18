from collections.abc import Callable
from unittest.mock import Mock
import json

from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse, HttpResponseBase
from django.test import Client, TestCase, override_settings
from django.urls import include, path, reverse
from django.views.decorators.csrf import csrf_exempt

from thelabtyping.api.openapi import OpenAPISchema
from thelabtyping.api.openapi.models import Server
from thelabtyping.api.routing import HttpMethod, Route, Router, URLPatternStr
from thelabtyping.api.status import Status

from ..sampleapp.views import (
    route_users,
    router,
    router_users_list,
)


class RouterTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username="joe", password="password")
        self.client = Client()

    def test_reverse_router_urls(self) -> None:
        self.assertEqual(
            reverse("sampleapp:router-users-list"),
            "/api/router/users/",
        )
        self.assertEqual(
            reverse("sampleapp:router-users-detail", args=(42,)),
            "/api/router/users/42/",
        )
        self.assertEqual(
            reverse("sampleapp:alt-router-users-list"),
            "/api/alt-router/users/",
        )
        self.assertEqual(
            reverse("sampleapp:alt-router-users-detail", args=(42,)),
            "/api/alt-router/users/42/",
        )

    def test_router_index_main(self) -> None:
        url = reverse("sampleapp:index")
        self.assertEqual(url, "/api/router/")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, Status.HTTP_200_OK)
        self.assertJSONEqual(
            resp.content,
            {
                "sampleapp:index": "http://testserver/api/router/",
                "sampleapp:router-users-list": "http://testserver/api/router/users/",
            },
        )

    def test_router_index_unnamespaced(self) -> None:
        url = reverse("unnamespaced-router-index")
        self.assertEqual(url, "/unnamespaced-router/")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, Status.HTTP_200_OK)
        self.assertJSONEqual(
            resp.content,
            {
                "unnamespaced-router-index": "http://testserver/unnamespaced-router/",
                "unnamespaced-router-users-list": "http://testserver/unnamespaced-router/users/",
            },
        )

    def test_router_dispatch_get(self) -> None:
        resp = self.client.get(reverse("sampleapp:router-users-list"))
        self.assertEqual(resp.status_code, Status.HTTP_200_OK)
        self.assertJSONEqual(
            resp.content,
            [
                {
                    "username": "joe",
                    "first_name": "",
                    "last_name": "",
                }
            ],
        )

    def test_router_dispatch_post(self) -> None:
        self.client.login(username="joe", password="password")
        resp = self.client.post(
            reverse("sampleapp:router-users-list"),
            content_type="application/json",
            data={
                "username": "jack",
                "first_name": "Jack",
                "last_name": "Jackson",
            },
        )
        self.assertEqual(resp.status_code, Status.HTTP_200_OK)
        self.assertJSONEqual(
            resp.content,
            {
                "username": "jack",
                "first_name": "Jack",
                "last_name": "Jackson",
            },
        )

    def test_router_dispatch_method_not_allowed(self) -> None:
        self.client.login(username="joe", password="password")
        resp = self.client.put(reverse("sampleapp:router-users-list"))
        self.assertEqual(resp.status_code, Status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_register_duplicate_route(self) -> None:
        with self.assertRaises(ImproperlyConfigured):
            router.route("users/", name="router-users-list-duplicate")

    def test_register_duplicate_route_method(self) -> None:
        with self.assertRaises(ImproperlyConfigured):
            route_users.get(router_users_list)

    def test_register_get(self) -> None:
        router = Router()
        route = router.route("test/", name="test")
        self.assertEqual(route.allowed_methods, set())
        route.get(router_users_list)
        self.assertEqual(route.allowed_methods, {HttpMethod.GET})

    def test_register_post(self) -> None:
        router = Router()
        route = router.route("test/", name="test")
        self.assertEqual(route.allowed_methods, set())
        route.post(router_users_list)
        self.assertEqual(route.allowed_methods, {HttpMethod.POST})

    def test_register_put(self) -> None:
        router = Router()
        route = router.route("test/", name="test")
        self.assertEqual(route.allowed_methods, set())
        route.put(router_users_list)
        self.assertEqual(route.allowed_methods, {HttpMethod.PUT})

    def test_register_patch(self) -> None:
        router = Router()
        route = router.route("test/", name="test")
        self.assertEqual(route.allowed_methods, set())
        route.patch(router_users_list)
        self.assertEqual(route.allowed_methods, {HttpMethod.PATCH})

    def test_register_delete(self) -> None:
        router = Router()
        route = router.route("test/", name="test")
        self.assertEqual(route.allowed_methods, set())
        route.delete(router_users_list)
        self.assertEqual(route.allowed_methods, {HttpMethod.DELETE})

    def test_register_during_route_creation(self) -> None:
        router = Router()
        route = router.route(
            "test/",
            name="test",
            get=router_users_list,
            post=router_users_list,
        )
        self.assertEqual(
            route.allowed_methods,
            {
                HttpMethod.GET,
                HttpMethod.POST,
            },
        )


class TestRouteDecorators(TestCase):
    """Tests for Route and Router decorator support."""

    def _dummy_view(
        self, request: HttpRequest, *args: object, **kwargs: object
    ) -> HttpResponse:
        """A simple view function for testing."""
        return HttpResponse("OK")

    def test_route_without_decorators_returns_dispatch(self) -> None:
        """Routes without decorators should return dispatch unchanged."""
        router = Router(enable_index=False)
        route = router.route("test/", name="test", get=self._dummy_view)
        # Without decorators, view should be the same as dispatch
        self.assertEqual(route.view, route.dispatch)

    def test_route_with_csrf_exempt_decorator(self) -> None:
        """csrf_exempt decorator should set attribute on view."""
        router = Router(enable_index=False)
        route = router.route(
            "test/",
            name="test",
            get=self._dummy_view,
            decorators=[csrf_exempt],
        )
        # The view property should have csrf_exempt attribute
        self.assertTrue(hasattr(route.view, "csrf_exempt"))
        self.assertTrue(route.view.csrf_exempt)  # type: ignore[attr-defined]

    def test_multiple_decorators_applied_in_order(self) -> None:
        """Decorators are applied in list order (last is outermost)."""
        call_order: list[str] = []

        def decorator_a(
            fn: Callable[..., HttpResponseBase],
        ) -> Callable[..., HttpResponseBase]:
            def wrapper(
                request: HttpRequest, *args: object, **kwargs: object
            ) -> HttpResponseBase:
                call_order.append("a")
                return fn(request, *args, **kwargs)

            return wrapper

        def decorator_b(
            fn: Callable[..., HttpResponseBase],
        ) -> Callable[..., HttpResponseBase]:
            def wrapper(
                request: HttpRequest, *args: object, **kwargs: object
            ) -> HttpResponseBase:
                call_order.append("b")
                return fn(request, *args, **kwargs)

            return wrapper

        router = Router(enable_index=False)
        route = router.route(
            "test/",
            name="test",
            get=self._dummy_view,
            decorators=[decorator_a, decorator_b],
        )

        # Call the decorated view
        request = Mock(spec=HttpRequest)
        request.method = "GET"
        route.view(request)

        # decorator_b is outermost (applied last), called first
        self.assertEqual(call_order, ["b", "a"])

    def test_view_property_is_cached(self) -> None:
        """Multiple calls to .view return same instance."""
        router = Router(enable_index=False)
        route = router.route(
            "test/",
            name="test",
            get=self._dummy_view,
            decorators=[csrf_exempt],
        )
        view1 = route.view
        view2 = route.view
        self.assertIs(view1, view2)

    def test_router_urls_uses_decorated_view(self) -> None:
        """Router.urls should use route.view, not route.dispatch."""
        router = Router(enable_index=False)
        router.route(
            "test/",
            name="test",
            get=self._dummy_view,
            decorators=[csrf_exempt],
        )
        urls = router.urls
        self.assertEqual(len(urls), 1)
        url_pattern = urls[0]
        # The callback should be the decorated view with csrf_exempt
        self.assertTrue(hasattr(url_pattern.callback, "csrf_exempt"))
        self.assertTrue(url_pattern.callback.csrf_exempt)  # type: ignore[attr-defined]

    def test_router_level_decorators_apply_to_all_routes(self) -> None:
        """Router-level decorators should apply to all routes."""
        router = Router(enable_index=False, decorators=[csrf_exempt])
        route1 = router.route("test1/", name="test1", get=self._dummy_view)
        route2 = router.route("test2/", name="test2", get=self._dummy_view)

        # Both routes should have csrf_exempt applied
        self.assertTrue(hasattr(route1.view, "csrf_exempt"))
        self.assertTrue(route1.view.csrf_exempt)  # type: ignore[attr-defined]
        self.assertTrue(hasattr(route2.view, "csrf_exempt"))
        self.assertTrue(route2.view.csrf_exempt)  # type: ignore[attr-defined]

    def test_router_and_route_decorators_combined(self) -> None:
        """Router decorators apply first (inner), route decorators on top (outer)."""
        call_order: list[str] = []

        def router_decorator(
            fn: Callable[..., HttpResponseBase],
        ) -> Callable[..., HttpResponseBase]:
            def wrapper(
                request: HttpRequest, *args: object, **kwargs: object
            ) -> HttpResponseBase:
                call_order.append("router")
                return fn(request, *args, **kwargs)

            return wrapper

        def route_decorator(
            fn: Callable[..., HttpResponseBase],
        ) -> Callable[..., HttpResponseBase]:
            def wrapper(
                request: HttpRequest, *args: object, **kwargs: object
            ) -> HttpResponseBase:
                call_order.append("route")
                return fn(request, *args, **kwargs)

            return wrapper

        router = Router(enable_index=False, decorators=[router_decorator])
        route = router.route(
            "test/",
            name="test",
            get=self._dummy_view,
            decorators=[route_decorator],
        )

        # Call the decorated view
        request = Mock(spec=HttpRequest)
        request.method = "GET"
        route.view(request)

        # Route decorator is outermost, called first
        self.assertEqual(call_order, ["route", "router"])

    def test_route_created_outside_router_with_decorators(self) -> None:
        """Route can be created directly with decorators."""
        route = Route(name="test", decorators=[csrf_exempt])
        route.get(self._dummy_view)

        self.assertTrue(hasattr(route.view, "csrf_exempt"))
        self.assertTrue(route.view.csrf_exempt)  # type: ignore[attr-defined]


class TestAutoOpenAPI(TestCase):
    """Tests for auto-OpenAPI endpoint feature."""

    def test_openapi_disabled_by_default(self) -> None:
        """No openapi route when no config provided."""
        router = Router(enable_index=False)
        router.route("users/", name="users")

        # Should not have openapi.json route
        route_patterns = [str(pattern) for pattern in router.routes.keys()]
        self.assertNotIn("openapi.json", route_patterns)

    def test_openapi_endpoint_registered(self) -> None:
        """OpenAPI route is registered when schemas is provided."""
        router = Router(
            enable_index=False,
            schemas={
                "openapi.json": OpenAPISchema(
                    title="Test API",
                    version="1.0.0",
                ),
            },
        )
        router.route("users/", name="users")

        # Should have openapi.json route
        route_patterns = [str(pattern) for pattern in router.routes.keys()]
        self.assertIn("openapi.json", route_patterns)

    def test_openapi_custom_url_pattern(self) -> None:
        """Custom URL pattern for OpenAPI endpoint."""
        router = Router(
            enable_index=False,
            schemas={
                "docs/openapi.json": OpenAPISchema(
                    title="Test API",
                    version="1.0.0",
                ),
            },
        )

        # Should have custom route
        route_patterns = [str(pattern) for pattern in router.routes.keys()]
        self.assertIn("docs/openapi.json", route_patterns)
        self.assertNotIn("openapi.json", route_patterns)

    def test_openapi_serves_valid_spec(self) -> None:
        """OpenAPI endpoint returns valid OpenAPI JSON."""
        router = Router(
            basename="test",
            enable_index=False,
            schemas={
                "openapi.json": OpenAPISchema(
                    title="Test API",
                    version="2.0.0",
                    description="A test API",
                    cache_timeout=None,  # Disable caching for test with mock request
                    require_auth=False,  # Disable auth for unit test
                ),
            },
        )
        router.route("users/", name="users")

        # Get the openapi route
        openapi_route = router.routes.get(URLPatternStr("openapi.json"))
        self.assertIsNotNone(openapi_route)
        assert openapi_route is not None  # for mypy

        # Create a mock request with resolver_match for namespace
        request = Mock(spec=HttpRequest)
        request.method = "GET"
        request.build_absolute_uri = Mock(return_value="http://testserver/")
        request.resolver_match = Mock()
        request.resolver_match.namespace = "test"

        # Set up URL config for reverse() to work
        class TestURLConf:
            urlpatterns = [
                path("test/", include((router.urls, "test"))),
            ]

        # Call the view with URL config in place
        with override_settings(ROOT_URLCONF=TestURLConf):
            response = openapi_route.view(request)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        # Parse and validate the JSON
        assert hasattr(response, "content")  # APIResponse has content
        data = json.loads(response.content)
        self.assertEqual(data["openapi"], "3.1.0")
        self.assertEqual(data["info"]["title"], "Test API")
        self.assertEqual(data["info"]["version"], "2.0.0")
        self.assertEqual(data["info"]["description"], "A test API")
        self.assertIn("/test/users/", data["paths"])
        self.assertIn("/test/openapi.json", data["paths"])

    def test_openapi_requires_auth_by_default(self) -> None:
        """OpenAPI endpoint requires authentication by default."""
        router = Router(
            enable_index=False,
            schemas={
                "openapi.json": OpenAPISchema(
                    title="Test API",
                    version="1.0.0",
                    cache_timeout=None,  # Disable caching for test
                ),
            },
        )

        # Get the openapi route
        openapi_route = router.routes.get(URLPatternStr("openapi.json"))
        self.assertIsNotNone(openapi_route)
        assert openapi_route is not None

        # Create a mock request with anonymous user
        request = Mock(spec=HttpRequest)
        request.method = "GET"
        request.user = Mock()
        request.user.is_anonymous = True

        # Call the view - should return 403
        response = openapi_route.view(request)
        self.assertEqual(response.status_code, Status.HTTP_403_FORBIDDEN)

    def test_openapi_allows_authenticated_users(self) -> None:
        """OpenAPI endpoint allows authenticated users when auth is required."""
        router = Router(
            enable_index=False,
            schemas={
                "openapi.json": OpenAPISchema(
                    title="Test API",
                    version="1.0.0",
                    cache_timeout=None,  # Disable caching for test
                ),
            },
        )

        # Get the openapi route
        openapi_route = router.routes.get(URLPatternStr("openapi.json"))
        self.assertIsNotNone(openapi_route)
        assert openapi_route is not None

        # Create a mock request with authenticated user
        request = Mock(spec=HttpRequest)
        request.method = "GET"
        request.user = Mock()
        request.user.is_anonymous = False
        request.build_absolute_uri = Mock(return_value="http://testserver/")
        request.resolver_match = Mock()
        request.resolver_match.namespace = "test"

        # Set up URL config for reverse() to work
        class TestURLConf:
            urlpatterns = [
                path("test/", include((router.urls, "test"))),
            ]

        # Call the view - should return 200
        with override_settings(ROOT_URLCONF=TestURLConf):
            response = openapi_route.view(request)
        self.assertEqual(response.status_code, Status.HTTP_200_OK)

        # Verify it's valid JSON
        self.assertIsInstance(response, HttpResponse)
        assert isinstance(response, HttpResponse)
        data = json.loads(response.content)
        self.assertEqual(data["openapi"], "3.1.0")

    def test_openapi_public_when_auth_disabled(self) -> None:
        """OpenAPI endpoint is public when require_auth is False."""
        router = Router(
            enable_index=False,
            schemas={
                "openapi.json": OpenAPISchema(
                    title="Test API",
                    version="1.0.0",
                    cache_timeout=None,
                    require_auth=False,  # Allow public access
                ),
            },
        )

        # Get the openapi route
        openapi_route = router.routes.get(URLPatternStr("openapi.json"))
        self.assertIsNotNone(openapi_route)
        assert openapi_route is not None

        # Create a mock request with anonymous user
        request = Mock(spec=HttpRequest)
        request.method = "GET"
        request.user = Mock()
        request.user.is_anonymous = True
        request.build_absolute_uri = Mock(return_value="http://testserver/")
        request.resolver_match = Mock()
        request.resolver_match.namespace = "test"

        # Set up URL config for reverse() to work
        class TestURLConf:
            urlpatterns = [
                path("test/", include((router.urls, "test"))),
            ]

        # Call the view - should return 200 even for anonymous user
        with override_settings(ROOT_URLCONF=TestURLConf):
            response = openapi_route.view(request)
        self.assertEqual(response.status_code, Status.HTTP_200_OK)

        # Verify it's valid JSON
        self.assertIsInstance(response, HttpResponse)
        assert isinstance(response, HttpResponse)
        data = json.loads(response.content)
        self.assertEqual(data["openapi"], "3.1.0")

    def test_openapi_caching_enabled_by_default(self) -> None:
        """OpenAPI schema generator has caching enabled by default (3600 seconds)."""
        schema = OpenAPISchema(
            title="Test API",
            version="1.0.0",
        )

        # Default cache_timeout is 3600
        self.assertEqual(schema.cache_timeout, 3600)

    def test_openapi_caching_disabled_when_none(self) -> None:
        """OpenAPI schema generator can have caching disabled."""
        schema = OpenAPISchema(
            title="Test API",
            version="1.0.0",
            cache_timeout=None,
        )

        # cache_timeout is None when disabled
        self.assertIsNone(schema.cache_timeout)

    def test_openapi_custom_cache_timeout(self) -> None:
        """OpenAPI schema generator respects custom cache_timeout value."""
        schema = OpenAPISchema(
            title="Test API",
            version="1.0.0",
            cache_timeout=7200,  # 2 hours
        )

        # Custom cache_timeout is preserved
        self.assertEqual(schema.cache_timeout, 7200)

    def test_openapi_auto_populates_servers_from_request(self) -> None:
        """OpenAPI spec auto-populates servers from request when not provided."""
        router = Router(
            enable_index=False,
            schemas={
                "openapi.json": OpenAPISchema(
                    title="Test API",
                    version="1.0.0",
                    cache_timeout=None,
                    require_auth=False,
                    # No servers provided - should auto-populate
                ),
            },
        )

        openapi_route = router.routes.get(URLPatternStr("openapi.json"))
        assert openapi_route is not None

        request = Mock(spec=HttpRequest)
        request.method = "GET"
        request.build_absolute_uri = Mock(return_value="https://api.example.com/")
        request.resolver_match = Mock()
        request.resolver_match.namespace = "test"

        # Set up URL config for reverse() to work
        class TestURLConf:
            urlpatterns = [
                path("test/", include((router.urls, "test"))),
            ]

        with override_settings(ROOT_URLCONF=TestURLConf):
            response = openapi_route.view(request)
        self.assertEqual(response.status_code, Status.HTTP_200_OK)

        self.assertIsInstance(response, HttpResponse)
        assert isinstance(response, HttpResponse)
        data = json.loads(response.content)

        # Server should be auto-populated from request
        self.assertIn("servers", data)
        self.assertEqual(len(data["servers"]), 1)
        self.assertEqual(data["servers"][0]["url"], "https://api.example.com")

    def test_openapi_uses_explicit_servers_when_provided(self) -> None:
        """OpenAPI spec uses explicit servers when provided."""
        router = Router(
            enable_index=False,
            schemas={
                "openapi.json": OpenAPISchema(
                    title="Test API",
                    version="1.0.0",
                    cache_timeout=None,
                    require_auth=False,
                    servers=[
                        Server(url="https://prod.example.com"),
                        Server(url="https://staging.example.com"),
                    ],
                ),
            },
        )

        openapi_route = router.routes.get(URLPatternStr("openapi.json"))
        assert openapi_route is not None

        request = Mock(spec=HttpRequest)
        request.method = "GET"
        # This should be ignored when servers are explicitly provided
        request.build_absolute_uri = Mock(return_value="https://ignored.example.com/")
        request.resolver_match = Mock()
        request.resolver_match.namespace = "test"

        # Set up URL config for reverse() to work
        class TestURLConf:
            urlpatterns = [
                path("test/", include((router.urls, "test"))),
            ]

        with override_settings(ROOT_URLCONF=TestURLConf):
            response = openapi_route.view(request)
        self.assertEqual(response.status_code, Status.HTTP_200_OK)

        self.assertIsInstance(response, HttpResponse)
        assert isinstance(response, HttpResponse)
        data = json.loads(response.content)

        # Explicit servers should be used, not auto-populated
        self.assertIn("servers", data)
        self.assertEqual(len(data["servers"]), 2)
        self.assertEqual(data["servers"][0]["url"], "https://prod.example.com")
        self.assertEqual(data["servers"][1]["url"], "https://staging.example.com")
