import app.pole.calculators.calc as calc
from app.pole.schemas import ObjectInput, PoleInput
from typing import List


def evaluate_calculate_pole(pole: PoleInput, objects: List[ObjectInput], wind_speed: float) -> dict:
    """
    Runs all structural calculations for a pole in one call.
 
    Parameters:
    - pole       : pole data (PoleInput)
    - objects    : list of mounted objects (List[ObjectInput])
    - wind_speed : wind speed (m/s)
 
    Returns: dict containing all calculation results
    """
    D = pole.diameter_pole    # mm
    t = pole.thickness_pole   # mm
    L = pole.height_pole      # m
    # Material
    mat = calc.get_material_properties(pole.material_pole)
    Fy  = mat["Fy"]
 
    # Cross-section
    print('result: ',D,t)
    A = calc.calc_cross_sectional_area(D, t)
    I = calc.calc_moment_of_inertia(D, t)
    Z = calc.calc_section_modulus(D, t)
    r = calc.calc_radius_of_gyration(D, t)
 
    # Loads
    q       = calc.calc_wind_pressure(wind_speed)
    P       = calc.calc_total_dead_load(objects)
    M_total = calc.calc_total_bending_moment(objects, q)
 
    # Stress
    sigma_axial   = calc.calc_axial_stress(P, A)
    sigma_bending = calc.calc_bending_stress(M_total, Z)
    sigma_total   = calc.calc_total_stress(sigma_axial, sigma_bending)
 
    # Slenderness
    lambda_ = calc.calc_slenderness_ratio(L, r)
 
    # Capacity
    f_allow = calc.calc_allowable_stress(Fy)
    UR      = calc.calc_utilization_ratio(sigma_axial, sigma_bending, f_allow, f_allow)
 
    return {
        "conclusion"                : "OK" if UR <= 1.0 else "NG",
        "details" : {
            "cross_section" : {
                "inner_diameter_mm"         : round(calc.calc_inner_diameter(D, t), 3),
                "cross_sectional_area_mm2"  : round(A, 3),
                "moment_of_inertia_mm4"     : round(I, 3),
                "section_modulus_mm3"       : round(Z, 3),
                "radius_of_gyration_mm"     : round(r, 3),
            },
            "loads" : {
                "wind_pressure_Pa"          : round(q, 3),
                "total_dead_load_N"         : round(P, 3),
                "total_bending_moment_Nm"   : round(M_total, 3),
            },
            "stress" : {
                "axial_stress_MPa"          : round(sigma_axial, 3),
                "bending_stress_MPa"        : round(sigma_bending, 3),
                "total_stress_MPa"          : round(sigma_total, 3),
            },
            "check" : {
                "slenderness_ratio"         : round(lambda_, 3),
                "slenderness_ok"            : lambda_ <= 200,
                "allowable_stress_MPa"      : round(f_allow, 3),
                "utilization_ratio"         : round(UR, 4),
            }
        },
 
 
 
    }
