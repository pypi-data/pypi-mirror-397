from various_api_tools.translators.psycopg.base import ErrorData
from various_api_tools.translators.psycopg.psycopg import PsycopgErrorTranslator


class TestPsycopgErrorTranslator:
    def test_translate_unique_violation(self):
        error_msg = (
            "DETAIL:  Key (uuid)=(a6cc5730-2261-11ee-9c43-2eb5a363657c) already exists."
        )
        result = PsycopgErrorTranslator._translate_unique_violation(error_msg)
        assert isinstance(result, ErrorData)
        assert result.key == "uuid"
        assert result.value == "a6cc5730-2261-11ee-9c43-2eb5a363657c"

        error_msg = "No violation here."
        result = PsycopgErrorTranslator._translate_unique_violation(error_msg)
        assert result is None

    def test_translate_check_violation(self):
        translator = PsycopgErrorTranslator(
            check_map={"valid_email": "Невалидный email"},
        )

        error_msg = 'violates check constraint "valid_email"'
        result = translator._translate_check_violation(error_msg)
        assert isinstance(result, ErrorData)
        assert result.key == "valid_email"
        assert result.value == "Невалидный email"

        error_msg = 'violates check constraint "unknown_check"'
        result = translator._translate_check_violation(error_msg)
        assert isinstance(result, ErrorData)
        assert result.key == "unknown_check"
        assert result.value == "Невалидная запись в БД"

        error_msg = "No violation here."
        result = translator._translate_check_violation(error_msg)
        assert result is None

    def test_translate_with_unique_violation(self):
        class MockError(Exception):
            def __init__(self):
                self.sqlstate = "23505"

            def __str__(self):
                return "DETAIL:  Key (email)=(invalid@example.com) already exists."

        translator = PsycopgErrorTranslator()
        result = translator.translate(MockError())
        assert (
            "БД уже содержит значение: ключ email, значение invalid@example.com."
            in result
        )

    def test_translate_with_check_violation(self):
        class MockError(Exception):
            def __init__(self):
                self.sqlstate = "23514"

            def __str__(self):
                return 'violates check constraint "valid_email"'

        translator = PsycopgErrorTranslator(
            check_map={"valid_email": "Невалидный email"},
        )
        result = translator.translate(MockError())
        assert (
            "Нарушено ограничение данных: ключ valid_email, значение Невалидный email."
            in result
        )

    def test_translate_with_unknown_code(self):
        class MockError(Exception):
            def __init__(self):
                self.sqlstate = "00000"

            def __str__(self):
                return ""

        translator = PsycopgErrorTranslator()
        result = translator.translate(MockError())
        assert result == "Неизвестная ошибка БД"

    def test_translate_with_custom_messages(self):
        class MockError(Exception):
            def __init__(self):
                self.sqlstate = "23503"

            def __str__(self):
                return ""

        custom_code_map = {
            "23503": "Указан несуществующий внешний идентификатор",
        }
        translator = PsycopgErrorTranslator(code_map=custom_code_map)
        result = translator.translate(MockError())
        assert result == "Указан несуществующий внешний идентификатор"
