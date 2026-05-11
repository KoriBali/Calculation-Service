from flask import Blueprint, request
from app.utils.response import success_response, error_response
from .schemas import PoleInput, ObjectInput
from .services import evaluate_calculate_pole

pole_bp = Blueprint('pole_calc', __name__, url_prefix='/api/pole')

@pole_bp.route('/calculate', methods=['POST'])
def calculate_pole():
    payload = request.get_json()
    print(payload)

    # Additional Variable(bisa juga nanti ada di input frontend)
    wind_speed = 30  # m/s

    try:
        # SALAH - ini passing dict sebagai 1 argumen
        # pole = PoleInput(payload['pole'])

        # BENAR - unpack dict jadi keyword arguments
        pole = PoleInput(**payload['pole'])
        
        # SALAH 
        # objects = [ObjectInput(payload['objects'])]

        # BENAR 
        objects = [ObjectInput(**obj) for obj in payload['objects']]


        result = evaluate_calculate_pole(pole, objects, wind_speed)


        return success_response(data=result, unique_code=3)
    
    except TypeError as e:
        return error_response(errors=e.args, status_code=400)
    except Exception as e:
        return error_response(errors=e.args, status_code=500)