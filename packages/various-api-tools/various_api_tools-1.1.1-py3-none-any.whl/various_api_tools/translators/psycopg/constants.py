"""Psycopg error translation constants.

This module defines constants used by the PsycopgErrorTranslator for parsing and
translating PostgreSQL error messages from psycopg and psycopg2 into user-friendly
localized messages.

The constants include:
- Regular expressions to extract structured details from PostgreSQL error texts
- Mappings from SQLSTATE codes to human-readable messages
- Default error descriptions for common constraint violations

These are primarily used to enhance error reporting in API responses by providing
clear, actionable feedback based on database-level constraints (e.g., unique,
foreign key, and check violations).
"""

from typing import Final

UNIQUE_VIOLATION_PATTERN: Final[str] = r"DETAIL:.*(Key|Ключ).*\((.*?)\)=\((.*?)\)"
"""Regex pattern to extract details from PostgreSQL unique constraint violation errors.

Matches the standard PostgreSQL error detail message format:
'DETAIL: Key (field)=(value) already exists.' or localized version 'Ключ'.

Captures:
    Group 1: 'Key' or 'Ключ' (language-independent match)
    Group 2: Column name involved in the constraint
    Group 3: Conflicting value

Used by: `BasePsycopgTranslator._translate_unique_violation`
Example match: 'DETAIL: Key (email)=(user@example.com) already exists.' →
key='email', value='user@example.com'"""

CHECK_VIOLATION_PATTERN: Final[str] = r'violates check constraint.*?"(.*?)"'
"""Regex pattern to extract the name of a violated check constraint from PSQL error.

Matches error messages containing: 'violates check constraint "constraint_name"'.
Captures the constraint name in group 1.

Used by: `BasePsycopgTranslator._translate_check_violation`
Example: 'new row for relation "users" violates check constraint "users_age_check"'
→ 'users_age_check'"""

UNKNOWN_CHECK_DESCRIPTION: Final[str] = "Невалидная запись в БД"
"""Fallback message used when a check constraint is violated but no custom description
is configured.

Used as the default value when a constraint name is not found in `check_map`.
Displayed to users when the system cannot provide more specific validation feedback."""

UNKNOWN_USER_RAISE_DESCRIPTION: Final[str] = "Невозможно выполнить операцию"
"""Default message shown when a custom database RAISE EXCEPTION is caught,
but no matching field or rule is found in `user_map`.

Used as a fallback in `BasePsycopgTranslator._translate_user_raise`
to avoid exposing raw internal messages to end users."""

USER_RAISE_KEY: Final[str] = "Ошибка БД"
"""Default display key used in error messages generated from RAISE EXCEPTION.

Used as a generic identifier when formatting user-facing errors from custom
database raises, especially when no specific field mapping is available.

Example: '{Ошибка БД}: {описание}'"""

DEFAULT_CODE_MAP: Final[dict[str, str]] = {
    "P0001": "Ошибка БД",
    "23503": "Указан несуществующий идентификатор связанного объекта",
    "23505": "БД уже содержит значение",
    "23514": "Нарушено ограничение данных",
}
"""Default mapping of PostgreSQL SQLSTATE codes to user-friendly Russian error messages.

Each key is a standardized SQLSTATE code:
    - "P0001" (raise_exception): Custom exception raised in PL/pgSQL
    - "23503" (foreign_key_violation): Referenced object does not exist
    - "23505" (unique_violation): Duplicate key value
    - "23514" (check_violation): Data fails check constraint

Values are localized messages suitable for API responses.
Can be overridden in translator instances for custom messaging."""

UNKNOWN_CODE: Final[str] = "Неизвестная ошибка БД"
"""Fallback message used when an unrecognized SQLSTATE code is encountered.

Ensures that no raw database error codes or technical messages are exposed to end users.
Should be replaced with more specific messages during
system localization or customization."""
