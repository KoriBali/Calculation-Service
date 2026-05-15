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

    calc   = CalcLoadPerSection(poles + direct_objects)
    totals = calc.get_total_load(z_ref)

    

    # Berdasarkan Calculation
    # build domain objects
    # poles = [
    #     PoleObject(
    #         name      = p.name,
    #         diameter  = p.diameter,
    #         thickness = p.thickness,
    #         material  = p.material,
    #         z_height  = p.z_height,
    #     )
    #     for p in request.poles
    # ]

    # direct_objects = [
    #     DirectObject(
    #         name     = d.name,
    #         area     = d.area,
    #         cf       = d.cf,
    #         weight   = d.weight,
    #         z_height = d.z_height,
    #     )
    #     for d in request.direct_objects
    # ]

    # objects = poles + direct_objects

    # run calculation
    # calc = CalcLoadPerSection(objects)


    # sections_result = {}
    # for section_name, z_ref in request.sections.items():
    #     per_obj = [
    #         {
    #             "name":     obj.name,
    #             "windload": round(windload, 4),
    #             "moment":   round(moment,   4),
    #         }
    #         for obj, windload, moment in calc.get_windloads(float(z_ref))
    #     ]

    #     totals = calc.get_total_load(float(z_ref))

    #     sections_result[section_name] = {
    #         "z_ref":          float(z_ref),
    #         "objects":        per_obj,
    #         "total_windload": round(totals["total_windload"], 4),
    #         "total_moment":   round(totals["total_moment"],   4),
    #     }

    return {
        # Berdasarkan Calculation
        # "summary": {
        #     "n_poles":          len(poles),
        #     "n_direct_objects": len(direct_objects),
        #     "n_high_evaluation":       len(request.sections),
        # },
        # "sections": sections_result,

        # Case Needs
        "total_windload": round(totals["total_windload"], 4),
        "total_moment":   round(totals["total_moment"],   4),
    }