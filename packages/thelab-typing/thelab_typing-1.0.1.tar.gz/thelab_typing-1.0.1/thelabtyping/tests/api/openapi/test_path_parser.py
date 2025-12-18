"""Tests for Django URL to OpenAPI path parser."""

from unittest import TestCase

from thelabtyping.api.openapi.path_parser import (
    get_placeholder_kwargs,
    parse_django_path_params,
    replace_placeholders_with_openapi_params,
)


class TestParseSimplePaths(TestCase):
    def test_empty_path(self) -> None:
        """Empty path becomes /."""
        params = parse_django_path_params("")
        self.assertEqual(params, [])

    def test_simple_path(self) -> None:
        """Simple path without parameters."""
        params = parse_django_path_params("users/")
        self.assertEqual(params, [])

    def test_nested_path(self) -> None:
        """Nested path without parameters."""
        params = parse_django_path_params("api/v1/users/")
        self.assertEqual(params, [])


class TestParsePathParameters(TestCase):
    def test_int_path_param(self) -> None:
        """Integer path parameter."""
        params = parse_django_path_params("users/<int:pk>/")
        self.assertEqual(len(params), 1)
        self.assertEqual(params[0].name, "pk")
        self.assertEqual(params[0].django_type, "int")
        self.assertEqual(params[0].openapi_type, "integer")
        self.assertIsNone(params[0].openapi_format)

    def test_str_path_param(self) -> None:
        """String path parameter."""
        params = parse_django_path_params("users/<str:username>/")
        self.assertEqual(len(params), 1)
        self.assertEqual(params[0].name, "username")
        self.assertEqual(params[0].django_type, "str")
        self.assertEqual(params[0].openapi_type, "string")

    def test_slug_path_param(self) -> None:
        """Slug path parameter."""
        params = parse_django_path_params("articles/<slug:article_slug>/")
        self.assertEqual(len(params), 1)
        self.assertEqual(params[0].name, "article_slug")
        self.assertEqual(params[0].django_type, "slug")
        self.assertEqual(params[0].openapi_type, "string")

    def test_uuid_path_param(self) -> None:
        """UUID path parameter."""
        params = parse_django_path_params("items/<uuid:item_id>/")
        self.assertEqual(len(params), 1)
        self.assertEqual(params[0].name, "item_id")
        self.assertEqual(params[0].django_type, "uuid")
        self.assertEqual(params[0].openapi_type, "string")
        self.assertEqual(params[0].openapi_format, "uuid")

    def test_path_path_param(self) -> None:
        """Path path parameter (for capturing slashes)."""
        params = parse_django_path_params("files/<path:file_path>/")
        self.assertEqual(len(params), 1)
        self.assertEqual(params[0].name, "file_path")
        self.assertEqual(params[0].django_type, "path")
        self.assertEqual(params[0].openapi_type, "string")

    def test_untyped_path_param(self) -> None:
        """Untyped path parameter defaults to string."""
        params = parse_django_path_params("users/<username>/")
        self.assertEqual(len(params), 1)
        self.assertEqual(params[0].name, "username")
        self.assertEqual(params[0].django_type, "str")
        self.assertEqual(params[0].openapi_type, "string")


class TestMultipleParameters(TestCase):
    def test_multiple_params(self) -> None:
        """Multiple path parameters."""
        params = parse_django_path_params("users/<int:user_id>/posts/<int:post_id>/")
        self.assertEqual(len(params), 2)
        self.assertEqual(params[0].name, "user_id")
        self.assertEqual(params[1].name, "post_id")

    def test_mixed_param_types(self) -> None:
        """Multiple path parameters with different types."""
        params = parse_django_path_params("orgs/<slug:org_slug>/users/<int:pk>/")
        self.assertEqual(len(params), 2)
        self.assertEqual(params[0].name, "org_slug")
        self.assertEqual(params[0].django_type, "slug")
        self.assertEqual(params[1].name, "pk")
        self.assertEqual(params[1].django_type, "int")


class TestEdgeCases(TestCase):
    def test_no_trailing_slash(self) -> None:
        """Path without trailing slash."""
        params = parse_django_path_params("users/<int:pk>")
        self.assertEqual(len(params), 1)

    def test_path_with_extension(self) -> None:
        """Path with file extension pattern."""
        params = parse_django_path_params("files/<int:file_id>.json")
        self.assertEqual(len(params), 1)

    def test_consecutive_static_segments(self) -> None:
        """Path with multiple static segments."""
        params = parse_django_path_params("api/v1/public/users/")
        self.assertEqual(params, [])


class TestGetPlaceholderKwargs(TestCase):
    """Tests for get_placeholder_kwargs function."""

    def test_no_params(self) -> None:
        """Pattern without params returns empty dict."""
        result = get_placeholder_kwargs("users/")
        self.assertEqual(result, {})

    def test_int_param(self) -> None:
        """Integer parameter gets unique placeholder."""
        result = get_placeholder_kwargs("users/<int:pk>/")
        self.assertEqual(result, {"pk": 1000000})

    def test_str_param(self) -> None:
        """String parameter gets placeholder string."""
        result = get_placeholder_kwargs("users/<str:username>/")
        self.assertEqual(result, {"username": "__placeholder__"})

    def test_slug_param(self) -> None:
        """Slug parameter gets slug placeholder."""
        result = get_placeholder_kwargs("articles/<slug:slug>/")
        self.assertEqual(result, {"slug": "placeholder-slug"})

    def test_uuid_param(self) -> None:
        """UUID parameter gets unique UUID placeholder."""
        result = get_placeholder_kwargs("items/<uuid:item_id>/")
        self.assertEqual(result, {"item_id": "00000000-0000-0000-0000-000000000000"})

    def test_path_param(self) -> None:
        """Path parameter gets path placeholder."""
        result = get_placeholder_kwargs("files/<path:file_path>/")
        self.assertEqual(result, {"file_path": "placeholder/path"})

    def test_untyped_param_defaults_to_str(self) -> None:
        """Untyped parameter defaults to string placeholder."""
        result = get_placeholder_kwargs("users/<username>/")
        self.assertEqual(result, {"username": "__placeholder__"})

    def test_multiple_params(self) -> None:
        """Multiple parameters with different types."""
        result = get_placeholder_kwargs("users/<int:user_id>/posts/<uuid:post_id>/")
        self.assertEqual(
            result,
            {
                "user_id": 1000000,
                "post_id": "00000000-0000-0000-0000-000000000000",
            },
        )

    def test_multiple_same_type_params(self) -> None:
        """Multiple parameters with same type get unique placeholders."""
        result = get_placeholder_kwargs("users/<int:user_id>/posts/<int:post_id>/")
        self.assertEqual(
            result,
            {
                "user_id": 1000000,
                "post_id": 1000001,
            },
        )


class TestReplacePlaceholdersWithOpenAPIParams(TestCase):
    """Tests for replace_placeholders_with_openapi_params function."""

    def test_no_placeholders(self) -> None:
        """URL without placeholders remains unchanged."""
        result = replace_placeholders_with_openapi_params("/users/", {})
        self.assertEqual(result, "/users/")

    def test_single_int_placeholder(self) -> None:
        """Single integer placeholder is replaced."""
        result = replace_placeholders_with_openapi_params(
            "/api/users/1000000/", {"pk": 1000000}
        )
        self.assertEqual(result, "/api/users/{pk}/")

    def test_single_str_placeholder(self) -> None:
        """Single string placeholder is replaced."""
        result = replace_placeholders_with_openapi_params(
            "/api/users/__placeholder__/", {"username": "__placeholder__"}
        )
        self.assertEqual(result, "/api/users/{username}/")

    def test_uuid_placeholder(self) -> None:
        """UUID placeholder is replaced."""
        result = replace_placeholders_with_openapi_params(
            "/items/00000000-0000-0000-0000-000000000000/",
            {"item_id": "00000000-0000-0000-0000-000000000000"},
        )
        self.assertEqual(result, "/items/{item_id}/")

    def test_multiple_placeholders(self) -> None:
        """Multiple placeholders are replaced correctly."""
        result = replace_placeholders_with_openapi_params(
            "/api/router/users/1000000/posts/00000000-0000-0000-0000-000000000000/",
            {
                "user_id": 1000000,
                "post_id": "00000000-0000-0000-0000-000000000000",
            },
        )
        self.assertEqual(result, "/api/router/users/{user_id}/posts/{post_id}/")

    def test_preserves_base_path(self) -> None:
        """Base path before placeholders is preserved."""
        result = replace_placeholders_with_openapi_params(
            "/api/v2/router/users/1000000/", {"pk": 1000000}
        )
        self.assertEqual(result, "/api/v2/router/users/{pk}/")
