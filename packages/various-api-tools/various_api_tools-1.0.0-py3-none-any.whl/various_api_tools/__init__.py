"""A package for various API utility tools.

Including JSON and Pydantic error translators.
"""

from .translators.json import JSONDecodeErrorTranslator
from .translators.psycopg.psycopg import PsycopgErrorTranslator
from .translators.psycopg.psycopg2 import Psycopg2ErrorTranslator
from .translators.pydantic import PydanticValidationErrorTranslator
from .validators.pydantic.constants import PYDANTIC_ERROR_TYPES
from .validators.pydantic.utils import (
    email_validator,
    latitude_validator,
    longitude_validator,
    optional_string_validator,
    strip_validator,
    validate_required_field,
)

__all__ = (
    "PYDANTIC_ERROR_TYPES",
    "JSONDecodeErrorTranslator",
    "Psycopg2ErrorTranslator",
    "PsycopgErrorTranslator",
    "PydanticValidationErrorTranslator",
    "email_validator",
    "latitude_validator",
    "longitude_validator",
    "optional_string_validator",
    "strip_validator",
    "validate_required_field",
)
