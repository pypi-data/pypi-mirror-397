from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from functools import reduce
from operator import or_
from typing import Concatenate, NewType, Protocol

from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model
from django.http import HttpRequest, HttpResponseBase, HttpResponseNotAllowed
from django.urls import URLPattern, path, reverse
from django.urls.exceptions import NoReverseMatch
import pydantic

from ..abc import DictOf
from .resource import CRUDViews
from .responses import APIResponse


class HttpMethod(StrEnum):
    """HTTP request methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


URLPatternStr = NewType("URLPatternStr", str)
AllowedMethods = set[HttpMethod]

type ViewFn[**P, R: HttpResponseBase] = Callable[Concatenate[HttpRequest, P], R]
type ViewDecorator = Callable[
    [Callable[..., HttpResponseBase]],
    Callable[..., HttpResponseBase],
]

ALL_METHODS: AllowedMethods = {
    HttpMethod.GET,
    HttpMethod.POST,
    HttpMethod.PUT,
    HttpMethod.PATCH,
    HttpMethod.DELETE,
}


@dataclass
class RegisteredView[**P, R: HttpResponseBase]:
    """Container for a view function and its allowed HTTP methods."""

    methods: AllowedMethods
    fn: ViewFn[P, R]


@dataclass
class Route:
    """Represents a URL route with multiple HTTP method handlers."""

    name: str
    views: list[RegisteredView[[], HttpResponseBase]]
    decorators: Sequence[ViewDecorator]
    _router_decorators: Sequence[ViewDecorator]
    _cached_view: Callable[..., HttpResponseBase] | None

    def __init__(
        self,
        name: str,
        decorators: Sequence[ViewDecorator] | None = None,
        router_decorators: Sequence[ViewDecorator] | None = None,
    ) -> None:
        """Initialize a new route with the given name and optional decorators."""
        self.name = name
        self.views = []
        self.decorators = decorators or []
        self._router_decorators = router_decorators or []
        self._cached_view = None

    def get[**P, R: HttpResponseBase](self, fn: ViewFn[P, R]) -> ViewFn[P, R]:
        """Register a view function for GET requests."""
        return self.register({HttpMethod.GET})(fn)

    def post[**P, R: HttpResponseBase](self, fn: ViewFn[P, R]) -> ViewFn[P, R]:
        """Register a view function for POST requests."""
        return self.register({HttpMethod.POST})(fn)

    def put[**P, R: HttpResponseBase](self, fn: ViewFn[P, R]) -> ViewFn[P, R]:
        """Register a view function for PUT requests."""
        return self.register({HttpMethod.PUT})(fn)

    def patch[**P, R: HttpResponseBase](self, fn: ViewFn[P, R]) -> ViewFn[P, R]:
        """Register a view function for PATCH requests."""
        return self.register({HttpMethod.PATCH})(fn)

    def delete[**P, R: HttpResponseBase](self, fn: ViewFn[P, R]) -> ViewFn[P, R]:
        """Register a view function for DELETE requests."""
        return self.register({HttpMethod.DELETE})(fn)

    def register[**P, R: HttpResponseBase](
        self,
        methods: AllowedMethods = ALL_METHODS,
    ) -> Callable[
        [ViewFn[P, R]],
        ViewFn[P, R],
    ]:
        """Register a view function for the specified HTTP methods."""

        def decorator(view_fn: ViewFn[P, R]) -> ViewFn[P, R]:
            self.add_view(view_fn, methods)
            return view_fn

        return decorator

    def add_view[**P, R: HttpResponseBase](
        self,
        view_fn: ViewFn[P, R],
        methods: AllowedMethods,
    ) -> None:
        """Add a view function to this route for the given methods."""
        conflicts = self.allowed_methods & methods
        if conflicts:
            raise ImproperlyConfigured(
                f"Cannot {view_fn} for methods {conflicts}. Views already "
                "exist for these methods."
            )
        self.views.append(
            RegisteredView(
                methods=methods,
                fn=view_fn,
            )
        )

    def dispatch(
        self,
        request: HttpRequest,
        *args: object,
        **kwargs: object,
    ) -> HttpResponseBase:
        """Dispatch an incoming request to the appropriate view function."""
        for view in self.views:
            if request.method in view.methods:
                return view.fn(request, *args, **kwargs)

        return HttpResponseNotAllowed(self.allowed_methods)

    @property
    def allowed_methods(self) -> AllowedMethods:
        """Get all HTTP methods supported by this route."""
        return reduce(or_, (view.methods for view in self.views), set())

    @property
    def view(self) -> Callable[..., HttpResponseBase]:
        """Get dispatch with all decorators applied (router-level first, then route-level)."""
        if self._cached_view is None:
            # No decorators - return dispatch directly
            if not self.decorators and not self._router_decorators:
                self._cached_view = self.dispatch
            else:
                result: Callable[..., HttpResponseBase] = self.dispatch
                # Apply router-level decorators first (innermost)
                for decorator in self._router_decorators:
                    result = decorator(result)
                # Apply route-level decorators on top (outermost)
                for decorator in self.decorators:
                    result = decorator(result)
                self._cached_view = result
        return self._cached_view


type RouteMap = dict[URLPatternStr, Route]


class SchemaGenerator(Protocol):
    """Protocol for API schema generators (OpenAPI, etc.).

    Schema generators handle the full view logic including authentication,
    caching, and response serialization. The Router treats them as views.

    Example implementation:
        @dataclass
        class MySchemaGenerator:
            def __call__(
                self, router: Router, request: HttpRequest
            ) -> HttpResponseBase:
                spec = generate_my_schema(router.routes)
                return APIResponse(spec)
    """

    def __call__(self, router: Router, request: HttpRequest) -> HttpResponseBase:
        """Handle a schema request.

        Args:
            router: The Router instance (provides access to routes).
            request: The incoming HTTP request.

        Returns:
            An HTTP response (typically APIResponse with serialized schema).
        """
        ...


RouterIndex = DictOf[str, pydantic.HttpUrl]


class Router:
    """URL router for organizing and dispatching API routes."""

    basename: str | None = None
    routes: RouteMap
    decorators: Sequence[ViewDecorator]
    _schemas: Mapping[str, SchemaGenerator]

    def __init__(
        self,
        basename: str | None = None,
        enable_index: bool = True,
        schemas: Mapping[str, SchemaGenerator] | None = None,
        decorators: Sequence[ViewDecorator] | None = None,
    ) -> None:
        """Initialize a new router with optional basename, index view, and decorators."""
        self.basename = basename
        self.routes: RouteMap = {}
        self.decorators = decorators or []
        self._schemas = schemas or {}
        # Immediately register the root index view
        if enable_index:
            self.route("", name="index", get=self.index_view)

        # Register schema endpoints - generator handles ALL view logic (auth, caching, response)
        # Create a view that passes self (router) to the generator
        def make_schema_view(
            gen: SchemaGenerator,
        ) -> Callable[[HttpRequest], HttpResponseBase]:
            def view(request: HttpRequest) -> HttpResponseBase:
                return gen(self, request)

            return view

        for url_pattern, generator in self._schemas.items():
            route_name = url_pattern.lower().replace(".", "-")
            route_name = f"schema-{route_name}"
            self.route(
                url_pattern,
                name=route_name,
                get=make_schema_view(generator),
            )

    def index_view(self, request: HttpRequest) -> APIResponse[RouterIndex]:
        """Auto-generated index view listing all available routes."""
        index = RouterIndex({})
        namespace = request.resolver_match.namespace if request.resolver_match else None
        for pattern, route in self.routes.items():
            name = f"{namespace}:{route.name}" if namespace else route.name
            try:
                url_path = reverse(name)
            except NoReverseMatch:
                # Catch and ignore this so that we skip URLs which require
                # params (e.g. detail views)
                continue
            url = request.build_absolute_uri(url_path)
            index[name] = pydantic.HttpUrl(url)
        return APIResponse(index)

    def route[**P, R: HttpResponseBase](
        self,
        url_pattern: str,
        name: str,
        get: ViewFn[P, R] | None = None,
        post: ViewFn[P, R] | None = None,
        put: ViewFn[P, R] | None = None,
        patch: ViewFn[P, R] | None = None,
        delete: ViewFn[P, R] | None = None,
        decorators: Sequence[ViewDecorator] | None = None,
    ) -> Route:
        """Register a new route with the given URL pattern, view functions, and decorators."""
        _pattern = URLPatternStr(url_pattern)
        if _pattern in self.routes:
            raise ImproperlyConfigured(
                f"Cannot add route {_pattern} to router. Route already exists."
            )
        # Create route
        name = f"{self.basename}-{name}" if self.basename is not None else name
        route = Route(name, decorators=decorators, router_decorators=self.decorators)
        # Register any provided views
        views: dict[HttpMethod, ViewFn[P, R] | None] = {
            HttpMethod.GET: get,
            HttpMethod.POST: post,
            HttpMethod.PUT: put,
            HttpMethod.PATCH: patch,
            HttpMethod.DELETE: delete,
        }
        for method, view in views.items():
            if view is not None:
                route.register({method})(view)
        # Save and return the view
        self.routes[_pattern] = route
        return self.routes[_pattern]

    def register_resource[_ModelT: Model, _PKT](
        self,
        *,
        basename: str,
        list_pattern: str,
        detail_pattern: str,
        views: CRUDViews[_ModelT, _PKT],
        model: type[_ModelT] | None = None,
        list_permissions: Sequence[str] | None = None,
        detail_permissions: Sequence[str] | None = None,
        create_permissions: Sequence[str] | None = None,
        update_permissions: Sequence[str] | None = None,
        patch_permissions: Sequence[str] | None = None,
        delete_permissions: Sequence[str] | None = None,
        enable_list: bool = True,
        enable_detail: bool = True,
        enable_create: bool = True,
        enable_update: bool = True,
        enable_patch: bool = True,
        enable_delete: bool = True,
    ) -> tuple[Route | None, Route | None]:
        """Register CRUD views for a resource with automatic permission handling.

        Permission Resolution:
            When a permission parameter is None (not provided), permissions are
            inferred from Django's default model permissions using the model's
            app_label and model_name:
            - list_permissions: "{app_label}.view_{model_name}"
            - detail_permissions: "{app_label}.view_{model_name}"
            - create_permissions: "{app_label}.add_{model_name}"
            - update_permissions: "{app_label}.change_{model_name}"
            - patch_permissions: "{app_label}.change_{model_name}"
            - delete_permissions: "{app_label}.delete_{model_name}"

            To explicitly disable permission checks for an operation, pass an
            empty sequence (e.g., list_permissions=[]).

        Args:
            basename: Base name for URL route names (e.g., "user" -> "user-list")
            list_pattern: URL pattern for list/create endpoint
            detail_pattern: URL pattern for detail/update/delete endpoint
            views: CRUDViews NamedTuple from build_crud_resource_views
            model: Django model class for inferring default permissions. Required
                if any permission parameter is None.
            list_permissions: Permissions for GET list. None=infer, []=none
            detail_permissions: Permissions for GET detail. None=infer, []=none
            create_permissions: Permissions for POST. None=infer, []=none
            update_permissions: Permissions for PUT. None=infer, []=none
            patch_permissions: Permissions for PATCH. None=infer, []=none
            delete_permissions: Permissions for DELETE. None=infer, []=none
            enable_list: Whether to enable the list endpoint
            enable_detail: Whether to enable the detail endpoint
            enable_create: Whether to enable the create endpoint
            enable_update: Whether to enable the update endpoint
            enable_patch: Whether to enable the patch endpoint
            enable_delete: Whether to enable the delete endpoint

        Returns:
            Tuple of (list_route, detail_route), either may be None if disabled
        """

        def get_default_permission(action: str) -> list[str]:
            """Get default Django permission for an action (view/add/change/delete)."""
            if model is None:
                raise ImproperlyConfigured(
                    f"Cannot infer {action} permission: 'model' parameter is required "
                    "when permission parameters are None. Either provide the model "
                    "class or explicitly set permissions (use [] for no permissions)."
                )
            app_label = model._meta.app_label
            model_name = model._meta.model_name
            return [f"{app_label}.{action}_{model_name}"]

        def resolve_permissions(
            explicit: Sequence[str] | None,
            action: str,
        ) -> Sequence[str]:
            """Resolve permissions: explicit value, or infer from model."""
            if explicit is not None:
                return explicit
            return get_default_permission(action)

        def wrap_with_permissions(
            view: Callable[..., HttpResponseBase] | None,
            perms: Sequence[str],
        ) -> Callable[..., HttpResponseBase] | None:
            """Wrap a view with permission_required decorators."""
            if view is None:
                return None
            if not perms:
                return view
            result = view
            for perm in reversed(perms):
                result = permission_required(perm, raise_exception=True)(result)
            return result

        # Resolve all permissions (infer from model if None)
        resolved_list_perms = resolve_permissions(list_permissions, "view")
        resolved_detail_perms = resolve_permissions(detail_permissions, "view")
        resolved_create_perms = resolve_permissions(create_permissions, "add")
        resolved_update_perms = resolve_permissions(update_permissions, "change")
        resolved_patch_perms = resolve_permissions(patch_permissions, "change")
        resolved_delete_perms = resolve_permissions(delete_permissions, "delete")

        list_route: Route | None = None
        if enable_list or (enable_create and views.create_view):
            list_route = self.route(
                list_pattern,
                name=f"{basename}-list",
                get=(
                    wrap_with_permissions(views.list_view, resolved_list_perms)
                    if enable_list
                    else None
                ),
                post=(
                    wrap_with_permissions(views.create_view, resolved_create_perms)
                    if (enable_create and views.create_view)
                    else None
                ),
            )

        detail_route: Route | None = None
        if (
            enable_detail
            or (enable_update and views.update_view)
            or (enable_patch and views.patch_view)
            or enable_delete
        ):
            detail_route = self.route(
                detail_pattern,
                name=f"{basename}-detail",
                get=(
                    wrap_with_permissions(views.detail_view, resolved_detail_perms)
                    if enable_detail
                    else None
                ),
                put=(
                    wrap_with_permissions(views.update_view, resolved_update_perms)
                    if enable_update and views.update_view
                    else None
                ),
                patch=(
                    wrap_with_permissions(views.patch_view, resolved_patch_perms)
                    if enable_patch and views.patch_view
                    else None
                ),
                delete=(
                    wrap_with_permissions(views.delete_view, resolved_delete_perms)
                    if enable_delete
                    else None
                ),
            )

        return (list_route, detail_route)

    @property
    def urls(self) -> list[URLPattern]:
        """Get Django URLPattern objects for all registered routes."""
        return [
            path(pattern, route.view, name=route.name)
            for pattern, route in self.routes.items()
        ]
