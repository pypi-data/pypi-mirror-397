"""Shared test fixtures for OpenAPI tests."""

from typing import Any
import json

from django.test import override_settings
from django.urls import include, path
import jsonschema
import pydantic

from thelabtyping.api.openapi.generator import (
    OpenAPIGenerator,
    OpenAPIGeneratorConfig,
    generate_openapi,
)
from thelabtyping.api.openapi.models import OpenAPI, Server
from thelabtyping.api.routing import Router


class QueryModel(pydantic.BaseModel):
    """Sample query model for tests."""

    search: str | None = None
    limit: int = 10


class BodyModel(pydantic.BaseModel):
    """Sample body model for tests."""

    name: str
    email: str


class ResponseModel(pydantic.BaseModel):
    """Sample response model for tests."""

    id: int
    name: str


class OpenAPITestMixin:
    """Mixin for tests that need to generate OpenAPI specs from test routers.

    Dynamically registers test routers in Django's URL config so that
    reverse() works correctly during OpenAPI generation.
    """

    def generate_openapi_for_test(
        self,
        router: Router,
        title: str = "Test API",
        version: str = "1.0.0",
        description: str | None = None,
        servers: list[Server] | None = None,
        namespace: str = "test",
    ) -> OpenAPI:
        """Generate OpenAPI spec after registering router in URL config."""

        class TestURLConf:
            urlpatterns = [
                path("test/", include((router.urls, namespace))),
            ]

        with override_settings(ROOT_URLCONF=TestURLConf):
            return generate_openapi(
                router,
                title=title,
                version=version,
                description=description,
                servers=servers,
                namespace=namespace,
            )

    def generate_openapi_with_config_for_test(
        self,
        router: Router,
        config: OpenAPIGeneratorConfig,
        namespace: str = "test",
    ) -> OpenAPI:
        """Generate OpenAPI spec with custom config after registering router."""

        class TestURLConf:
            urlpatterns = [
                path("test/", include((router.urls, namespace))),
            ]

        with override_settings(ROOT_URLCONF=TestURLConf):
            generator = OpenAPIGenerator(config)
            return generator.generate(router, namespace=namespace)

    def validate_spec_for_test(
        self,
        router: Router,
        schema: dict[str, Any],
        namespace: str = "test",
        **kwargs: Any,
    ) -> None:
        """Generate OpenAPI spec and validate against JSON schema."""

        class TestURLConf:
            urlpatterns = [
                path("test/", include((router.urls, namespace))),
            ]

        with override_settings(ROOT_URLCONF=TestURLConf):
            spec = generate_openapi(
                router,
                title=kwargs.get("title", "Test API"),
                version=kwargs.get("version", "1.0.0"),
                description=kwargs.get("description"),
                servers=kwargs.get("servers"),
                namespace=namespace,
            )
            spec_data = json.loads(
                spec.model_dump_json(by_alias=True, exclude_none=True)
            )
            jsonschema.validate(spec_data, schema)
