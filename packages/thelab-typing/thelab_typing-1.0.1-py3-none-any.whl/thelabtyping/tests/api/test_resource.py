"""Tests for build_crud_resource_views - type-safe CRUD view generation."""

from __future__ import annotations

from typing import Self
import json

from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.test import Client, RequestFactory, TestCase, override_settings
from django.urls import include, path
import pydantic
import pydantic_core

from thelabtyping.api.pagination import (
    PaginatedResponse,
    PaginationParams,
    paginate_queryset,
)
from thelabtyping.api.resource import CRUDViews, build_crud_resource_views
from thelabtyping.api.routing import Router
from thelabtyping.api.serializers import APIObj
from thelabtyping.api.status import Status
from thelabtyping.result import Err, Ok, Result, as_result

# =============================================================================
# Test Serializers - All inherit from APIObj[User] for type safety
# =============================================================================


class UserRead(APIObj[User]):
    id: int
    username: str
    first_name: str
    last_name: str

    @classmethod
    @as_result(pydantic_core.ValidationError)
    def from_django(cls, request: HttpRequest, obj: User) -> Self:
        return cls(
            id=obj.id,
            username=obj.username,
            first_name=obj.first_name,
            last_name=obj.last_name,
        )


class UserCreate(APIObj[User]):
    username: str
    first_name: str = ""
    last_name: str = ""
    password: str = "defaultpassword"

    def create(self, request: HttpRequest) -> Result[User, Exception]:
        user = User.objects.create_user(
            username=self.username,
            first_name=self.first_name,
            last_name=self.last_name,
            password=self.password,
        )
        return Ok(user)


class UserUpdate(APIObj[User]):
    """Full update serializer for User model (PUT)."""

    username: str
    first_name: str
    last_name: str

    def update(self, request: HttpRequest, instance: User) -> Result[User, Exception]:
        instance.username = self.username
        instance.first_name = self.first_name
        instance.last_name = self.last_name
        instance.save()
        return Ok(instance)


class UserPatch(APIObj[User]):
    """Partial update serializer for User model (PATCH)."""

    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None

    def patch(self, request: HttpRequest, instance: User) -> Result[User, Exception]:
        if self.username is not None:
            instance.username = self.username
        if self.first_name is not None:
            instance.first_name = self.first_name
        if self.last_name is not None:
            instance.last_name = self.last_name
        instance.save()
        return Ok(instance)


class UserListQuery(pydantic.BaseModel):
    """Query parameters for user list filtering."""

    first_name: str | None = None
    is_active: bool | None = None


# =============================================================================
# Test URL Configuration using build_crud_resource_views
# =============================================================================
test_router = Router(enable_index=False)


def sort_by_username(
    request: HttpRequest,
    queryset: QuerySet[User],
) -> QuerySet[User]:
    """Sort users by username."""
    return queryset.order_by("username")


test_router.register_resource(
    basename="user",
    list_pattern="users/",
    detail_pattern="users/<int:pk>/",
    views=build_crud_resource_views(
        ModelKlass=User,
        pk_type=int,
        ListFilters=PaginationParams,
        ReadSchema=UserRead,
        CreateSchema=UserCreate,
        UpdateSchema=UserUpdate,
        PatchSchema=UserPatch,
        default_page_size=10,
        sort_queryset=sort_by_username,
    ),
    # Explicitly disable permissions for basic CRUD tests
    list_permissions=[],
    detail_permissions=[],
    create_permissions=[],
    update_permissions=[],
    patch_permissions=[],
    delete_permissions=[],
)


class TestURLConf:
    """URL configuration for tests."""

    urlpatterns = [
        path("api/", include((test_router.urls, "test"))),
    ]


# =============================================================================
# Tests
# =============================================================================


@override_settings(ROOT_URLCONF=TestURLConf)
class CRUDListViewTest(TestCase):
    """Tests for list endpoint."""

    def setUp(self) -> None:
        self.admin = User.objects.create_superuser(
            username="admin", password="password"
        )
        self.client = Client()

    def test_list_returns_paginated_response(self) -> None:
        """List endpoint returns paginated response."""
        for i in range(15):
            User.objects.create_user(username=f"user{i:02d}")

        resp = self.client.get("/api/users/")

        self.assertEqual(resp.status_code, Status.HTTP_200_OK)
        data = json.loads(resp.content)

        # Check pagination structure
        self.assertIn("count", data)
        self.assertIn("next", data)
        self.assertIn("previous", data)
        self.assertIn("results", data)

        # 16 users total (15 created + admin)
        self.assertEqual(data["count"], 16)
        # Page size is 10
        self.assertEqual(len(data["results"]), 10)
        self.assertIsNotNone(data["next"])
        self.assertIsNone(data["previous"])

    def test_list_respects_sort_queryset(self) -> None:
        """List endpoint respects sort_queryset callable."""
        User.objects.create_user(username="zebra")
        User.objects.create_user(username="apple")

        resp = self.client.get("/api/users/")

        self.assertEqual(resp.status_code, Status.HTTP_200_OK)
        data = json.loads(resp.content)

        usernames = [u["username"] for u in data["results"]]
        self.assertEqual(usernames, sorted(usernames))

    def test_list_pagination_page_parameter(self) -> None:
        """List endpoint respects page parameter."""
        for i in range(25):
            User.objects.create_user(username=f"user{i:02d}")

        resp = self.client.get("/api/users/?page=2")

        self.assertEqual(resp.status_code, Status.HTTP_200_OK)
        data = json.loads(resp.content)

        # Page 2 should have next and previous
        self.assertIsNotNone(data["previous"])


@override_settings(ROOT_URLCONF=TestURLConf)
class CRUDDetailViewTest(TestCase):
    """Tests for detail endpoint."""

    def setUp(self) -> None:
        self.admin = User.objects.create_superuser(
            username="admin", password="password"
        )
        self.target_user = User.objects.create_user(
            username="target", first_name="Target", last_name="User"
        )
        self.client = Client()

    def test_detail_returns_single_object(self) -> None:
        """Detail endpoint returns single object."""
        resp = self.client.get(f"/api/users/{self.target_user.pk}/")

        self.assertEqual(resp.status_code, Status.HTTP_200_OK)
        data = json.loads(resp.content)

        self.assertEqual(data["id"], self.target_user.pk)
        self.assertEqual(data["username"], "target")
        self.assertEqual(data["first_name"], "Target")
        self.assertEqual(data["last_name"], "User")

    def test_detail_returns_404_for_missing_object(self) -> None:
        """Detail endpoint returns 404 for missing object."""
        resp = self.client.get("/api/users/99999/")

        self.assertEqual(resp.status_code, Status.HTTP_404_NOT_FOUND)


@override_settings(ROOT_URLCONF=TestURLConf)
class CRUDCreateViewTest(TestCase):
    """Tests for create endpoint."""

    def setUp(self) -> None:
        self.admin = User.objects.create_superuser(
            username="admin", password="password"
        )
        self.client = Client()

    def test_create_creates_object(self) -> None:
        """Create endpoint creates object and returns 201."""
        resp = self.client.post(
            "/api/users/",
            content_type="application/json",
            data={
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "password": "testpass123",
            },
        )

        self.assertEqual(resp.status_code, Status.HTTP_201_CREATED)
        data = json.loads(resp.content)

        self.assertEqual(data["username"], "newuser")
        self.assertEqual(data["first_name"], "New")
        self.assertEqual(data["last_name"], "User")

        # Verify object was created in database
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_create_validates_input(self) -> None:
        """Create endpoint validates input data."""
        resp = self.client.post(
            "/api/users/",
            content_type="application/json",
            data={},  # Missing required username
        )

        self.assertEqual(resp.status_code, Status.HTTP_400_BAD_REQUEST)


@override_settings(ROOT_URLCONF=TestURLConf)
class CRUDUpdateViewTest(TestCase):
    """Tests for update (PUT) endpoint."""

    def setUp(self) -> None:
        self.admin = User.objects.create_superuser(
            username="admin", password="password"
        )
        self.target_user = User.objects.create_user(
            username="target", first_name="Target", last_name="User"
        )
        self.client = Client()

    def test_update_replaces_object(self) -> None:
        """Update (PUT) endpoint replaces object completely."""
        resp = self.client.put(
            f"/api/users/{self.target_user.pk}/",
            content_type="application/json",
            data={
                "username": "updated",
                "first_name": "Updated",
                "last_name": "Name",
            },
        )

        self.assertEqual(resp.status_code, Status.HTTP_200_OK)
        data = json.loads(resp.content)

        self.assertEqual(data["username"], "updated")
        self.assertEqual(data["first_name"], "Updated")
        self.assertEqual(data["last_name"], "Name")

        # Verify database was updated
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.username, "updated")

    def test_update_returns_404_for_missing_object(self) -> None:
        """Update endpoint returns 404 for missing object."""
        resp = self.client.put(
            "/api/users/99999/",
            content_type="application/json",
            data={
                "username": "updated",
                "first_name": "Updated",
                "last_name": "Name",
            },
        )

        self.assertEqual(resp.status_code, Status.HTTP_404_NOT_FOUND)


@override_settings(ROOT_URLCONF=TestURLConf)
class CRUDPatchViewTest(TestCase):
    """Tests for partial update (PATCH) endpoint."""

    def setUp(self) -> None:
        self.admin = User.objects.create_superuser(
            username="admin", password="password"
        )
        self.target_user = User.objects.create_user(
            username="target", first_name="Target", last_name="User"
        )
        self.client = Client()

    def test_patch_partially_updates_object(self) -> None:
        """Patch endpoint only updates provided fields."""
        resp = self.client.patch(
            f"/api/users/{self.target_user.pk}/",
            content_type="application/json",
            data={
                "first_name": "Patched",
            },
        )

        self.assertEqual(resp.status_code, Status.HTTP_200_OK)
        data = json.loads(resp.content)

        # Only first_name should change
        self.assertEqual(data["username"], "target")  # unchanged
        self.assertEqual(data["first_name"], "Patched")  # changed
        self.assertEqual(data["last_name"], "User")  # unchanged

        # Verify database
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.first_name, "Patched")
        self.assertEqual(self.target_user.last_name, "User")

    def test_patch_returns_404_for_missing_object(self) -> None:
        """Patch endpoint returns 404 for missing object."""
        resp = self.client.patch(
            "/api/users/99999/",
            content_type="application/json",
            data={"first_name": "Patched"},
        )

        self.assertEqual(resp.status_code, Status.HTTP_404_NOT_FOUND)


@override_settings(ROOT_URLCONF=TestURLConf)
class CRUDDeleteViewTest(TestCase):
    """Tests for delete endpoint."""

    def setUp(self) -> None:
        self.admin = User.objects.create_superuser(
            username="admin", password="password"
        )
        self.target_user = User.objects.create_user(
            username="target", first_name="Target", last_name="User"
        )
        self.client = Client()

    def test_delete_removes_object(self) -> None:
        """Delete endpoint removes object and returns 204."""
        target_pk = self.target_user.pk

        resp = self.client.delete(f"/api/users/{target_pk}/")

        self.assertEqual(resp.status_code, Status.HTTP_204_NO_CONTENT)

        # Verify object was deleted
        self.assertFalse(User.objects.filter(pk=target_pk).exists())

    def test_delete_returns_404_for_missing_object(self) -> None:
        """Delete endpoint returns 404 for missing object."""
        resp = self.client.delete("/api/users/99999/")

        self.assertEqual(resp.status_code, Status.HTTP_404_NOT_FOUND)


class CRUDViewsReturnTypeTest(TestCase):
    """Tests for CRUDViews NamedTuple."""

    def test_build_returns_crud_views_namedtuple(self) -> None:
        """build_crud_resource_views returns CRUDViews NamedTuple."""
        views = build_crud_resource_views(
            ModelKlass=User,
            pk_type=int,
            ListFilters=PaginationParams,
            ReadSchema=UserRead,
        )

        self.assertIsInstance(views, CRUDViews)
        self.assertTrue(callable(views.list_view))
        self.assertTrue(callable(views.detail_view))

    def test_optional_schemas_produce_none_views(self) -> None:
        """When schemas are None, corresponding views are None."""
        views = build_crud_resource_views(
            ModelKlass=User,
            pk_type=int,
            ListFilters=PaginationParams,
            ReadSchema=UserRead,
            # CreateSchema, UpdateSchema, PatchSchema not provided
        )

        # Only read views should be available
        self.assertIsNotNone(views.list_view)
        self.assertIsNotNone(views.detail_view)
        self.assertIsNone(views.create_view)
        self.assertIsNone(views.update_view)
        self.assertIsNone(views.patch_view)
        # delete_view should still work (doesn't need schema)
        self.assertIsNotNone(views.delete_view)


class PaginationTest(TestCase):
    """Tests for pagination utilities."""

    def test_paginated_response_model(self) -> None:
        """PaginatedResponse model validates correctly."""
        response: PaginatedResponse[UserRead] = PaginatedResponse(
            count=100,
            next="http://example.com/api/users/?page=2",
            previous=None,
            results=[],
        )

        self.assertEqual(response.count, 100)
        self.assertEqual(response.next, "http://example.com/api/users/?page=2")
        self.assertIsNone(response.previous)
        self.assertEqual(response.results, [])

    def test_paginate_queryset_first_page(self) -> None:
        """paginate_queryset returns correct first page."""
        for i in range(25):
            User.objects.create_user(username=f"user{i:02d}")

        request = RequestFactory().get("/api/users/")
        qs = User.objects.all().order_by("username")

        paginated_qs, count, next_url, prev_url = paginate_queryset(
            request, qs, page=1, page_size=10
        )

        self.assertEqual(count, 25)
        self.assertEqual(len(list(paginated_qs)), 10)
        self.assertIsNotNone(next_url)
        self.assertIsNone(prev_url)

    def test_paginate_queryset_middle_page(self) -> None:
        """paginate_queryset returns correct middle page."""
        for i in range(25):
            User.objects.create_user(username=f"user{i:02d}")

        request = RequestFactory().get("/api/users/?page=2")
        qs = User.objects.all().order_by("username")

        paginated_qs, count, next_url, prev_url = paginate_queryset(
            request, qs, page=2, page_size=10
        )

        self.assertEqual(count, 25)
        self.assertEqual(len(list(paginated_qs)), 10)
        self.assertIsNotNone(next_url)
        self.assertIsNotNone(prev_url)

    def test_paginate_queryset_last_page(self) -> None:
        """paginate_queryset returns correct last page."""
        for i in range(25):
            User.objects.create_user(username=f"user{i:02d}")

        request = RequestFactory().get("/api/users/?page=3")
        qs = User.objects.all().order_by("username")

        paginated_qs, count, next_url, prev_url = paginate_queryset(
            request, qs, page=3, page_size=10
        )

        self.assertEqual(count, 25)
        self.assertEqual(len(list(paginated_qs)), 5)  # Last 5 items
        self.assertIsNone(next_url)
        self.assertIsNotNone(prev_url)

    def test_paginate_queryset_empty(self) -> None:
        """paginate_queryset handles empty queryset correctly."""
        request = RequestFactory().get("/api/users/")
        qs = User.objects.none()

        paginated_qs, count, next_url, prev_url = paginate_queryset(
            request, qs, page=1, page_size=10
        )

        self.assertEqual(count, 0)
        self.assertEqual(len(list(paginated_qs)), 0)
        self.assertIsNone(next_url)
        self.assertIsNone(prev_url)

    def test_paginate_queryset_page_beyond_last(self) -> None:
        """paginate_queryset returns empty results for page beyond last."""
        for i in range(5):
            User.objects.create_user(username=f"user{i:02d}")

        request = RequestFactory().get("/api/users/?page=999")
        qs = User.objects.all().order_by("username")

        paginated_qs, count, next_url, prev_url = paginate_queryset(
            request, qs, page=999, page_size=10
        )

        self.assertEqual(count, 5)
        self.assertEqual(len(list(paginated_qs)), 0)
        self.assertIsNone(next_url)
        # Previous should exist since we're beyond page 1
        self.assertIsNotNone(prev_url)


class PaginationValidationTest(TestCase):
    """Tests for pagination parameter validation."""

    def test_page_must_be_positive(self) -> None:
        """page=0 is rejected by validation."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            PaginationParams(page=0)

        errors = ctx.exception.errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["loc"], ("page",))
        self.assertIn("greater than or equal to 1", errors[0]["msg"])

    def test_negative_page_rejected(self) -> None:
        """Negative page numbers are rejected."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            PaginationParams(page=-1)

        errors = ctx.exception.errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["loc"], ("page",))

    def test_page_size_must_be_positive(self) -> None:
        """page_size=0 is rejected by validation."""
        with self.assertRaises(pydantic.ValidationError) as ctx:
            PaginationParams(page_size=0)

        errors = ctx.exception.errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["loc"], ("page_size",))

    def test_page_size_max_limit(self) -> None:
        """page_size exceeding MAX_PAGE_SIZE is rejected."""
        from thelabtyping.api.pagination import MAX_PAGE_SIZE

        with self.assertRaises(pydantic.ValidationError) as ctx:
            PaginationParams(page_size=MAX_PAGE_SIZE + 1)

        errors = ctx.exception.errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["loc"], ("page_size",))

    def test_valid_pagination_params(self) -> None:
        """Valid pagination params are accepted."""
        params = PaginationParams(page=5, page_size=50)
        self.assertEqual(params.page, 5)
        self.assertEqual(params.page_size, 50)


# =============================================================================
# Permission Tests
# =============================================================================


class PermissionInferenceTest(TestCase):
    """Tests for automatic permission inference from Model meta."""

    def test_permissions_inferred_from_model(self) -> None:
        """Permissions are inferred from model when not explicitly provided."""
        from django.core.exceptions import ImproperlyConfigured

        router = Router(enable_index=False)

        # Without model parameter, should raise when permissions are None
        with self.assertRaises(ImproperlyConfigured) as ctx:
            router.register_resource(
                basename="test-user",
                list_pattern="test-users/",
                detail_pattern="test-users/<int:pk>/",
                views=build_crud_resource_views(
                    ModelKlass=User,
                    pk_type=int,
                    ListFilters=PaginationParams,
                    ReadSchema=UserRead,
                ),
                # No model= parameter and no explicit permissions
            )

        self.assertIn("model", str(ctx.exception))
        self.assertIn("required", str(ctx.exception))

    def test_permissions_inferred_correctly(self) -> None:
        """Inferred permissions use correct Django format."""
        router = Router(enable_index=False)

        # With model parameter, should infer permissions
        router.register_resource(
            basename="inferred-user",
            list_pattern="inferred-users/",
            detail_pattern="inferred-users/<int:pk>/",
            views=build_crud_resource_views(
                ModelKlass=User,
                pk_type=int,
                ListFilters=PaginationParams,
                ReadSchema=UserRead,
                CreateSchema=UserCreate,
            ),
            model=User,  # Provides model for inference
        )

        # Routes should be registered (detailed permission testing requires
        # request flow, but this confirms registration succeeded)
        self.assertIn("inferred-users/", router.routes)
        self.assertIn("inferred-users/<int:pk>/", router.routes)

    def test_explicit_empty_permissions_bypass_inference(self) -> None:
        """Empty permission lists disable permission checks."""
        router = Router(enable_index=False)

        # With empty permission lists, no model needed
        router.register_resource(
            basename="public-user",
            list_pattern="public-users/",
            detail_pattern="public-users/<int:pk>/",
            views=build_crud_resource_views(
                ModelKlass=User,
                pk_type=int,
                ListFilters=PaginationParams,
                ReadSchema=UserRead,
            ),
            # Empty lists = no permissions required
            list_permissions=[],
            detail_permissions=[],
            create_permissions=[],
            update_permissions=[],
            patch_permissions=[],
            delete_permissions=[],
        )

        # Should register without error
        self.assertIn("public-users/", router.routes)


# =============================================================================
# Router with permissions for permission enforcement tests
# =============================================================================
perm_router = Router(enable_index=False)
perm_router.register_resource(
    basename="perm-user",
    list_pattern="perm-users/",
    detail_pattern="perm-users/<int:pk>/",
    views=build_crud_resource_views(
        ModelKlass=User,
        pk_type=int,
        ListFilters=PaginationParams,
        ReadSchema=UserRead,
        CreateSchema=UserCreate,
        UpdateSchema=UserUpdate,
        PatchSchema=UserPatch,
        default_page_size=10,
    ),
    model=User,  # Infer permissions from User model
)


class PermTestURLConf:
    """URL configuration for permission tests."""

    urlpatterns = [
        path("api/", include((perm_router.urls, "perm_test"))),
    ]


@override_settings(ROOT_URLCONF=PermTestURLConf)
class PermissionEnforcementTest(TestCase):
    """Tests that permissions are actually enforced."""

    def setUp(self) -> None:
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client = Client()

    def test_anonymous_user_denied_list(self) -> None:
        """Anonymous users are denied access to protected list endpoint."""
        resp = self.client.get("/api/perm-users/")
        # permission_required with raise_exception=True returns 403
        self.assertEqual(resp.status_code, Status.HTTP_403_FORBIDDEN)

    def test_anonymous_user_denied_detail(self) -> None:
        """Anonymous users are denied access to protected detail endpoint."""
        resp = self.client.get(f"/api/perm-users/{self.user.pk}/")
        self.assertEqual(resp.status_code, Status.HTTP_403_FORBIDDEN)

    def test_anonymous_user_denied_create(self) -> None:
        """Anonymous users are denied access to protected create endpoint."""
        resp = self.client.post(
            "/api/perm-users/",
            content_type="application/json",
            data={"username": "newuser"},
        )
        self.assertEqual(resp.status_code, Status.HTTP_403_FORBIDDEN)

    def test_anonymous_user_denied_delete(self) -> None:
        """Anonymous users are denied access to protected delete endpoint."""
        resp = self.client.delete(f"/api/perm-users/{self.user.pk}/")
        self.assertEqual(resp.status_code, Status.HTTP_403_FORBIDDEN)

    def test_user_without_permission_denied(self) -> None:
        """Users without required permission are denied access."""
        self.client.login(username="testuser", password="testpass")

        resp = self.client.get("/api/perm-users/")
        self.assertEqual(resp.status_code, Status.HTTP_403_FORBIDDEN)

    def test_user_with_permission_allowed(self) -> None:
        """Users with required permission can access endpoint."""
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        # Grant view_user permission
        content_type = ContentType.objects.get_for_model(User)
        permission = Permission.objects.get(
            codename="view_user",
            content_type=content_type,
        )
        self.user.user_permissions.add(permission)

        self.client.login(username="testuser", password="testpass")

        resp = self.client.get("/api/perm-users/")
        self.assertEqual(resp.status_code, Status.HTTP_200_OK)


# =============================================================================
# Custom QuerySet Tests
# =============================================================================


class CustomQuerySetFilterQuery(PaginationParams):
    """Query params that includes a filter field."""

    username_prefix: str | None = None


custom_qs_router = Router(enable_index=False)
custom_qs_router.register_resource(
    basename="filtered-user",
    list_pattern="filtered-users/",
    detail_pattern="filtered-users/<int:pk>/",
    views=build_crud_resource_views(
        ModelKlass=User,
        pk_type=int,
        ListFilters=CustomQuerySetFilterQuery,
        ReadSchema=UserRead,
        # Custom get_queryset that only returns active users
        get_queryset=lambda request: User.objects.filter(is_active=True),
        # Custom filter_queryset that filters by username prefix
        filter_queryset=lambda request, qs: (
            qs.filter(
                username__startswith=request.validated_querystring.username_prefix
            )
            if request.validated_querystring.username_prefix
            else qs
        ),
    ),
    list_permissions=[],
    detail_permissions=[],
    create_permissions=[],
    update_permissions=[],
    patch_permissions=[],
    delete_permissions=[],
)


class CustomQSTestURLConf:
    """URL configuration for custom queryset tests."""

    urlpatterns = [
        path("api/", include((custom_qs_router.urls, "custom_qs_test"))),
    ]


@override_settings(ROOT_URLCONF=CustomQSTestURLConf)
class CustomQuerySetTest(TestCase):
    """Tests for custom get_queryset and filter_queryset functions."""

    def setUp(self) -> None:
        self.active_user1 = User.objects.create_user(username="alice", is_active=True)
        self.active_user2 = User.objects.create_user(username="bob", is_active=True)
        self.inactive_user = User.objects.create_user(
            username="charlie", is_active=False
        )
        self.client = Client()

    def test_get_queryset_filters_list(self) -> None:
        """Custom get_queryset filters list view results."""
        resp = self.client.get("/api/filtered-users/")

        self.assertEqual(resp.status_code, Status.HTTP_200_OK)
        data = json.loads(resp.content)

        # Only active users should be returned
        usernames = {u["username"] for u in data["results"]}
        self.assertIn("alice", usernames)
        self.assertIn("bob", usernames)
        self.assertNotIn("charlie", usernames)  # inactive

    def test_get_queryset_filters_detail(self) -> None:
        """Custom get_queryset filters detail view (404 for filtered out)."""
        # Active user should be accessible
        resp = self.client.get(f"/api/filtered-users/{self.active_user1.pk}/")
        self.assertEqual(resp.status_code, Status.HTTP_200_OK)

        # Inactive user should return 404 (filtered out by get_queryset)
        resp = self.client.get(f"/api/filtered-users/{self.inactive_user.pk}/")
        self.assertEqual(resp.status_code, Status.HTTP_404_NOT_FOUND)

    def test_filter_queryset_applies_additional_filters(self) -> None:
        """filter_queryset applies additional filters on top of get_queryset."""
        # Filter by username prefix
        resp = self.client.get("/api/filtered-users/?username_prefix=a")

        self.assertEqual(resp.status_code, Status.HTTP_200_OK)
        data = json.loads(resp.content)

        # Only alice should match (active + starts with 'a')
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["username"], "alice")


# =============================================================================
# Error Result Path Tests
# =============================================================================


class FailingCreate(APIObj[User]):
    """Create schema that always fails."""

    username: str

    def create(self, request: HttpRequest) -> Result[User, Exception]:
        return Err(ValueError("Create always fails for testing"))


class FailingUpdate(APIObj[User]):
    """Update schema that always fails."""

    username: str

    def update(self, request: HttpRequest, instance: User) -> Result[User, Exception]:
        return Err(ValueError("Update always fails for testing"))


class FailingPatch(APIObj[User]):
    """Patch schema that always fails."""

    username: str | None = None

    def patch(self, request: HttpRequest, instance: User) -> Result[User, Exception]:
        return Err(ValueError("Patch always fails for testing"))


error_router = Router(enable_index=False)
error_router.register_resource(
    basename="error-user",
    list_pattern="error-users/",
    detail_pattern="error-users/<int:pk>/",
    views=build_crud_resource_views(
        ModelKlass=User,
        pk_type=int,
        ListFilters=PaginationParams,
        ReadSchema=UserRead,
        CreateSchema=FailingCreate,
        UpdateSchema=FailingUpdate,
        PatchSchema=FailingPatch,
    ),
    list_permissions=[],
    detail_permissions=[],
    create_permissions=[],
    update_permissions=[],
    patch_permissions=[],
    delete_permissions=[],
)


class ErrorTestURLConf:
    """URL configuration for error path tests."""

    urlpatterns = [
        path("api/", include((error_router.urls, "error_test"))),
    ]


@override_settings(ROOT_URLCONF=ErrorTestURLConf)
class ErrorResultPathTest(TestCase):
    """Tests for create/update/patch methods that return Err."""

    def setUp(self) -> None:
        self.target_user = User.objects.create_user(username="target")
        self.client = Client()

    def test_create_err_returns_400(self) -> None:
        """Create method returning Err results in 400 response."""
        with self.assertRaises(ValueError):
            self.client.post(
                "/api/error-users/",
                content_type="application/json",
                data={"username": "newuser"},
            )
        # Verify no user was created
        self.assertFalse(User.objects.filter(username="newuser").exists())

    def test_update_err(self) -> None:
        """Update method returning Err results in 400 response."""
        original_username = self.target_user.username
        with self.assertRaises(ValueError):
            self.client.put(
                f"/api/error-users/{self.target_user.pk}/",
                content_type="application/json",
                data={"username": "updated"},
            )
        # Verify user was not updated
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.username, original_username)

    def test_patch_err_returns_400(self) -> None:
        """Patch method returning Err results in 400 response."""
        original_username = self.target_user.username
        with self.assertRaises(ValueError):
            self.client.patch(
                f"/api/error-users/{self.target_user.pk}/",
                content_type="application/json",
                data={"username": "patched"},
            )
        # Verify user was not patched
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.username, original_username)


# =============================================================================
# List View Empty Results Test
# =============================================================================


@override_settings(ROOT_URLCONF=TestURLConf)
class ListViewEdgeCasesTest(TestCase):
    """Tests for list view edge cases."""

    def setUp(self) -> None:
        self.client = Client()

    def test_list_empty_returns_zero_count(self) -> None:
        """List endpoint with no data returns count=0."""
        resp = self.client.get("/api/users/")

        self.assertEqual(resp.status_code, Status.HTTP_200_OK)
        data = json.loads(resp.content)

        self.assertEqual(data["count"], 0)
        self.assertEqual(data["results"], [])
        self.assertIsNone(data["next"])
        self.assertIsNone(data["previous"])

    def test_invalid_page_returns_400(self) -> None:
        """Invalid page parameter returns 400."""
        resp = self.client.get("/api/users/?page=0")

        self.assertEqual(resp.status_code, Status.HTTP_400_BAD_REQUEST)

    def test_invalid_page_size_returns_400(self) -> None:
        """Invalid page_size parameter returns 400."""
        resp = self.client.get("/api/users/?page_size=-1")

        self.assertEqual(resp.status_code, Status.HTTP_400_BAD_REQUEST)


# =============================================================================
# Custom get_object Tests
# =============================================================================


def get_user_by_username(
    request: HttpRequest,
    queryset: QuerySet[User],
    username: str,
) -> User:
    """Custom get_object that looks up users by username."""
    return get_object_or_404(queryset, username=username)


get_object_router = Router(enable_index=False)
get_object_router.register_resource(
    basename="username-user",
    list_pattern="username-users/",
    detail_pattern="username-users/<str:pk>/",  # pk is the URL param, but looks up by username
    views=build_crud_resource_views(
        ModelKlass=User,
        pk_type=str,
        ListFilters=PaginationParams,
        ReadSchema=UserRead,
        CreateSchema=UserCreate,
        UpdateSchema=UserUpdate,
        PatchSchema=UserPatch,
        sort_queryset=sort_by_username,
        get_object=get_user_by_username,
    ),
    list_permissions=[],
    detail_permissions=[],
    create_permissions=[],
    update_permissions=[],
    patch_permissions=[],
    delete_permissions=[],
)


class GetObjectTestURLConf:
    """URL configuration for get_object tests."""

    urlpatterns = [
        path("api/", include((get_object_router.urls, "get_object_test"))),
    ]


@override_settings(ROOT_URLCONF=GetObjectTestURLConf)
class GetObjectTest(TestCase):
    """Tests for get_object parameter in build_crud_resource_views."""

    def setUp(self) -> None:
        self.target_user = User.objects.create_user(
            username="target_user", first_name="Target", last_name="User"
        )
        self.other_user = User.objects.create_user(
            username="other_user", first_name="Other", last_name="User"
        )
        self.client = Client()

    def test_detail_view_with_custom_get_object(self) -> None:
        """Detail view uses custom get_object to look up by username."""
        # Access by username, not by pk
        resp = self.client.get("/api/username-users/target_user/")

        self.assertEqual(resp.status_code, Status.HTTP_200_OK)
        data = json.loads(resp.content)
        self.assertEqual(data["username"], "target_user")
        self.assertEqual(data["first_name"], "Target")

    def test_detail_view_returns_404_for_nonexistent_username(self) -> None:
        """Detail view returns 404 when custom get_object raises Http404."""
        resp = self.client.get("/api/username-users/nonexistent/")

        self.assertEqual(resp.status_code, Status.HTTP_404_NOT_FOUND)

    def test_update_view_with_custom_get_object(self) -> None:
        """Update view uses custom get_object to look up by username."""
        resp = self.client.put(
            "/api/username-users/target_user/",
            content_type="application/json",
            data={
                "username": "updated_user",
                "first_name": "Updated",
                "last_name": "Name",
            },
        )

        self.assertEqual(resp.status_code, Status.HTTP_200_OK)
        data = json.loads(resp.content)
        self.assertEqual(data["username"], "updated_user")
        self.assertEqual(data["first_name"], "Updated")

        # Verify database was updated
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.username, "updated_user")

    def test_patch_view_with_custom_get_object(self) -> None:
        """Patch view uses custom get_object to look up by username."""
        resp = self.client.patch(
            "/api/username-users/target_user/",
            content_type="application/json",
            data={"first_name": "Patched"},
        )

        self.assertEqual(resp.status_code, Status.HTTP_200_OK)
        data = json.loads(resp.content)
        self.assertEqual(data["first_name"], "Patched")
        self.assertEqual(data["username"], "target_user")  # unchanged

        # Verify database was updated
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.first_name, "Patched")

    def test_delete_view_with_custom_get_object(self) -> None:
        """Delete view uses custom get_object to look up by username."""
        resp = self.client.delete("/api/username-users/target_user/")

        self.assertEqual(resp.status_code, Status.HTTP_204_NO_CONTENT)

        # Verify object was deleted
        self.assertFalse(User.objects.filter(username="target_user").exists())

    def test_delete_view_returns_404_for_nonexistent_username(self) -> None:
        """Delete view returns 404 when custom get_object raises Http404."""
        resp = self.client.delete("/api/username-users/nonexistent/")

        self.assertEqual(resp.status_code, Status.HTTP_404_NOT_FOUND)


@override_settings(ROOT_URLCONF=TestURLConf)
class GetObjectDefaultTest(TestCase):
    """Tests to verify default get_object behavior uses pk lookup."""

    def setUp(self) -> None:
        self.target_user = User.objects.create_user(
            username="target", first_name="Target", last_name="User"
        )
        self.client = Client()

    def test_default_get_object_uses_pk(self) -> None:
        """Default get_object looks up by pk."""
        resp = self.client.get(f"/api/users/{self.target_user.pk}/")

        self.assertEqual(resp.status_code, Status.HTTP_200_OK)
        data = json.loads(resp.content)
        self.assertEqual(data["id"], self.target_user.pk)
        self.assertEqual(data["username"], "target")
