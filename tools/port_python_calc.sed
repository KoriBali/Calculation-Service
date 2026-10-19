# Rewrites python_calc imports and BasicFunction names to app.engine.
# Usage: git -C ../python_calc show 41cca03:<file> | sed -f tools/port_python_calc.sed > <target>

# BasicFunction -> app.engine.sections
s/^import BasicFunction$/from app.engine import sections/
s/BasicFunction\.Cross_AreaP/sections.cross_section_area_cm2/g
s/BasicFunction\.Moment_Inertia/sections.moment_of_inertia_cm4/g
s/BasicFunction\.Section_Modulus/sections.section_modulus_cm3/g
s/BasicFunction\.Radius_Gyration/sections.radius_of_gyration_cm/g
s/BasicFunction\.Pole_WeightKg_Straight/sections.straight_pole_mass_kg/g
s/BasicFunction\.Pole_WeightKg_Taper/sections.taper_pole_mass_kg/g
s/BasicFunction\.PI/sections.PI/g
s/BasicFunction\.DENSITY/sections.DENSITY/g
s/DiameterP_U=/diameter_upper_mm=/g
s/DiameterP_L=/diameter_lower_mm=/g
s/ThicknessP_U=/thickness_upper_mm=/g
s/ThicknessP_L=/thickness_lower_mm=/g
s/DiameterP=/diameter_mm=/g
s/ThicknessP=/thickness_mm=/g
s/LengthP=/length_m=/g

# domain -> app.engine
s/^from \.loads import /from app.engine.loads.base import /
s/^from domain\.loads import /from app.engine.loads.base import /
s/^from \.materials import /from app.engine.materials import /
s/^from domain\.materials import /from app.engine.materials import /
s/^from domain\.pole import /from app.engine.loads.pole import /
s/^from domain\.direct_object import /from app.engine.loads.direct_object import /
s/^from domain\.overhead_wire import /from app.engine.loads.overhead_wire import /
s/^from domain\.conditions import SeismicCondition, WindCondition, std_act_common$/from app.engine.conditions.seismic import SeismicCondition\nfrom app.engine.conditions.wind import WindCondition, std_act_common/
s/^from domain\.conditions import SeismicCondition, WindCondition$/from app.engine.conditions.seismic import SeismicCondition\nfrom app.engine.conditions.wind import WindCondition/

# calculation -> app.engine
s/^from \.result import /from app.engine.results import /
s/^from \.pole_assembly import /from app.engine.geometry.pole_assembly import /
s/^from calculation\.pole_assembly import /from app.engine.geometry.pole_assembly import /
s/^from \.pole_calculator import /from app.engine.calculators.pole import /
s/^from calculation\.pole_calculator import /from app.engine.calculators.pole import /
s/^from \.direct_object_calculator import /from app.engine.calculators.direct_object import /
s/^from calculation\.direct_object_calculator import /from app.engine.calculators.direct_object import /
s/^from \.overhead_wire_calculator import /from app.engine.calculators.overhead_wire import /
s/^from calculation\.overhead_wire_calculator import /from app.engine.calculators.overhead_wire import /
s/^from calculation\.evaluated_position_calculator import /from app.engine.calculators.section_check import /

# nnC_P is not ported (duplicate of PoleObject.base_wind_coefficient)
/def test_nnc_matches_confirmed_vba_formula/,+2d