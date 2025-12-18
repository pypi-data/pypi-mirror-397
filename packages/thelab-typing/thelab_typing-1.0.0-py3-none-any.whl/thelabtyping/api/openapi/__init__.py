"""OpenAPI 3.1 specification generation for thelab-typing Router."""

from dataclasses import dataclass, field
from typing import cast
import hashlib

from django.core.cache import cache
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden

from ..responses import APIResponse
from ..routing import Router
from .generator import OpenAPIGenerator, OpenAPIGeneratorConfig
from .models import OpenAPI, Server


@dataclass
class OpenAPISchema:
    """OpenAPI 3.1 schema generator that implements SchemaGenerator protocol."""

    title: str
    version: str
    description: str | None = None
    servers: list[Server] = field(default_factory=list)
    cache_timeout: int | None = 3600
    require_auth: bool = True

    def __call__(self, router: "Router", request: HttpRequest) -> HttpResponse:
        """Handle schema request - implements SchemaGenerator protocol."""
        # Check authentication first
        if self.require_auth:
            if (
                not hasattr(request, "user")
                or not request.user
                or request.user.is_anonymous
            ):
                return HttpResponseForbidden()

        # Auto-populate servers from request if not provided
        servers = self.servers
        if not servers:
            # Build server URL from request (scheme + host)
            base_url = request.build_absolute_uri("/").rstrip("/")
            servers = [Server(url=base_url)]

        # Get namespace from request for full path resolution
        namespace = request.resolver_match.namespace if request.resolver_match else None

        # Try to get cached response
        def _inner() -> OpenAPI:
            config = OpenAPIGeneratorConfig(
                title=self.title,
                version=self.version,
                description=self.description,
                servers=servers,
            )
            generator = OpenAPIGenerator(config)
            return generator.generate_from_routes(router.routes, namespace=namespace)

        cache_key = self._get_cache_key(router, servers, namespace)
        spec = cast(
            OpenAPI,
            cache.get_or_set(cache_key, _inner, timeout=self.cache_timeout)
            if self.cache_timeout is not None
            else _inner(),
        )
        return APIResponse(spec, exclude_none=True)

    def _get_cache_key(
        self,
        router: "Router",
        servers: list[Server],
        namespace: str | None,
    ) -> str:
        """Generate a cache key for the OpenAPI spec."""
        # Include all factors that affect the generated spec
        key_parts = [
            "openapi_schema",
            self.title,
            self.version,
            self.description or "",
            ",".join(s.url for s in servers),
            namespace or "",
            router.basename or "",
        ]
        key_data = "|".join(key_parts)
        return f"openapi:{hashlib.md5(key_data.encode(), usedforsecurity=False).hexdigest()}"
