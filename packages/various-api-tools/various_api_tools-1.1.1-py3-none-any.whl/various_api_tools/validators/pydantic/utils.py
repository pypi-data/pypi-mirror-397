"""Utility functions for Pydantic-based data validation.

This module provides reusable validator functions designed to be used with
Pydantic models to enforce data consistency, formatting, and business rules.
These validators are particularly useful in API request/response handling
where user input requires strict sanitization and meaningful error reporting.

Features:
- String normalization (whitespace stripping, empty value handling)
- Email format validation using Pydantic's `EmailStr`
- Geographic coordinate validation (latitude and longitude ranges)
- Support for custom error messages via `error_types` dictionary
- Integration with Pydantic's `PydanticCustomError` for consistent error codes
"""

from decimal import Decimal
from typing import Any

from pydantic import EmailStr
from pydantic_core._pydantic_core import PydanticCustomError

from .constants import (
    MAX_LATITUDE,
    MAX_LONGITUDE,
    MIN_LATITUDE,
    MIN_LONGITUDE,
    PYDANTIC_ERROR_TYPES,
)


def strip_validator(value: str) -> str:
    """Strip whitespace from both ends of a string.

    Args:
        value: Input string to be stripped.

    Returns:
        The stripped string.

    Example:
        ```python
        print(PydanticValidator.strip_validator("  test  "))
        #> "test"
        ```

    """
    return value.strip()


def optional_string_validator(
    value: Any | None,
    *,
    error_types: dict | None = None,
) -> str | None:
    """Validate and strips an optional string value.

    Args:
        value: Input value to be validated.
        error_types: Optional dict mapping error codes to custom messages.
            If None, defaults to `PYDANTIC_ERROR_TYPES`.

    Returns:
        A stripped string or None if the value is empty.

    Raises:
        PydanticCustomError: If the value is not a string.

    Example:
        ```python
        print(PydanticValidator.optional_string_validator("  test  "))
        #> "test"

        print(PydanticValidator.optional_string_validator(""))
        #> None

        print(PydanticValidator.optional_string_validator(123))
        #> Traceback (most recent call last):
        #> ...
        #> PydanticCustomError: 'string_type'
        ```

    """
    if error_types is None:
        error_types = PYDANTIC_ERROR_TYPES

    if value is not None:
        if not isinstance(value, str):
            raise PydanticCustomError("string_type", error_types["string_type"])

        value = strip_validator(value=value)
        if value == "":
            value = None

    return value


def email_validator(value: str, *, error_types: dict | None = None) -> EmailStr | None:
    """Validate an email address format.

    Args:
        value: Input string to be validated as an email.
        error_types: Optional dict mapping error codes to custom messages.
            If None, defaults to `PYDANTIC_ERROR_TYPES`.

    Returns:
        Validated EmailStr object or None if input is invalid.

    Raises:
        PydanticCustomError: If the email format is incorrect.

    Example:
        ```python
        print(PydanticValidator.email_validator("test@example.com"))
        #> EmailStr('test@example.com')

        print(PydanticValidator.email_validator("invalid-email"))
        #> Traceback (most recent call last):
        #> ...
        #> PydanticCustomError: 'incorrect_email'
        ```

    """
    if error_types is None:
        error_types = PYDANTIC_ERROR_TYPES

    email_str: EmailStr | None = None
    stripped_value: str | None = optional_string_validator(value=value)

    if stripped_value is not None:
        try:
            email_str = EmailStr._validate(stripped_value)  # noqa SLF001
        except ValueError as exc:
            raise PydanticCustomError(
                "incorrect_email",
                error_types["incorrect_email"],
            ) from exc

    return email_str


def latitude_validator(value: Decimal, *, error_types: dict | None = None) -> Decimal:
    """Validate that a value is a valid geographic latitude.

    Args:
        value: Input Decimal to be validated.
        error_types: Optional dict mapping error codes to custom messages.
            If None, defaults to `PYDANTIC_ERROR_TYPES`.

    Returns:
        The validated Decimal value.

    Raises:
        PydanticCustomError: If the value is not in the range [-90.0, 90.0].

    Example:
        ```python
        print(PydanticValidator.latitude_validator(Decimal("45.0")))
        #> Decimal('45.0')

        print(PydanticValidator.latitude_validator(Decimal("100.0")))
        #> Traceback (most recent call last):
        #> ...
        #> PydanticCustomError: 'incorrect_latitude'
        ```

    """
    if error_types is None:
        error_types = PYDANTIC_ERROR_TYPES

    if not MIN_LATITUDE <= value <= MAX_LATITUDE:
        raise PydanticCustomError(
            "incorrect_latitude",
            error_types["incorrect_latitude"],
        )
    return value


def longitude_validator(value: Decimal, *, error_types: dict | None = None) -> Decimal:
    """Validate that a value is a valid geographic longitude.

    Args:
        value: Input Decimal to be validated.
        error_types: Optional dict mapping error codes to custom messages.
            If None, defaults to `PYDANTIC_ERROR_TYPES`.

    Returns:
        The validated Decimal value.

    Raises:
        PydanticCustomError: If the value is not in the range [-180.0, 180.0].

    Example:
        ```python
        print(PydanticValidator.longitude_validator(Decimal("90.0")))
        #> Decimal('90.0')

        print(PydanticValidator.longitude_validator(Decimal("200.0")))
        #> Traceback (most recent call last):
        #> ...
        #> PydanticCustomError: 'incorrect_longitude'
        ```

    """
    if error_types is None:
        error_types = PYDANTIC_ERROR_TYPES

    if not MIN_LONGITUDE <= value <= MAX_LONGITUDE:
        raise PydanticCustomError(
            "incorrect_longitude",
            error_types["incorrect_longitude"],
        )
    return value


def validate_required_field(
    value: Any | None,
    *,
    error_types: dict | None = None,
) -> Any:
    """Validate that a field is not missing in update models.

    Args:
        value: Input value to be validated.
        error_types: Optional dict mapping error codes to custom messages.
            If None, defaults to `PYDANTIC_ERROR_TYPES`.

    Returns:
        The original value if it's valid.

    Raises:
        PydanticCustomError: If the value is None or empty string.

    Example:
        ```python
        print(PydanticValidator.validate_required_field("test"))
        #> "test"

        print(PydanticValidator.validate_required_field(None))
        #> Traceback (most recent call last):
        #> ...
        #> PydanticCustomError: 'missing'
        ```

    """
    if error_types is None:
        error_types = PYDANTIC_ERROR_TYPES

    if isinstance(value, str):
        value = optional_string_validator(value=value)

    if value is None:
        raise PydanticCustomError("missing", error_types["missing"])

    return value
