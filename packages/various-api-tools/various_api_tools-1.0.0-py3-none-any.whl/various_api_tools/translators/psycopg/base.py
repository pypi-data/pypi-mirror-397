"""Abstract base class for translating psycopg/psycopg2 database errors.

This module provides a foundation for parsing PostgreSQL error
details (such as `pgcode` and `pgerror`) from psycopg exceptions and converting
them into structured, human-readable error descriptions.
It supports both `psycopg2` and `psycopg3` by abstracting access to error attributes,
allowing concrete implementations to handle version-specific details.
"""

import re
from dataclasses import dataclass
from typing import Any

from .constants import (
    CHECK_VIOLATION_PATTERN,
    DEFAULT_CODE_MAP,
    UNIQUE_VIOLATION_PATTERN,
    UNKNOWN_CHECK_DESCRIPTION,
    UNKNOWN_CODE,
)


@dataclass
class ErrorData:
    """Represents structured data extracted from a database error.

    Used to capture constraint details such as the violated field and
    its conflicting value.

    Attributes:
        key: The name of the field or constraint involved in the error.
        value: The value that caused the constraint violation.

    """

    key: str
    value: Any


class BasePsycopgTranslator:
    """Base translator for turning psycopg errors into user-friendly messages.

    Supports customizing error messages via:
    - `code_map`: maps SQLSTATE codes to human-readable messages
    - `check_map`: maps check constraint names to meaningful descriptions

    Subclasses must implement `_get_pgcode()` and `_get_pgerror()` to support specific
    psycopg versions (e.g., psycopg2 vs. psycopg3).

    Attributes:
        code_map (dict): Mapping from SQLSTATE codes (str) to error messages (str).
        check_map (dict): Mapping from check constraint names (str)
            to descriptions (str).

    """

    code_map: dict
    check_map: dict

    def __init__(
        self,
        *,
        code_map: dict | None = None,
        check_map: dict | None = None,
    ) -> None:
        """Initialize the translator with optional custom message mappings.

        Args:
            code_map: Optional mapping from SQLSTATE codes (e.g. '23505')
                to error messages. If None, defaults to `DEFAULT_CODE_MAP`.
            check_map: Optional mapping from check constraint names
                to descriptive messages. If None, defaults to an empty dict.

        Example:
        ```python
            custom_codes = {"23505": "Значение уже существует"}
            custom_checks = {"age_check": "Возраст должен быть от 18 до 120"}
            t = BasePsycopgTranslator(code_map=custom_codes, check_map=custom_checks)
        ```

        """
        if code_map is not None:
            self.code_map = code_map
        else:
            self.code_map = DEFAULT_CODE_MAP

        if check_map is not None:
            self.check_map = check_map
        else:
            self.check_map = {}

    def translate(
        self,
        error: Any,
    ) -> str:
        """Translate a psycopg database error into a user-friendly message.

        Extracts `pgcode` and `pgerror` from the error and formats a meaningful response
        based on the type of constraint violation (unique, check, foreign key).

        Args:
            error: A psycopg exception (e.g. IntegrityError, DatabaseError).

        Returns:
            A formatted error message, or a fallback if no match is found.

        Example:
        ```python
            # Given error: unique_violation on email = 'test@example.com'
            print(translator.translate(error))
            #> "БД уже содержит значение: ключ email, значение test@example.com"
        ```

        """
        msg: str = UNKNOWN_CODE

        pgcode = self._get_pgcode(error)
        pgerror = self._get_pgerror(error)

        if pgcode is not None:
            code_msg: str | None = self.code_map.get(pgcode, UNKNOWN_CODE)
            data: ErrorData | None = None

            if pgcode == "23514":
                data = self._translate_check_violation(error_msg=pgerror)
            elif pgcode in ["23505", "23503"]:
                data = self._translate_unique_violation(error_msg=pgerror)

            if data and code_msg:
                msg = f"{code_msg}: ключ {data.key}, значение {data.value}."
            else:
                msg = code_msg

        return msg

    def _get_pgcode(self, error: Any) -> str | None:
        """Extract pgcode code from the error.

        Must be implemented by subclasses to support specific psycopg versions.

        Args:
            error: The raw database exception.

        Returns:
            The SQLSTATE code as a string (e.g. '23505'), or None if not available.

        """
        raise NotImplementedError

    def _get_pgerror(self, error: Any) -> str | None:
        """Extract the full error message from the exception.

        Must be implemented by subclasses to support specific psycopg versions.

        Args:
            error: The raw database exception.

        Returns:
            Full error message string, or None if not available.

        """
        raise NotImplementedError

    @classmethod
    def _translate_unique_violation(cls, error_msg: str) -> ErrorData:
        """Extract field and value from a unique constraint violation error.

        Uses a regex to parse the PostgreSQL
        "DETAIL: Key (field)=(value) already exists" message.

        Args:
            error_msg: The full error text from the database.

        Returns:
            ErrorData with extracted field name and value, or None if not matched.

        Example:
        ```python
            error_msg = "DETAIL: Key (email)=(user@example.com) already exists."
            print(BasePsycopgTranslator._translate_unique_violation(error_msg))
            #> ErrorData(key='email', value='user@example.com')
        ```

        """
        data: ErrorData | None = None

        pattern = re.compile(UNIQUE_VIOLATION_PATTERN)
        matched = pattern.search(error_msg)

        if matched is not None:
            data = ErrorData(key=matched.group(2), value=matched.group(3))

        return data

    def _translate_check_violation(self, error_msg: str) -> ErrorData | None:
        """Extract constraint name and description from a check constraint violation.

        Looks up a human-readable description in `self.check_map`. If not found,
        returns a default message.

        Args:
            error_msg: The full error text from the database.

        Returns:
            ErrorData with constraint name and description, or None if not matched.

        Example:
        ```python
            error_msg = "violates check constraint 'age_check'"
            check_map = {"age_check": "Возраст должен быть от 18 до 120"}
            translator = BasePsycopgTranslator(check_map=check_map)
            print(translator._translate_check_violation(error_msg))
            #> ErrorData(key='age_check', value='Возраст должен быть от 18 до 120')
        ```

        """
        data: ErrorData | None = None

        pattern = re.compile(CHECK_VIOLATION_PATTERN)
        matched = pattern.search(error_msg)
        if matched is not None:
            check_constraint = matched.group(1)
            constraint_description = self.check_map.get(
                check_constraint,
                UNKNOWN_CHECK_DESCRIPTION,
            )
            data = ErrorData(key=check_constraint, value=constraint_description)

        return data
