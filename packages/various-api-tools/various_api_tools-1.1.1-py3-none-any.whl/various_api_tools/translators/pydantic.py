"""Module for translating Pydantic validation errors into Russian messages.

This module provides a utility class to convert Pydantic error details into
descriptive error messages in Russian, suitable for end-user feedback.

"""

from collections.abc import Sequence
from typing import Final

from pydantic_core import ErrorDetails

from ..validators.pydantic.constants import (  # noqa: TID252
    PYDANTIC_ERROR_TYPES,
    UNKNOWN_ERROR_TYPE,
)

DEFAULT_LOCATION_PREFIX: Final[str] = "Поле"


class PydanticValidationErrorTranslator:
    """Translate Pydantic validation errors into human-readable Russian messages.

    This class provides a method to translate a sequence of Pydantic error details
    into a formatted string with location, type and input information.

    """

    error_types = PYDANTIC_ERROR_TYPES

    @classmethod
    def get_str_pydantic_loc(cls, loc: tuple[str]) -> str:
        """Convert a Pydantic location tuple into a dot-separated string.

        Args:
            loc: A tuple representing the field path in the model.

        Returns:
            A string representation of the field path.

        Example:
            ```python
            print(ValidationErrorTranslator.get_str_pydantic_loc(("user", "name")))
            #> "user.name"
            ```

        """
        return ".".join([str(loc_value) for loc_value in loc])

    @classmethod
    def translate(cls, errors: Sequence[ErrorDetails]) -> str:
        """Translate a list of Pydantic error details into a human-readable message.

        Args:
            errors: A sequence of Pydantic ErrorDetails objects.

        Returns:
            A formatted string containing all translated errors.

        Example:
           ```python
           class Model(BaseModel):
               email: str

           try:
               Model(email=1)
           except ValidationError as exc:
               print(ValidationErrorTranslator.translate(exc.errors())

           #> Поле: "email". Ошибка: "Невалидное строковое значение(str)";
           ```

        """
        formatted_errors: list[str] = []
        for error in errors:
            error_str: str = ""

            location_part: str = ""
            type_part: str = ""
            input_part: str = ""

            if "loc" in error:
                prefix: str = DEFAULT_LOCATION_PREFIX
                if error["loc"][0] == "query":
                    prefix = "Параметр запроса"
                location_part = (
                    f'{prefix}: "{cls.get_str_pydantic_loc(loc=error["loc"])}"'
                )

            if "type" in error:
                msg = cls.error_types.get(error["type"], UNKNOWN_ERROR_TYPE)
                type_part = f'Ошибка: "{msg}"'

            if "input" in error and cls.error_types["missing"] not in type_part:
                input_part = f'заполнено неверно: "{error["input"]!r}"'

            if input_part != "":
                error_str = f"{location_part} {input_part}. {type_part};"
            else:
                error_str = f"{location_part}. {type_part};"

            formatted_errors.append(error_str)

        return "\n".join(formatted_errors)
