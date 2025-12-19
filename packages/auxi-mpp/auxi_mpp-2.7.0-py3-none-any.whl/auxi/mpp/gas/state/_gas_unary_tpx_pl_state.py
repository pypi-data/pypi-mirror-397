from typing import Self

from auxi.core.validation import floatFraction, floatPositive
from pydantic import Field, model_validator

from ...core.material_state import MaterialState


class GasUnaryTpxpLState(MaterialState):
    """
    Binary temperature, pressure, composition and gas geometry state for a gas.

    Args:
    ----
        T : [K] Temperature.
        p : [Pa] Pressure.
        x : [mol/mol] Partial pressure fraction of unary gas.
        pL : [Pa.m] Pressure path length.

    Raises:
    ------
        ValueError: If less than or more than one component was provided.
        ValueError: If the temperature is out of range (298 K < T < 2500 K).
        ValueError: If the pressure is out of range (50 662.5 Pa (0.5 atm) < p < 202 650 Pa (2 atm)).
        ValueError: If the partial pressure is not a fraction between 0.0 and 1.0.
        ValueError: If the pressure path length is out of range (0 Pa.m < pL < 500 000 Pa.m)
    """

    T: floatPositive
    p: floatPositive
    x: dict[str, floatFraction]
    pL: floatPositive
    compound: str = Field(default_factory=str)

    @model_validator(mode="after")
    def check_model(self) -> Self:
        comp_list = list(self.x.keys())
        if len(comp_list) != 1:
            raise ValueError("One and only one component should be provided.")
        self.compound = comp_list[0]

        if self.T < 298 or self.T > 2500:
            raise ValueError("Temperature should be above 298 K and below 2500 K.")

        if self.p < 0.5 * 101325 or self.p > 2 * 101325:
            raise ValueError("Pressure should be above 50 662.5 Pa (0.5 atm) and below 202 650 Pa (2 atm).")

        for comp in self.x:
            if self.x[comp] < 0.0 or self.x[comp] > 1.0:
                raise ValueError("Gas partial pressure should be a fraction between 0.0 and 1.0, inclusive.")

        if self.pL < 0.001 or self.pL > 5e5:
            raise ValueError("Pressure path should be above 0 Pa.m and below 500 000 Pa.m.")

        return self

    def _init(self):
        return
