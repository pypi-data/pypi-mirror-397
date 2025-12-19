"""Translator implementation for psycopg2-specific database errors.

This module provides a concrete implementation of `BasePsycopgTranslator`
tailored for `psycopg2`exceptions.
It extracts error details using `psycopg2`'s attribute-based interface:
- `pgcode`: the SQLSTATE code (e.g. '23505' for unique violation)
- `pgerror`: the full error message from PostgreSQL
"""

from typing import Any

from .base import BasePsycopgTranslator


class Psycopg2ErrorTranslator(BasePsycopgTranslator):
    """Concrete error translator for psycopg2 exceptions.

    Implements the `_get_pgcode` and `_get_pgerror` methods to extract error details
    from `psycopg2` exception objects using their standard attributes.

    This class supports customization via:
    - `code_map`: mapping of SQLSTATE codes to user-friendly messages
    - `check_map`: mapping of check constraint names to descriptive texts

    Usage:
        translator = Psycopg2ErrorTranslator(
            code_map={"23505": "Значение уже существует"},
            check_map={"users_age_check": "Возраст должен быть от 18 до 120"}
        )
    """

    def _get_pgcode(self, error: Any) -> str | None:
        return getattr(error, "pgcode", None)

    def _get_pgerror(self, error: Any) -> str | None:
        return getattr(error, "pgerror", None)
