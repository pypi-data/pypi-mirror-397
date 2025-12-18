from __future__ import annotations

from typing import Annotated
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from django.db.models import Model, QuerySet
from django.http import HttpRequest
import pydantic

# Maximum allowed page size to prevent excessive memory usage
MAX_PAGE_SIZE = 1000


class PaginationParams(pydantic.BaseModel):
    """Default pagination query parameters.

    Validation:
        - page: Must be >= 1 (1-indexed pagination)
        - page_size: Must be >= 1 and <= MAX_PAGE_SIZE (1000) when provided
    """

    page: Annotated[int, pydantic.Field(ge=1)] = 1
    page_size: Annotated[int | None, pydantic.Field(ge=1, le=MAX_PAGE_SIZE)] = None


class PaginatedResponse[T](pydantic.BaseModel):
    """Paginated API response with count, next/previous URLs, and results."""

    count: int
    next: str | None
    previous: str | None
    results: list[T]


def paginate_queryset[_ModelT: Model](
    request: HttpRequest,
    queryset: QuerySet[_ModelT],
    page: int,
    page_size: int,
) -> tuple[QuerySet[_ModelT], int, str | None, str | None]:
    """
    Paginate a queryset and return pagination metadata.

    Args:
        request: The HTTP request (used for building URLs)
        queryset: The queryset to paginate
        page: The page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple of (paginated_queryset, total_count, next_url, previous_url)
    """
    # Get total count
    count = queryset.count()

    # Calculate offset
    offset = (page - 1) * page_size

    # Slice queryset
    paginated_qs = queryset[offset : offset + page_size]

    # Calculate if there are more pages
    has_next = offset + page_size < count
    has_previous = page > 1

    # Build next/previous URLs
    next_url = _build_page_url(request, page + 1) if has_next else None
    previous_url = _build_page_url(request, page - 1) if has_previous else None

    return paginated_qs, count, next_url, previous_url


def _build_page_url(request: HttpRequest, page: int) -> str:
    """Build a URL for a specific page, preserving other query parameters."""
    # Parse the current URL
    parsed = urlparse(request.get_full_path())

    # Parse existing query parameters
    query_params = parse_qs(parsed.query)

    # Update the page parameter
    query_params["page"] = [str(page)]

    # Flatten the query params (parse_qs returns lists)
    flat_params = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}

    # Rebuild the URL
    new_query = urlencode(flat_params, doseq=True)
    new_parsed = parsed._replace(query=new_query)

    # Build absolute URL
    return request.build_absolute_uri(urlunparse(new_parsed))
