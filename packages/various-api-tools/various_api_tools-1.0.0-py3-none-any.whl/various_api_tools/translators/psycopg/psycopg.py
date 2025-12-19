"""Translator implementation for psycopg3 (psycopg) database errors.

This module provides a concrete implementation of `BasePsycopgTranslator` tailored
for `psycopg` (aka psycopg3) exceptions.
It extracts error details using psycopg3's exception interface:
- `sqlstate`: the SQLSTATE code (e.g. '23505' for unique violation)
- `str(error)`: the full error message, as psycopg3 does not expose `pgerror` directly
"""

from typing import Any

from .base import BasePsycopgTranslator


class PsycopgErrorTranslator(BasePsycopgTranslator):
    """Concrete error translator for psycopg (psycopg3) exceptions.

    Implements the `_get_pgcode` and `_get_pgerror` methods to extract error details
    from `psycopg` exception objects:
    - Uses `.sqlstate` attribute for SQLSTATE code (psycopg3 equivalent of pgcode)
    - Uses `str(error)` as the error message, since psycopg3 does not expose `.pgerror`

    Supports customization via:
    - `code_map`: mapping of SQLSTATE codes to user-facing messages
    - `check_map`: mapping of check constraint names to human-readable descriptions

    Usage:
        translator = PsycopgErrorTranslator(
            code_map={"23505": "Значение уже существует"},
            check_map={"users_age_check": "Возраст должен быть от 18 до 120"}
        )

    Note:
        This class is intended for use with `psycopg` >= 3.0. For `psycopg2`, use
        `Psycopg2ErrorTranslator` instead.

    """

    def _get_pgcode(self, error: Any) -> str | None:
        return getattr(error, "sqlstate", None)

    def _get_pgerror(self, error: Any) -> str | None:
        return str(error)
