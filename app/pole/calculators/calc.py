"""
file ini berisi rumus-rumus kalkulasi (testing purpose)
1. Material Properties
2. Cross-Section
3. Wind Load
4. Axial Load
5. Bending Load
6. Stress
7. Slenderness Check
8. Capacity Check & Utilization Ratio
9. Torsion
"""
import math
from app.constants import PI, AIR_DENSITY, GRAVITY
from typing import List
from app.pole.schemas import PoleInput, ObjectInput

# 1. Material Properties
MATERIAL_PROPERTIES = {
    "STK400": {"Fy": 250, "Fu": 400},  
    "STK490": {"Fy": 315, "Fu": 490},
    "STK540": {"Fy": 355, "Fu": 540},
}
 
def get_material_properties(material_code: str) -> dict:
    """
    Returns material properties based on material code.
    Fy = yield strength (MPa)
    Fu = ultimate tensile strength (MPa)
    """
    props = MATERIAL_PROPERTIES.get(material_code.upper())
    if not props:
        raise ValueError(f"Material '{material_code}' is not recognized.")
    return props



# 2. Cross-Section
def calc_inner_diameter(D: float, t: float) -> float:
    """
    d = D - 2t
    D = outer diameter (mm)
    t = wall thickness (mm)
    """
    return D - 2 * t
 
 
def calc_cross_sectional_area(D: float, t: float) -> float:
    """
    A = pi/4 x (D^2 - d^2)
    Output unit: mm^2
    """
    d = calc_inner_diameter(D, t)
    return (PI / 4) * (D**2 - d**2)
 
 
def calc_moment_of_inertia(D: float, t: float) -> float:
    """
    I = pi/64 x (D^4 - d^4)
    Output unit: mm^4
    """
    d = calc_inner_diameter(D, t)
    return (PI / 64) * (D**4 - d**4)
 
 
def calc_section_modulus(D: float, t: float) -> float:
    """
    Z = I / (D/2) = pi(D^4 - d^4) / (32 x D)
    Output unit: mm^3
    """
    I = calc_moment_of_inertia(D, t)
    return I / (D / 2)
 
 
def calc_radius_of_gyration(D: float, t: float) -> float:
    """
    r = sqrt(I / A)
    Output unit: mm
    """
    I = calc_moment_of_inertia(D, t)
    A = calc_cross_sectional_area(D, t)
    return math.sqrt(I / A)



# 3. Wind Load
def calc_wind_pressure(V: float) -> float:
    """
    q = 0.5 x rho x V^2
    V = wind speed (m/s)
    Output unit: Pa (N/m^2)
    """
    return 0.5 * AIR_DENSITY * V**2
 
 
def calc_frontal_wind_force(cf: float, area_front: float, q: float) -> float:
    """
    F_wind = cf x area_front x q
    cf         = drag coefficient (dimensionless)
    area_front = frontal projected area (m^2)
    q          = wind pressure (Pa)
    Output unit: N
    """
    return cf * area_front * q
 
 
def calc_lateral_wind_force(cf: float, area_side: float, q: float) -> float:
    """
    F_side = cf x area_side x q
    Output unit: N
    """
    return cf * area_side * q



# 4. Axial Load
def calc_total_dead_load(objects: List[ObjectInput]) -> float:
    """
    P = sum(weightDo_i) x g
    Output unit: N
    """
    total_kg = sum(obj.weight_do for obj in objects)
    return total_kg * GRAVITY



# 5. Bending Load
def calc_moment_per_object(F_wind: float, height: float) -> float:
    """
    M_i = F_wind_i x height_i
    F_wind = wind force on object (N)
    height = mounting height of object (m)
    Output unit: N.m
    """
    return F_wind * height
 
 
def calc_total_bending_moment(objects: List[ObjectInput], q: float) -> float:
    """
    M_total = sum(F_wind_i x heightDo_i)
    Output unit: N.m
    """
    total = 0.0
    for obj in objects:
        F = calc_frontal_wind_force(obj.cf_do, obj.area_front_do, q)
        M = calc_moment_per_object(F, obj.height_do)
        total += M
    return total



# 6. Stress
def calc_axial_stress(P: float, A: float) -> float:
    """
    sigma_axial = P / A
    P = axial load (N)
    A = cross-sectional area (mm^2)
    Output unit: MPa (N/mm^2)
    """
    return P / A
 
 
def calc_bending_stress(M: float, Z: float) -> float:
    """
    sigma_bending = M / Z
    M = bending moment (N.m) -> converted to N.mm internally
    Z = section modulus (mm^3)
    Output unit: MPa
    """
    M_Nmm = M * 1000  # convert N.m -> N.mm
    return M_Nmm / Z
 
 
def calc_total_stress(sigma_axial: float, sigma_bending: float) -> float:
    """
    sigma_total = sigma_axial + sigma_bending
    Output unit: MPa
    """
    return sigma_axial + sigma_bending


# 7. Slenderness Check
def calc_slenderness_ratio(L_eff: float, r: float) -> float:
    """
    lambda = L_eff / r
    L_eff = effective length of pole (m) -> converted to mm internally
    r     = radius of gyration (mm)
    General limit: lambda <= 200
    """
    L_eff_mm = L_eff * 1000  # convert meter -> mm
    return L_eff_mm / r



# 8. Capacity Check & Utilization Ratio
def calc_allowable_stress(Fy: float, factor: float = 0.6) -> float:
    """
    f_allow = factor x Fy
    Default factor = 0.6 (ASD method)
    Output unit: MPa
    """
    return factor * Fy
 
 
def calc_utilization_ratio(
    sigma_axial: float,
    sigma_bending: float,
    f_axial_allow: float,
    f_bending_allow: float
) -> float:
    """
    UR = (sigma_axial / f_axial_allow) + (sigma_bending / f_bending_allow)
    UR <= 1.0 -> SAFE
    UR >  1.0 -> NOT SAFE
    """
    return (sigma_axial / f_axial_allow) + (sigma_bending / f_bending_allow)



# 9. Torsion
def calc_polar_moment_of_inertia(D: float, t: float) -> float:
    """
    J = 2 x I  (for circular cross-section)
    Output unit: mm^4
    """
    return 2 * calc_moment_of_inertia(D, t)
 
 
def calc_torsional_moment(F_wind: float, eccentricity: float) -> float:
    """
    T = F_wind x e
    e = eccentricity from pole axis (m)
    Output unit: N.m
    """
    return F_wind * eccentricity
 
 
def calc_torsional_shear_stress(T: float, D: float, t: float) -> float:
    """
    tau = T x r / J
    r = D/2 (outer radius, mm)
    J = polar moment of inertia (mm^4)
    Output unit: MPa
    """
    T_Nmm = T * 1000                            # N.m -> N.mm
    r     = D / 2                               # mm
    J     = calc_polar_moment_of_inertia(D, t)  # mm^4
    return (T_Nmm * r) / J
