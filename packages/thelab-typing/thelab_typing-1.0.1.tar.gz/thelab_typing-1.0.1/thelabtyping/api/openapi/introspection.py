"""Type introspection utilities for extracting OpenAPI schema info from views."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, get_args, get_origin, get_type_hints
import logging

import pydantic

from ..requests import (
    AuthdEmptyTypedRequest,
    AuthdTypedRequest,
    AuthdTypedRequestBody,
    AuthdTypedRequestQuery,
    EmptyTypedRequest,
    TypedRequest,
    TypedRequestBody,
    TypedRequestQuery,
)
from ..responses import APIResponse
from ..serializers import Empty

logger = logging.getLogger(__name__)


def _safe_cast_to_model(
    value: Any,
) -> type[pydantic.BaseModel] | None:
    """Safely cast a type argument to a Pydantic BaseModel subclass."""
    if value is None:
        return None
    if isinstance(value, type) and issubclass(value, pydantic.BaseModel):
        return value
    logger.warning(
        "Expected BaseModel subclass, got %s. Ignoring type argument.",
        type(value).__name__,
    )
    return None


@dataclass
class ViewTypeInfo:
    """Extracted type information from a view function."""

    querystring_model: type[pydantic.BaseModel] | None
    body_model: type[pydantic.BaseModel] | None
    response_model: type[pydantic.BaseModel] | None
    requires_auth: bool


def is_empty_model(model: type[pydantic.BaseModel] | None) -> bool:
    """Check if a model is the Empty sentinel model or None."""
    return model is None or model is Empty


def _normalize_model(
    model: type[pydantic.BaseModel] | None,
) -> type[pydantic.BaseModel] | None:
    """Return None if model is Empty, otherwise return the model."""
    if is_empty_model(model):
        return None
    return model


def _infer_request_types(
    request_type: type[Any] | None,
) -> tuple[type[pydantic.BaseModel] | None, type[pydantic.BaseModel] | None, bool]:
    """Extract query model, body model, and auth requirement from request type."""
    if request_type is None:
        return None, None, False

    origin = get_origin(request_type)
    if origin is None:
        origin = request_type
    args = get_args(request_type)

    # Auth-required types
    if origin is AuthdEmptyTypedRequest:
        return None, None, True

    if origin is AuthdTypedRequestQuery:
        qs_model = _safe_cast_to_model(args[0]) if args else None
        return _normalize_model(qs_model), None, True

    if origin is AuthdTypedRequestBody:
        body_model = _safe_cast_to_model(args[0]) if args else None
        return None, _normalize_model(body_model), True

    if origin is AuthdTypedRequest:
        qs_model = _safe_cast_to_model(args[0]) if len(args) > 0 else None
        body_model = _safe_cast_to_model(args[1]) if len(args) > 1 else None
        return _normalize_model(qs_model), _normalize_model(body_model), True

    # Auth-not-required types
    if origin is EmptyTypedRequest:
        return None, None, False

    if origin is TypedRequestQuery:
        qs_model = _safe_cast_to_model(args[0]) if args else None
        return _normalize_model(qs_model), None, False

    if origin is TypedRequestBody:
        body_model = _safe_cast_to_model(args[0]) if args else None
        return None, _normalize_model(body_model), False

    if origin is TypedRequest:
        qs_model = _safe_cast_to_model(args[0]) if len(args) > 0 else None
        body_model = _safe_cast_to_model(args[1]) if len(args) > 1 else None
        return _normalize_model(qs_model), _normalize_model(body_model), False

    # Unknown request type - return defaults
    return None, None, False


def _extract_response_model(
    return_type: type[Any] | None,
) -> type[pydantic.BaseModel] | None:
    """Extract the model type T from APIResponse[T]."""
    if return_type is None:
        return None

    origin = get_origin(return_type)
    if origin is not APIResponse:
        return None

    args = get_args(return_type)
    if not args:
        return None

    response_type = args[0]

    # Handle generic types like ListOf[T] which are subscripted generics
    response_origin = get_origin(response_type)
    if response_origin is not None:
        # It's a generic like ListOf[T] - return the subscripted generic itself
        # This preserves type info for schema generation
        if hasattr(response_type, "__mro__") or hasattr(response_origin, "__mro__"):
            # Check if it's Empty
            inner_args = get_args(response_type)
            if inner_args and inner_args[0] is Empty:
                return None
            # Return the generic origin class (e.g., ListOf)
            # The actual type info will be handled by Pydantic's model_json_schema
            return response_type  # type: ignore[no-any-return]

    # Check if it's a concrete Pydantic model
    if isinstance(response_type, type) and issubclass(
        response_type, pydantic.BaseModel
    ):
        if is_empty_model(response_type):
            return None
        return response_type

    return None


def infer_view_types(fn: Callable[..., Any]) -> ViewTypeInfo:
    """Extract type information from a view function's annotations."""
    try:
        hints = get_type_hints(fn)
    except (NameError, AttributeError, TypeError) as e:
        # Type hint resolution can fail due to:
        # - NameError: Forward references that can't be resolved
        # - AttributeError: Invalid type annotations
        # - TypeError: Invalid type hint syntax
        logger.warning(
            "Failed to resolve type hints for function %s: %s. "
            "OpenAPI schema will be incomplete.",
            getattr(fn, "__name__", fn),
            e,
        )
        return ViewTypeInfo(
            querystring_model=None,
            body_model=None,
            response_model=None,
            requires_auth=False,
        )

    request_type = hints.get("request")
    return_type = hints.get("return")

    qs_model, body_model, requires_auth = _infer_request_types(request_type)
    response_model = _extract_response_model(return_type)

    return ViewTypeInfo(
        querystring_model=qs_model,
        body_model=body_model,
        response_model=response_model,
        requires_auth=requires_auth,
    )
