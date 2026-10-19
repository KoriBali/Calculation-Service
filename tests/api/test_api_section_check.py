"""POST /api/section-check/calculate: contract, validation, and parity."""

import copy

import pytest
from pydantic.alias_generators import to_camel

from app.shared.mappers import camelize
from tests.parity.parity import assert_matches, case_names, load_fixture

URL = "/api/section-check/calculate"

# Cases that the API can run before D6 (no overhead wire).
API_CASES = [
    name for name in case_names() if not load_fixture(name)["input"]["overhead_wires"]
]


def to_request(case_input: dict, with_seismic: bool = True) -> dict:
    """Fixture input (engine kwargs) -> request body (API contract)."""
    poles = []
    for pole in case_input["poles"]:
        body = {
            "name": pole["name"],
            "poleType": pole["pole_type"],
            "material": pole["material"],
            "topElevationM": pole["top_elevation_m"],
        }
        if pole["pole_type"] == "Straight":
            body |= {
                "diameterMm": pole["diameter_lower_mm"],
                "thicknessMm": pole["thickness_lower_mm"],
            }
        else:
            body |= {
                "diameterLowerMm": pole["diameter_lower_mm"],
                "diameterUpperMm": pole["diameter_upper_mm"],
                "thicknessLowerMm": pole["thickness_lower_mm"],
                "thicknessUpperMm": pole["thickness_upper_mm"],
            }
        poles.append(body)

    direct_objects = []
    for item in case_input["direct_objects"]:
        body = {
            "name": item["name"],
            "objectType": item["object_type"],
            "frontAreaM2": item["front_area_m2"],
            "massPerUnitKg": item["mass_per_unit_kg"],
            "elevationM": item["elevation_m"],
            "baseWindCoefficient": item["base_wind_coefficient"],
            "quantity": item["quantity"],
        }
        if item["object_type"] == "Directional":
            body |= {
                "sideAreaM2": item["side_area_m2"],
                "fixedAngleDeg": item["fixed_angle_deg"],
            }
        direct_objects.append(body)

    request = {
        "wind": {to_camel(k): v for k, v in case_input["wind"].items()},
        "overdesignFactor": case_input["overdesign_factor"],
        "baseElevationM": case_input["base_elevation_m"],
        "poles": poles,
        "directObjects": direct_objects,
        "evaluatedPositionsM": case_input["evaluated_positions_m"],
    }
    if with_seismic:
        request["seismic"] = {to_camel(k): v for k, v in case_input["seismic"].items()}
    return request


@pytest.mark.parametrize("with_seismic", [True, False], ids=["seismic", "no-seismic"])
@pytest.mark.parametrize("name", API_CASES)
def test_response_matches_python_calc(client, name, with_seismic):
    fixture = load_fixture(name)
    response = client.post(URL, json=to_request(fixture["input"], with_seismic))

    assert response.status_code == 200, response.get_json()
    body = response.get_json()
    assert body["success"] is True
    data = body["data"]
    assert data["checks"] == (["wind", "seismic"] if with_seismic else ["wind"])

    for actual, expected in zip(
        data["evaluatedPositions"], fixture["expected"]["positions"], strict=True
    ):
        label = f"{name}@{expected['evaluated_position_m']}"
        assert actual["evaluatedPositionM"] == expected["evaluated_position_m"]
        for key, fixture_key in (
            ("pole", "pole"),
            ("directObject", "direct_object"),
            ("sectionCheck", "section_check"),
        ):
            assert_matches(
                actual[key],
                camelize(expected[fixture_key]),
                f"{label}.{key}",
                seismic_absent=not with_seismic,
            )


def test_snake_case_body_is_accepted(client):
    """gateway forward() sends model_dump() in snake_case."""
    body = {
        "wind": {"design_standard": 3, "structure_height_m": 8.0},
        "poles": [{
            "name": "P", "pole_type": "Straight", "diameter_mm": 139.8,
            "thickness_mm": 4.5, "material": "STK400", "top_elevation_m": 8.0,
        }],
        "evaluated_positions_m": [0.0],
    }
    assert client.post(URL, json=body).status_code == 200


def base_request() -> dict:
    return to_request(load_fixture("case_pole_only_std2")["input"])


def error_fields(response) -> set[str]:
    return {item["field"] for item in response.get_json()["errors"]}


@pytest.mark.parametrize(
    ("change", "field"),
    [
        (lambda r: r["wind"].update(designStandard=1), "wind.1.atmosphericCategory"),
        (lambda r: r["wind"].update(designStandard=9), "wind"),
        (lambda r: r["wind"].update(atmosphericCategory=2), "wind.2.atmosphericCategory"),
        (lambda r: r.update(seismic={"position": "Rooftop"}), "seismic.Rooftop.seismicClass"),
        (lambda r: r["poles"][0].update(material="SS400"), "poles.0.Straight.material"),
        (lambda r: r["poles"][0].pop("thicknessMm"), "poles.0.Straight.thicknessMm"),
        (lambda r: r.update(poles=[]), "poles"),
        (lambda r: r.update(evaluatedPositionsM=[]), "evaluatedPositionsM"),
        (lambda r: r.update(overheadWires=[]), "overheadWires"),
        (lambda r: r.update(overdesignFactor=0), "overdesignFactor"),
    ],
)
def test_schema_errors_return_422_with_field(client, change, field):
    request = copy.deepcopy(base_request())
    change(request)
    response = client.post(URL, json=request)
    assert response.status_code == 422
    assert response.get_json()["success"] is False
    assert field in error_fields(response)


@pytest.mark.parametrize(
    "change",
    [
        lambda r: r["poles"].append(dict(r["poles"][0], topElevationM=9.0)),
        lambda r: r.update(evaluatedPositionsM=[1.0, 1.0]),
        lambda r: r.update(evaluatedPositionsM=[0.0]),  # base is 0.5
    ],
    ids=["duplicate-pole-name", "duplicate-position", "below-base"],
)
def test_cross_field_errors_return_422(client, change):
    request = copy.deepcopy(base_request())
    change(request)
    assert client.post(URL, json=request).status_code == 422


def test_engine_rule_error_returns_422_with_message(client):
    request = base_request() | {"evaluatedPositionsM": [6.0]}  # top of the only pole
    response = client.post(URL, json=request)
    assert response.status_code == 422
    assert "EvaluatedPosition must be below the top" in response.get_json()["message"]


def test_non_json_body_returns_400(client):
    response = client.post(URL, data="not json", content_type="text/plain")
    assert response.status_code == 400