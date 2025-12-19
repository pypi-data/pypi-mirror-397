"""Abstract base class for translating psycopg/psycopg2 database errors.

This module provides a foundation for parsing PostgreSQL error
details (such as `pgcode` and `pgerror`) from psycopg exceptions and converting
them into structured, human-readable error descriptions.
It supports both `psycopg2` and `psycopg3` by abstracting access to error attributes,
allowing concrete implementations to handle version-specific details.
"""

import re
from typing import Any

from .constants import (
    CHECK_VIOLATION_PATTERN,
    DEFAULT_CODE_MAP,
    UNIQUE_VIOLATION_PATTERN,
    UNKNOWN_CHECK_DESCRIPTION,
    UNKNOWN_CODE,
    UNKNOWN_USER_RAISE_DESCRIPTION,
)


class BasePsycopgTranslator:
    """Base translator for turning psycopg errors into user-friendly messages.

    Supports customization via:
    - `code_map`: maps SQLSTATE codes to human-readable messages
    - `check_map`: maps check constraint names to meaningful descriptions
    - `user_map`: maps database column names to user-friendly field names

    Subclasses must implement `_get_pgcode()` and `_get_pgerror()` to support specific
    psycopg versions (e.g., psycopg2 vs. psycopg3).

    Attributes:
        code_map (dict): Mapping from SQLSTATE codes (str) to error messages (str).
        check_map (dict): Mapping from check constraint names (str)
            to descriptions (str).
        user_map (dict): Mapping from DB column/field names (str)
            to user-friendly names (str).

    """

    code_map: dict
    check_map: dict
    user_map: dict

    check_codes: list[str] = ["23514"]
    unique_codes: list[str] = ["23505", "23503"]
    user_codes: list[str] = ["P0001"]

    def __init__(
        self,
        *,
        code_map: dict | None = None,
        check_map: dict | None = None,
        user_map: dict | None = None,
    ) -> None:
        """Initialize the translator with optional custom message mappings.

        Args:
            code_map: Optional mapping from SQLSTATE codes (e.g. '23505') to
                error messages. If None, defaults to `DEFAULT_CODE_MAP`.
            check_map: Optional mapping from check constraint names to
                descriptive messages. If None, defaults to an empty dict.
            user_map: Optional mapping from database column names to
                user-friendly field names.
                    Used to improve readability in error messages.
                    Example: {"email": "Email пользователя", "phone": "Номер телефона"}
                    If None, defaults to an empty dict.

        Example:
        ```python
            custom_codes = {"23505": "Значение уже существует"}
            custom_checks = {"age_check": "Возраст должен быть от 18 до 120"}
            t = BasePsycopgTranslator(code_map=custom_codes, check_map=custom_checks)
        ```

        """
        self.code_map = code_map if code_map is not None else DEFAULT_CODE_MAP
        self.check_map = check_map if check_map is not None else {}
        self.user_map = user_map if user_map is not None else {}

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

            if pgcode in self.check_codes:
                msg = self._translate_check_violation(
                    code_msg=code_msg,
                    error_msg=pgerror,
                )
            elif pgcode in self.unique_codes:
                msg = self._translate_unique_violation(
                    code_msg=code_msg,
                    error_msg=pgerror,
                )
            elif pgcode in self.user_codes:
                msg = self._translate_user_raise(code_msg=code_msg, error_msg=pgerror)

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
    def _translate_unique_violation(cls, code_msg: str, error_msg: str) -> str:
        """Extract details from a unique constraint violation and format a message.

        Parses the PostgreSQL error message to extract the violated field and
        its conflicting value using a predefined regex pattern.

        Args:
            code_msg: Base message from code_map for this error type.
            error_msg: Full PostgreSQL error text.

        Returns:
            Formatted message with field name and value if found;
            otherwise returns the base code_msg.

        Example:
            For error_msg = "DETAIL: Key (email)=(user@example.com) already exists",
            returns: "БД уже содержит значение: ключ email, значение user@example.com"

        """
        msg = code_msg

        pattern = re.compile(UNIQUE_VIOLATION_PATTERN)
        matched = pattern.search(error_msg)

        if matched is not None:
            constraint = matched.group(2)
            description = matched.group(3)
            if constraint and description:
                msg = f"{code_msg}: ключ {constraint}, значение {description}"

        return msg

    def _translate_check_violation(self, code_msg: str, error_msg: str) -> str:
        """Extract details from a check constraint violation and return a message.

        Looks up the violated constraint in `check_map` for a custom description.
        Falls back to `UNKNOWN_CHECK_DESCRIPTION` if not found.

        Args:
            code_msg: Base message from code_map for this error type.
            error_msg: Full PostgreSQL error text.

        Returns:
            Formatted message with constraint name and its description if available;
            otherwise returns the base code_msg.

        Example:
            If constraint 'age_check' is violated and check_map provides a description,
            returns: "Нарушено ограничение данных: ключ age_check.
            Описание: Возраст должен быть от 18 до 120"

        """
        msg = code_msg

        pattern = re.compile(CHECK_VIOLATION_PATTERN)
        matched = pattern.search(error_msg)
        if matched is not None:
            constraint = matched.group(1)
            description = self.check_map.get(
                constraint,
                UNKNOWN_CHECK_DESCRIPTION,
            )

            if constraint and description:
                msg = f"{code_msg}: ключ {constraint}. Описание: {description}"

        return msg

    def _translate_user_raise(self, code_msg: str, error_msg: str) -> str:
        """Extract details from a user-raised exception and return a message.

        Searches the error message for known field keys defined in `user_map`.
        Returns a user-friendly description if a match is found; otherwise falls back
        to `UNKNOWN_USER_RAISE_DESCRIPTION`.

        Args:
            code_msg: Base message from code_map for this error type.
            error_msg: Full PostgreSQL error text from RAISE EXCEPTION.

        Returns:
            Formatted message with a friendly field description if found;
            otherwise returns the base code_msg with a generic description.

        Example:
            If error_msg contains 'status' and user_map={"status": "Статус"},
            returns: "Ошибка БД: Статус"

            If no match is found:
            returns: "Ошибка БД: Невозможно выполнить операцию"

        """
        description = UNKNOWN_USER_RAISE_DESCRIPTION

        for key in self.user_map:
            if key in error_msg:
                description = self.user_map.get(key)
                break

        return f"{code_msg}: {description}"
