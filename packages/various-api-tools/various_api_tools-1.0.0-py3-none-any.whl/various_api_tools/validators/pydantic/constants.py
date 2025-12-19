"""Module: Pydantic Validator Constants.

This module defines constants used across Pydantic-based
validators in the application.
It includes:
- Geographical coordinate boundaries (latitude and longitude limits)
- A centralized mapping of error codes to localized human-readable
messages (`PYDANTIC_ERROR_TYPES`)
- Default error message for unknown validation issues (`UNKNOWN_ERROR_TYPE`)
"""

from typing import Final

MIN_LATITUDE: Final[float] = -90.0
"""Minimum allowed latitude value in degrees (-90.0 corresponds to the South Pole).

Used in geographic validation to ensure latitude values are within valid range.
See: `latitude_validator` in `utils.py`."""

MAX_LATITUDE: Final[float] = 90.0
"""Maximum allowed latitude value in degrees (90.0 corresponds to the North Pole).

Used in geographic validation to ensure latitude values are within valid range.
See: `latitude_validator` in `utils.py`."""

MIN_LONGITUDE: Final[float] = -180.0
"""Minimum allowed longitude value in degrees (-180.0 corresponds to the IDL).

Used in geographic validation to ensure longitude values are within valid range.
See: `longitude_validator` in `utils.py`."""

MAX_LONGITUDE: Final[float] = 180.0
"""Maximum allowed longitude value in degrees (180.0 corresponds to the IDL).

Used in geographic validation to ensure longitude values are within valid range.
See: `longitude_validator` in `utils.py`."""

PYDANTIC_ERROR_TYPES: dict[str, str] = {
    "missing": "Не заполнено обязательное поле",
    "uuid_parsing": "Невалидное значение для UUID",
    "uuid_type": "Невалидное значение для UUID",
    "uuid_version": "Невалидное значение для UUID",
    "bool_parsing": "Невалидное значение для логического типа(bool)",
    "bool_type": "Невалидное значение для логического типа(bool)",
    "date_type": "Невалидное значение даты(date)",
    "datetime_from_date_parsing": "Невалидное значение даты и времени(datetime)",
    "datetime_type": "Невалидное значение даты и времени(datetime)",
    "dict_type": "Невалидное значение словаря",
    "list_type": "Невалидное значение списка",
    "string_type": "Невалидное строковое значение(str)",
    "enum": "Невалидное значение Enum",
    "float_parsing": "Невалидное значение числа с плавающей точкой(float)",
    "float_type": "Невалидное значение числа с плавающей точкой(float)",
    "int_from_float": "Невалидное значение для целочисленного числа(int)",
    "int_parsing": "Невалидное значение для целочисленного числа(int)",
    "int_parsing_size": "Невалидное значение для целочисленного числа(int)",
    "int_type": "Невалидное значение для целочисленного числа(int)",
    "non_negative_int": "Невалидное значение для целочисленного числа(int), "
    "должно быть больше или равно 0",
    "incorrect_latitude": "Некорректное значение широты, должно быть больше, "
    "чем -90.0 и меньше, чем 90.0",
    "incorrect_longitude": "Некорректное значение долготы, должно быть больше, "
    "чем -180.0 и меньше, чем 180.0",
    "string_too_short": "Cтрока слишком короткая",
    "ip_address": "Невалидное значение адреса IPv4/IPv6",
    "incorrect_email": "Невалидное значение email-адреса",
    "list_expected": "Некорректный тип данных. Ожидается список.",
}
"""Mapping of Pydantic built-in error codes to localized Russian messages.

Used by custom validators to provide consistent, user-friendly error descriptions
in API responses. Each key corresponds to a standard Pydantic error type.
Values are human-readable messages suitable for end users or frontend display.

Example keys:
- 'string_type': invalid type for string field
- 'incorrect_email': failed email format validation
- 'missing': required field is missing

Used in: `optional_string_validator`, `email_validator`, etc."""

UNKNOWN_ERROR_TYPE: Final[str] = "Неизвестная ошибка"
"""Default fallback message for validation errors with
no matching code in `PYDANTIC_ERROR_TYPES`.

Used when an unexpected or unrecognized error code is encountered during validation,
ensuring that no raw or technical messages are exposed to the user."""
