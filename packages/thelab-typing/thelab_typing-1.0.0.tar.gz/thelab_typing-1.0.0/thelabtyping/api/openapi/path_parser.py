from dataclasses import dataclass
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class PathParam:
    name: str
    django_type: str
    openapi_type: str
    openapi_format: str | None


# Map Django path converter types to OpenAPI types and formats
DJANGO_TO_OPENAPI_TYPES: dict[str, tuple[str, str | None]] = {
    "int": ("integer", None),
    "str": ("string", None),
    "slug": ("string", None),
    "uuid": ("string", "uuid"),
    "path": ("string", None),
}

# Base values for placeholder generation (used to avoid collision with real IDs)
PLACEHOLDER_INT_BASE = 1000000
PLACEHOLDER_UUID_PREFIX = "00000000-0000-0000-0000-"
PLACEHOLDER_SLUG_BASE = "placeholder-slug"
PLACEHOLDER_PATH_BASE = "placeholder/path"
PLACEHOLDER_STR_BASE = "__placeholder__"

# Regex to match Django path parameter syntax: <type:name> or <name>
DJANGO_PATH_PARAM_PATTERN = re.compile(r"<(?:(?P<type>\w+):)?(?P<name>\w+)>")


def parse_django_path_params(pattern: str) -> list[PathParam]:
    """Convert Django URL pattern to OpenAPI path format."""
    params: list[PathParam] = []
    for match in DJANGO_PATH_PARAM_PATTERN.finditer(pattern):
        param_type = match.group("type") or "str"
        param_name = match.group("name")
        if param_type not in DJANGO_TO_OPENAPI_TYPES:
            logger.warning(
                "Unknown Django path converter type '%s' for parameter '%s'. "
                "Defaulting to OpenAPI type 'string'. "
                "Known types: %s",
                param_type,
                param_name,
                ", ".join(DJANGO_TO_OPENAPI_TYPES.keys()),
            )
            openapi_type, openapi_format = "string", None
        else:
            openapi_type, openapi_format = DJANGO_TO_OPENAPI_TYPES[param_type]
        params.append(
            PathParam(
                name=param_name,
                django_type=param_type,
                openapi_type=openapi_type,
                openapi_format=openapi_format,
            )
        )
    return params


def get_placeholder_kwargs(pattern: str) -> dict[str, str | int]:
    """Generate placeholder kwargs for reverse() from a Django URL pattern."""
    kwargs: dict[str, str | int] = {}
    # Track unique placeholder offsets by type to avoid collisions
    type_counters: dict[str, int] = {}

    for match in DJANGO_PATH_PARAM_PATTERN.finditer(pattern):
        param_type = match.group("type") or "str"
        param_name = match.group("name")

        # Get or initialize counter for this type
        counter = type_counters.get(param_type, 0)
        type_counters[param_type] = counter + 1

        # Generate unique placeholder based on type and counter
        if param_type == "int":
            # Use large base numbers that won't collide with real IDs
            kwargs[param_name] = PLACEHOLDER_INT_BASE + counter
        elif param_type == "uuid":
            # Generate unique UUIDs with proper 12-digit suffix padding
            kwargs[param_name] = f"{PLACEHOLDER_UUID_PREFIX}{counter:012d}"
        elif param_type == "slug":
            kwargs[param_name] = (
                f"{PLACEHOLDER_SLUG_BASE}-{counter}"
                if counter
                else PLACEHOLDER_SLUG_BASE
            )
        elif param_type == "path":
            kwargs[param_name] = (
                f"{PLACEHOLDER_PATH_BASE}/{counter}"
                if counter
                else PLACEHOLDER_PATH_BASE
            )
        else:
            # Default string type
            kwargs[param_name] = (
                f"{PLACEHOLDER_STR_BASE[:-2]}_{counter}__"
                if counter
                else PLACEHOLDER_STR_BASE
            )

    return kwargs


def replace_placeholders_with_openapi_params(
    url: str,
    placeholder_kwargs: dict[str, str | int],
) -> str:
    """Replace placeholder values in a reversed URL with OpenAPI parameter syntax."""
    result = url
    # Sort by placeholder value length (longest first) to avoid partial replacements
    # e.g., replace "00000000-0000-0000-0000-000000000000" before "0"
    sorted_items = sorted(
        placeholder_kwargs.items(),
        key=lambda item: len(str(item[1])),
        reverse=True,
    )
    for param_name, placeholder_value in sorted_items:
        # Replace the placeholder value with OpenAPI parameter syntax
        result = result.replace(str(placeholder_value), f"{{{param_name}}}")
    return result
