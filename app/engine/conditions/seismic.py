"""Seismic condition. Ported from python_calc ``domain/conditions.py`` (commit 41cca03)."""


class SeismicCondition:
    """Seismic condition currently supplied as a dimensionless K value."""

    ROOFTOP_K_VALUES = {"A": 1.5, "B": 1.0, "S": 2.0}

    def __init__(
        self,
        position: str,
        k_value: float,
        seismic_class: str | None = None,
    ) -> None:
        normalized_position = position.strip().title()
        if normalized_position not in {"Ground", "Rooftop"}:
            raise ValueError("Position must be 'Ground' or 'Rooftop'")
        if k_value <= 0:
            raise ValueError("Seismic K value must be greater than zero")

        self.position = normalized_position
        self.k_value = float(k_value)
        self.seismic_class = seismic_class

    @classmethod
    def ground(cls, k_value: float) -> "SeismicCondition":
        return cls(position="Ground", k_value=k_value)

    @classmethod
    def rooftop(cls, seismic_class: str) -> "SeismicCondition":
        normalized_class = seismic_class.strip().upper()
        try:
            k_value = cls.ROOFTOP_K_VALUES[normalized_class]
        except KeyError:
            raise ValueError("Seismic class must be A, B, or S") from None
        return cls("Rooftop", k_value, normalized_class)
