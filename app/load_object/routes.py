from flask import Blueprint, request
from app.utils.response import success_response, error_response

from .schemas import DirectObjectInput, PoleInput, LoadObjectRequest
from .services import evaluate_load_object

load_object_bp = Blueprint("load_object_calc", __name__, url_prefix="/api/load-object")

@load_object_bp.route("/calculate", methods=["POST"])
def calculate_load_object():
    payload = request.get_json()
    # print("this is Payload", payload)
 
    try:
        poles = [PoleInput(**p) for p in payload["poles"]]

        # direct_objects opsional — kalau key tidak ada, default list kosong
        direct_objects = [
            DirectObjectInput(**d) for d in payload.get("direct_objects", [])
        ]
 
        req = LoadObjectRequest(
            poles          = poles,
            direct_objects = direct_objects,
            high_evaluation       = payload["high_evaluation"],
        )
 
        result = evaluate_load_object(req)
 
        return success_response(data=result)
 
    except TypeError as e:
        return error_response(errors=e.args, status_code=400)
    except ValueError as e:
        return error_response(errors=e.args, status_code=422)
    except Exception as e:
        return error_response(errors=e.args, status_code=500)
