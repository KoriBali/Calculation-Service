"""Turn validation and engine input errors into the error envelope."""

from pydantic import ValidationError

from app.shared.response import error_response


class CalculationInputError(Exception):
    """Input passed schema validation but the engine rejected it."""


def register_error_handlers(app) -> None:
    @app.errorhandler(ValidationError)
    def _validation_error(error: ValidationError):
        errors = [
            {
                "field": ".".join(str(part) for part in item["loc"]),
                "message": item["msg"],
                "type": item["type"],
            }
            for item in error.errors(include_url=False)
        ]
        return error_response("Input tidak valid", errors=errors, status_code=422)

    @app.errorhandler(CalculationInputError)
    def _calculation_input_error(error: CalculationInputError):
        return error_response(str(error), status_code=422)