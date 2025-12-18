"""OpenAPI 3.1 specification Pydantic models."""

from typing import Any, Literal

import pydantic


class Contact(pydantic.BaseModel):
    """OpenAPI Contact Object.

    https://spec.openapis.org/oas/v3.1.0#contact-object
    """

    name: str | None = None
    url: pydantic.HttpUrl | None = None
    email: str | None = None


class License(pydantic.BaseModel):
    """OpenAPI License Object.

    https://spec.openapis.org/oas/v3.1.0#license-object
    """

    name: str
    identifier: str | None = None
    url: pydantic.HttpUrl | None = None


class Info(pydantic.BaseModel):
    """OpenAPI Info Object.

    https://spec.openapis.org/oas/v3.1.0#info-object
    """

    title: str
    version: str
    summary: str | None = None
    description: str | None = None
    termsOfService: pydantic.HttpUrl | None = None
    contact: Contact | None = None
    license: License | None = None


class Server(pydantic.BaseModel):
    """OpenAPI Server Object.

    https://spec.openapis.org/oas/v3.1.0#server-object
    """

    url: str
    description: str | None = None


class ExternalDocumentation(pydantic.BaseModel):
    """OpenAPI External Documentation Object.

    https://spec.openapis.org/oas/v3.1.0#external-documentation-object
    """

    url: pydantic.HttpUrl
    description: str | None = None


class Reference(pydantic.BaseModel):
    """OpenAPI Reference Object.

    https://spec.openapis.org/oas/v3.1.0#reference-object
    """

    ref: str = pydantic.Field(serialization_alias="$ref")

    model_config = pydantic.ConfigDict(
        validate_by_name=True,
        validate_by_alias=False,
        serialize_by_alias=True,
    )


class MediaType(pydantic.BaseModel):
    """OpenAPI Media Type Object.

    https://spec.openapis.org/oas/v3.1.0#media-type-object
    """

    media_type_schema: dict[str, Any] | Reference | None = pydantic.Field(
        default=None, serialization_alias="schema"
    )

    model_config = pydantic.ConfigDict(
        validate_by_name=True,
        validate_by_alias=False,
        serialize_by_alias=True,
    )


class RequestBody(pydantic.BaseModel):
    """OpenAPI Request Body Object.

    https://spec.openapis.org/oas/v3.1.0#request-body-object
    """

    description: str | None = None
    content: dict[str, MediaType]
    required: bool = False


class Parameter(pydantic.BaseModel):
    """OpenAPI Parameter Object.

    https://spec.openapis.org/oas/v3.1.0#parameter-object
    """

    name: str
    param_in: Literal["query", "header", "path", "cookie"] = pydantic.Field(
        serialization_alias="in"
    )
    description: str | None = None
    required: bool = False
    deprecated: bool = False
    param_schema: dict[str, Any] | Reference | None = pydantic.Field(
        default=None, serialization_alias="schema"
    )

    model_config = pydantic.ConfigDict(
        validate_by_name=True,
        validate_by_alias=False,
        serialize_by_alias=True,
    )


class Response(pydantic.BaseModel):
    """OpenAPI Response Object.

    https://spec.openapis.org/oas/v3.1.0#response-object
    """

    description: str
    content: dict[str, MediaType] | None = None


class Operation(pydantic.BaseModel):
    """OpenAPI Operation Object.

    https://spec.openapis.org/oas/v3.1.0#operation-object
    """

    tags: list[str] | None = None
    summary: str | None = None
    description: str | None = None
    operationId: str | None = None
    parameters: list[Parameter | Reference] | None = None
    requestBody: RequestBody | Reference | None = None
    responses: dict[str, Response | Reference]
    deprecated: bool = False
    security: list[dict[str, list[str]]] | None = None


class PathItem(pydantic.BaseModel):
    """OpenAPI Path Item Object.

    https://spec.openapis.org/oas/v3.1.0#path-item-object
    """

    summary: str | None = None
    description: str | None = None
    get: Operation | None = None
    put: Operation | None = None
    post: Operation | None = None
    delete: Operation | None = None
    patch: Operation | None = None
    parameters: list[Parameter | Reference] | None = None


class SecurityScheme(pydantic.BaseModel):
    """OpenAPI Security Scheme Object.

    https://spec.openapis.org/oas/v3.1.0#security-scheme-object
    """

    type: Literal["apiKey", "http", "mutualTLS", "oauth2", "openIdConnect"]
    description: str | None = None
    name: str | None = None
    security_scheme_in: Literal["query", "header", "cookie"] | None = pydantic.Field(
        default=None, serialization_alias="in"
    )
    scheme: str | None = None
    bearerFormat: str | None = None

    model_config = pydantic.ConfigDict(
        validate_by_name=True,
        validate_by_alias=False,
        serialize_by_alias=True,
    )


class Components(pydantic.BaseModel):
    """OpenAPI Components Object.

    https://spec.openapis.org/oas/v3.1.0#components-object
    """

    schemas: dict[str, dict[str, Any]] | None = None
    securitySchemes: dict[str, SecurityScheme] | None = None


class Tag(pydantic.BaseModel):
    """OpenAPI Tag Object.

    https://spec.openapis.org/oas/v3.1.0#tag-object
    """

    name: str
    description: str | None = None
    externalDocs: ExternalDocumentation | None = None


class OpenAPI(pydantic.BaseModel):
    """OpenAPI 3.1 Document Root.

    https://spec.openapis.org/oas/v3.1.0#openapi-object
    """

    openapi: Literal["3.1.0"] = "3.1.0"
    info: Info
    servers: list[Server] | None = None
    paths: dict[str, PathItem]
    components: Components | None = None
    security: list[dict[str, list[str]]] | None = None
    tags: list[Tag] | None = None
    externalDocs: ExternalDocumentation | None = None
