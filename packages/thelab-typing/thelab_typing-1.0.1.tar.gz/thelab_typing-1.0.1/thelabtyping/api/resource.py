from collections.abc import Callable
from typing import NamedTuple

from django.db.models import Model, QuerySet
from django.http import HttpResponse, HttpResponseBase
from django.shortcuts import get_object_or_404

from ..result import Ok
from .pagination import PaginatedResponse, PaginationParams, paginate_queryset
from .requests import (
    EmptyTypedRequest,
    TypedRequestBody,
    TypedRequestQuery,
)
from .responses import APIResponse
from .serializers import APIObj, Empty
from .status import Status
from .views import validate

# Type aliases for view functions
type ViewFn = Callable[..., HttpResponseBase]

# Default pagination settings
DEFAULT_PAGE_SIZE = 100


class CRUDViews[_ModelT: Model, _PKT](NamedTuple):
    """Container for generated CRUD view functions."""

    list_view: ViewFn
    detail_view: ViewFn
    create_view: ViewFn | None
    update_view: ViewFn | None
    patch_view: ViewFn | None
    delete_view: ViewFn


def build_crud_resource_views[
    _ModelT: Model,
    _PKT,
    _ListFilters: PaginationParams,
](
    ModelKlass: type[_ModelT],
    pk_type: type[_PKT],
    ListFilters: type[_ListFilters],
    ReadSchema: type[APIObj[_ModelT]],
    CreateSchema: type[APIObj[_ModelT]] | None = None,
    UpdateSchema: type[APIObj[_ModelT]] | None = None,
    PatchSchema: type[APIObj[_ModelT]] | None = None,
    default_page_size: int = DEFAULT_PAGE_SIZE,
    get_queryset: Callable[
        [
            TypedRequestQuery[_ListFilters]
            | EmptyTypedRequest
            | TypedRequestBody[APIObj[_ModelT]]
        ],
        QuerySet[_ModelT],
    ]
    | None = None,
    filter_queryset: Callable[
        [TypedRequestQuery[_ListFilters], QuerySet[_ModelT]],
        QuerySet[_ModelT],
    ]
    | None = None,
    sort_queryset: Callable[
        [TypedRequestQuery[_ListFilters], QuerySet[_ModelT]],
        QuerySet[_ModelT],
    ]
    | None = None,
    get_object: Callable[
        [
            EmptyTypedRequest | TypedRequestBody[APIObj[_ModelT]],
            QuerySet[_ModelT],
            _PKT,
        ],
        _ModelT,
    ]
    | None = None,
) -> CRUDViews[_ModelT, _PKT]:
    """
    Build type-safe CRUD views for a Django model.

    All schema types must be APIObj[_ModelT] - mypy enforces this at call site.

    Args:
        ModelKlass: The Django model class
        pk_type: The type of the primary key (int, str, etc.)
        ListFilters: Pydantic model for list view query parameters
        ReadSchema: APIObj subclass for serializing model instances
        CreateSchema: APIObj subclass for create request bodies (optional)
        UpdateSchema: APIObj subclass for PUT request bodies (optional)
        PatchSchema: APIObj subclass for PATCH request bodies (optional)
        default_page_size: Default number of items per page
        get_queryset: Custom queryset function (defaults to ModelKlass.objects.all()).
            Used by all views (list, detail, update, patch, delete).
        filter_queryset: Optional function to filter the queryset for list view only.
            Receives the typed request with validated query params and base queryset.
        sort_queryset: Custom function to sort the queryset for list view only.
            Receives the typed request with validated query params and base queryset.
            Defaults to ordering by pk.
        get_object: Custom function to retrieve a single object for detail views.
            Receives the typed request, base queryset, and lookup value.
            Should raise Http404 if object not found. Defaults to
            get_object_or_404(queryset, pk=lookup_value).

    Returns:
        CRUDViews NamedTuple with all generated view functions
    """

    # Default queryset function. Uses _default_manager instead of .objects to
    # respect any custom default managers defined on the model (e.g., managers
    # that filter soft-deleted records or scope to the current tenant).
    def default_get_queryset(
        request: TypedRequestQuery[_ListFilters]
        | EmptyTypedRequest
        | TypedRequestBody[APIObj[_ModelT]],
    ) -> QuerySet[_ModelT]:
        return ModelKlass._default_manager.all()

    # Default sort function. Orders by pk for consistent pagination.
    def default_sort_queryset(
        request: TypedRequestQuery[_ListFilters],
        queryset: QuerySet[_ModelT],
    ) -> QuerySet[_ModelT]:
        return queryset.order_by("pk")

    # Default object lookup function. Uses pk field for lookups.
    def default_get_object(
        request: EmptyTypedRequest | TypedRequestBody[APIObj[_ModelT]],
        queryset: QuerySet[_ModelT],
        pk: _PKT,
    ) -> _ModelT:
        return get_object_or_404(queryset, pk=pk)

    _get_queryset = get_queryset or default_get_queryset
    _sort_queryset = sort_queryset or default_sort_queryset
    _get_object = get_object or default_get_object

    # -------------------------------------------------------------------------
    # List View
    # -------------------------------------------------------------------------
    @validate(query_model=ListFilters)
    def list_view(
        request: TypedRequestQuery[_ListFilters],
    ) -> HttpResponse:
        """List all objects with pagination."""
        params = request.validated_querystring
        qs = _get_queryset(request)
        qs = _sort_queryset(request, qs)
        if filter_queryset is not None:
            qs = filter_queryset(request, qs)

        paginated_qs, total_count, next_url, prev_url = paginate_queryset(
            request=request,
            queryset=qs,
            page=params.page,
            page_size=params.page_size or default_page_size,
        )

        objs, errs = ReadSchema.list_from_django(request, paginated_qs)
        results = list(objs.root)

        # Adjust count to reflect actual serialized results, not raw queryset count.
        # Objects that fail serialization are logged by list_from_django but omitted
        # from results. The count should match what the client actually receives.
        dropped_count = len(errs)
        adjusted_count = total_count - dropped_count

        response = PaginatedResponse(
            count=adjusted_count,
            next=next_url,
            previous=prev_url,
            results=results,
        )
        return APIResponse(Ok(response))

    # -------------------------------------------------------------------------
    # Detail View
    # -------------------------------------------------------------------------
    @validate()
    def detail_view(
        request: EmptyTypedRequest,
        pk: _PKT,
    ) -> HttpResponse:
        """Get a single object by lookup value."""
        qs = _get_queryset(request)
        obj = _get_object(request, qs, pk)
        result = ReadSchema.from_django(request, obj)
        return APIResponse(result)

    # -------------------------------------------------------------------------
    # Create View
    # -------------------------------------------------------------------------
    create_view: ViewFn | None = None
    if CreateSchema is not None:

        @validate(body_model=CreateSchema)
        def _create_view(
            request: TypedRequestBody[APIObj[_ModelT]],
        ) -> HttpResponse:
            """Create a new object."""
            create_result = request.validated_body.create(request)
            if create_result.is_err:
                return APIResponse(
                    create_result,
                    status=Status.HTTP_400_BAD_REQUEST,
                )
            result = ReadSchema.from_django(request, create_result.ok())
            if result.is_ok:
                return APIResponse(result, status=Status.HTTP_201_CREATED)
            return APIResponse(result)

        create_view = _create_view

    # -------------------------------------------------------------------------
    # Update View (PUT)
    # -------------------------------------------------------------------------
    update_view: ViewFn | None = None
    if UpdateSchema is not None:

        @validate(body_model=UpdateSchema)
        def _update_view(
            request: TypedRequestBody[APIObj[_ModelT]],
            pk: _PKT,
        ) -> HttpResponse:
            """Update an existing object (full replacement)."""
            qs = _get_queryset(request)
            obj = _get_object(request, qs, pk)
            update_result = request.validated_body.update(request, obj)
            if update_result.is_err:
                return APIResponse(
                    update_result,
                    status=Status.HTTP_400_BAD_REQUEST,
                )
            result = ReadSchema.from_django(request, update_result.ok())
            return APIResponse(result)

        update_view = _update_view

    # -------------------------------------------------------------------------
    # Patch View (PATCH)
    # -------------------------------------------------------------------------
    patch_view: ViewFn | None = None
    if PatchSchema is not None:

        @validate(body_model=PatchSchema)
        def _patch_view(
            request: TypedRequestBody[APIObj[_ModelT]],
            pk: _PKT,
        ) -> HttpResponse:
            """Partially update an existing object."""
            qs = _get_queryset(request)
            obj = _get_object(request, qs, pk)
            patch_result = request.validated_body.patch(request, obj)
            if patch_result.is_err:
                return APIResponse(
                    patch_result,
                    status=Status.HTTP_400_BAD_REQUEST,
                )
            result = ReadSchema.from_django(request, patch_result.ok())
            return APIResponse(result)

        patch_view = _patch_view

    # -------------------------------------------------------------------------
    # Delete View
    # -------------------------------------------------------------------------
    @validate()
    def delete_view(
        request: EmptyTypedRequest,
        pk: _PKT,
    ) -> HttpResponse:
        """Delete an object."""
        qs = _get_queryset(request)
        obj = _get_object(request, qs, pk)
        obj.delete()
        return APIResponse(Ok(Empty()), status=Status.HTTP_204_NO_CONTENT)

    return CRUDViews(
        list_view=list_view,
        detail_view=detail_view,
        create_view=create_view,
        update_view=update_view,
        patch_view=patch_view,
        delete_view=delete_view,
    )
