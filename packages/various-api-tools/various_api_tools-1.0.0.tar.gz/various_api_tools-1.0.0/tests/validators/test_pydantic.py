from decimal import Decimal
from typing import Any

import pytest
from pydantic import EmailStr
from pydantic_core._pydantic_core import PydanticCustomError

from src.various_api_tools.validators.pydantic.utils import (
    email_validator,
    latitude_validator,
    longitude_validator,
    optional_string_validator,
    strip_validator,
    validate_required_field,
)


class TestPydanticValidator:
    @pytest.mark.parametrize(
        "input_value, expected_output",
        [
            ("  test  ", "test"),
            ("", ""),
            ("   ", ""),
        ],
    )
    def test_strip_validator(self, input_value: str, expected_output: str):
        result = strip_validator(input_value)
        assert result == expected_output

    @pytest.mark.parametrize(
        "input_value, expected_output, is_raised",
        [
            ("  test  ", "test", False),
            ("", None, False),
            (123, None, True),
        ],
    )
    def test_optional_string_validator(
        self,
        input_value: Any,
        expected_output: str | None,
        is_raised: bool,
    ):
        if is_raised:
            with pytest.raises(Exception):
                optional_string_validator(input_value)
        else:
            result = optional_string_validator(input_value)
            assert result == expected_output

    @pytest.mark.parametrize(
        "input_value, expected_output, is_raised",
        [
            ("test@example.com", EmailStr._validate("test@example.com"), False),
            (None, None, False),
            ("invalid-email", None, True),
        ],
    )
    def test_email_validator(
        self,
        input_value: Any,
        expected_output: EmailStr | None,
        is_raised: bool,
    ):
        if is_raised:
            with pytest.raises(Exception):
                email_validator(input_value)
        else:
            result = email_validator(input_value)
            assert result == expected_output

    @pytest.mark.parametrize(
        "input_value, expected_output, is_raised",
        [
            (Decimal("45.0"), Decimal("45.0"), False),
            (Decimal("90.0"), Decimal("90.0"), False),
            (Decimal("-90.0"), Decimal("-90.0"), False),
            (Decimal("100.0"), None, True),
        ],
    )
    def test_latitude_validator(
        self,
        input_value: Decimal,
        expected_output: Decimal | None,
        is_raised: bool,
    ):
        if is_raised:
            with pytest.raises(Exception):
                latitude_validator(input_value)
        else:
            result = latitude_validator(input_value)
            assert result == expected_output

    @pytest.mark.parametrize(
        "input_value, expected_output, is_raised",
        [
            (Decimal("90.0"), Decimal("90.0"), False),
            (Decimal("-180.0"), Decimal("-180.0"), False),
            (Decimal("180.0"), Decimal("180.0"), False),
            (Decimal("200.0"), None, True),
        ],
    )
    def test_longitude_validator(
        self,
        input_value: Decimal,
        expected_output: Decimal | None,
        is_raised: bool,
    ):
        if is_raised:
            with pytest.raises(Exception):
                longitude_validator(input_value)
        else:
            result = longitude_validator(input_value)
            assert result == expected_output

    @pytest.mark.parametrize(
        "input_value, expected_output, is_raised",
        [
            ("test", "test", False),
            (None, pytest.raises(PydanticCustomError), True),
            ("", pytest.raises(PydanticCustomError), True),
        ],
    )
    def test_validate_required_field(
        self,
        input_value: Any,
        expected_output: Any,
        is_raised: bool,
    ):
        if is_raised:
            with pytest.raises(Exception):
                validate_required_field(input_value)
        else:
            result = validate_required_field(input_value)
            assert result == expected_output
