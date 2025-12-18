"""Tests for type introspection utilities."""

from unittest import TestCase

from django.http import HttpResponse

from thelabtyping.abc import ListOf
from thelabtyping.api.openapi.introspection import (
    infer_view_types,
    is_empty_model,
)
from thelabtyping.api.requests import (
    AuthdEmptyTypedRequest,
    AuthdTypedRequest,
    AuthdTypedRequestBody,
    AuthdTypedRequestQuery,
    EmptyTypedRequest,
    TypedRequest,
    TypedRequestBody,
    TypedRequestQuery,
)
from thelabtyping.api.responses import APIResponse
from thelabtyping.api.serializers import Empty

from .conftest import BodyModel, QueryModel, ResponseModel


class TestIsEmptyModel(TestCase):
    def test_empty_is_empty(self) -> None:
        """Empty model is identified as empty."""
        self.assertTrue(is_empty_model(Empty))

    def test_none_is_empty(self) -> None:
        """None is considered empty."""
        self.assertTrue(is_empty_model(None))

    def test_other_model_not_empty(self) -> None:
        """Other Pydantic models are not empty."""
        self.assertFalse(is_empty_model(QueryModel))
        self.assertFalse(is_empty_model(BodyModel))


class TestInferViewTypesEmptyRequest(TestCase):
    def test_empty_typed_request(self) -> None:
        """EmptyTypedRequest has no query or body models."""

        def view(request: EmptyTypedRequest) -> APIResponse[Empty]:
            return APIResponse(Empty())

        info = infer_view_types(view)
        self.assertIsNone(info.querystring_model)
        self.assertIsNone(info.body_model)
        self.assertFalse(info.requires_auth)

    def test_authd_empty_typed_request(self) -> None:
        """AuthdEmptyTypedRequest requires auth but has no models."""

        def view(request: AuthdEmptyTypedRequest) -> APIResponse[Empty]:
            return APIResponse(Empty())

        info = infer_view_types(view)
        self.assertIsNone(info.querystring_model)
        self.assertIsNone(info.body_model)
        self.assertTrue(info.requires_auth)


class TestInferViewTypesQueryRequest(TestCase):
    def test_typed_request_query(self) -> None:
        """TypedRequestQuery extracts query model."""

        def view(request: TypedRequestQuery[QueryModel]) -> APIResponse[Empty]:
            return APIResponse(Empty())

        info = infer_view_types(view)
        self.assertEqual(info.querystring_model, QueryModel)
        self.assertIsNone(info.body_model)
        self.assertFalse(info.requires_auth)

    def test_authd_typed_request_query(self) -> None:
        """AuthdTypedRequestQuery extracts query model and requires auth."""

        def view(request: AuthdTypedRequestQuery[QueryModel]) -> APIResponse[Empty]:
            return APIResponse(Empty())

        info = infer_view_types(view)
        self.assertEqual(info.querystring_model, QueryModel)
        self.assertIsNone(info.body_model)
        self.assertTrue(info.requires_auth)


class TestInferViewTypesBodyRequest(TestCase):
    def test_typed_request_body(self) -> None:
        """TypedRequestBody extracts body model."""

        def view(request: TypedRequestBody[BodyModel]) -> APIResponse[Empty]:
            return APIResponse(Empty())

        info = infer_view_types(view)
        self.assertIsNone(info.querystring_model)
        self.assertEqual(info.body_model, BodyModel)
        self.assertFalse(info.requires_auth)

    def test_authd_typed_request_body(self) -> None:
        """AuthdTypedRequestBody extracts body model and requires auth."""

        def view(request: AuthdTypedRequestBody[BodyModel]) -> APIResponse[Empty]:
            return APIResponse(Empty())

        info = infer_view_types(view)
        self.assertIsNone(info.querystring_model)
        self.assertEqual(info.body_model, BodyModel)
        self.assertTrue(info.requires_auth)


class TestInferViewTypesFullRequest(TestCase):
    def test_typed_request(self) -> None:
        """TypedRequest extracts both query and body models."""

        def view(
            request: TypedRequest[QueryModel, BodyModel],
        ) -> APIResponse[ResponseModel]:
            return APIResponse(ResponseModel(id=1, name="test"))

        info = infer_view_types(view)
        self.assertEqual(info.querystring_model, QueryModel)
        self.assertEqual(info.body_model, BodyModel)
        self.assertFalse(info.requires_auth)

    def test_authd_typed_request(self) -> None:
        """AuthdTypedRequest extracts both models and requires auth."""

        def view(
            request: AuthdTypedRequest[QueryModel, BodyModel],
        ) -> APIResponse[ResponseModel]:
            return APIResponse(ResponseModel(id=1, name="test"))

        info = infer_view_types(view)
        self.assertEqual(info.querystring_model, QueryModel)
        self.assertEqual(info.body_model, BodyModel)
        self.assertTrue(info.requires_auth)


class TestInferViewTypesResponse(TestCase):
    def test_api_response_model(self) -> None:
        """APIResponse[T] extracts response model."""

        def view(request: EmptyTypedRequest) -> APIResponse[ResponseModel]:
            return APIResponse(ResponseModel(id=1, name="test"))

        info = infer_view_types(view)
        self.assertEqual(info.response_model, ResponseModel)

    def test_api_response_list_of(self) -> None:
        """APIResponse[ListOf[T]] extracts ListOf response model."""

        def view(request: EmptyTypedRequest) -> APIResponse[ListOf[ResponseModel]]:
            return APIResponse(ListOf[ResponseModel]([]))

        info = infer_view_types(view)
        # ListOf is a generic alias, but we should get the actual type
        self.assertIsNotNone(info.response_model)

    def test_api_response_empty(self) -> None:
        """APIResponse[Empty] has no response model."""

        def view(request: EmptyTypedRequest) -> APIResponse[Empty]:
            return APIResponse(Empty())

        info = infer_view_types(view)
        # Empty is the response model, but we treat it as None
        self.assertIsNone(info.response_model)


class TestInferViewTypesEdgeCases(TestCase):
    def test_function_with_path_params(self) -> None:
        """Function with path parameters still works."""

        def view(
            request: TypedRequestQuery[QueryModel], pk: int
        ) -> APIResponse[ResponseModel]:
            return APIResponse(ResponseModel(id=pk, name="test"))

        info = infer_view_types(view)
        self.assertEqual(info.querystring_model, QueryModel)
        self.assertEqual(info.response_model, ResponseModel)

    def test_unannotated_request(self) -> None:
        """Function without request type hint returns empty info."""

        def view(request) -> HttpResponse:  # type: ignore[no-untyped-def]
            return HttpResponse()

        info = infer_view_types(view)
        self.assertIsNone(info.querystring_model)
        self.assertIsNone(info.body_model)
        self.assertFalse(info.requires_auth)

    def test_non_api_response_return(self) -> None:
        """Function with non-APIResponse return has no response model."""

        def view(request: EmptyTypedRequest) -> HttpResponse:
            return HttpResponse()

        info = infer_view_types(view)
        self.assertIsNone(info.response_model)
