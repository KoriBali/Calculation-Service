from flask import Blueprint, request

from app.section_check.schemas import SectionCheckRequest
from app.section_check.services import calculate_section_check
from app.shared.response import error_response, success_response

section_check_bp = Blueprint("section_check", __name__, url_prefix="/api/section-check")


@section_check_bp.post("/calculate")
def calculate():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return error_response("Request body harus berupa JSON object", status_code=400)

    # ValidationError and CalculationInputError become 422 in app/shared/errors.py.
    data = SectionCheckRequest.model_validate(payload)
    return success_response(calculate_section_check(data))
