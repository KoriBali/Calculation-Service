from typing import List

from app.load_object.calculators.load_object import (
    CalcLoadPerSection,
    DirectObject,
    PoleObject,
)
from .schemas import DirectObjectInput, PoleInput, LoadObjectRequest


def evaluate_load_object(request: LoadObjectRequest) -> dict:
    """
    Terima LoadObjectRequest, return hasil kalkulasi sebagai dict
    siap dimasukkan ke success_response(data=...).
    """

    poles = [PoleObject(
        name=p.name, diameter=p.diameter, thickness=p.thickness,
        material=p.material, z_height=p.z_height
    ) for p in request.poles]
 
    direct_objects = [DirectObject(
        name=d.name, area=d.area, cf=d.cf,
        weight=d.weight, z_height=d.z_height
    ) for d in request.direct_objects]

    z_ref = float(list(request.high_evaluation.values())[0])

    calc   = CalcLoadPerSection(direct_objects + poles)

    eval_results = {}
    
    # Iterasi untuk setiap titik high_evaluation (contoh: eval_point_1)
    for eval_name, z_ref in request.high_evaluation.items():
        z_val = float(z_ref)
        
        # 1. Dapatkan detail beban per objek
        per_obj = [
            {
                "name": obj.name,
                "windload": round(windload, 4),
                "moment": round(moment, 4),
            }
            for obj, windload, moment in calc.get_windloads(z_val)
        ]

        # 2. Dapatkan total beban di titik tersebut
        totals = calc.get_total_load(z_val)
        
        # 3. Tentukan status (OK / NG)
        is_safe = totals["total_moment"] < 100000 

        # 4. Susun struktur response per evaluasi
        eval_results[eval_name] = {
            "z_ref": z_val,
            "status": "OK" if is_safe else "NG",
            "total_windload": round(totals["total_windload"], 4),
            "total_moment": round(totals["total_moment"], 4),
            "objects": per_obj
        }


    return eval_results