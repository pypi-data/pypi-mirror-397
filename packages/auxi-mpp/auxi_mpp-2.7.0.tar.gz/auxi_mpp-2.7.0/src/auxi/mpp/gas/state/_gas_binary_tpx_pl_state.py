from typing import Self

from auxi.chemistry.validation import listCompoundFormulas
from auxi.core.validation import floatFraction, floatPositive
from pydantic import Field, model_validator

from ...core.material_state import MaterialState


class GasBinaryTpxpLState(MaterialState):
    """
    Binary temperature, pressure, composition and gas geometry state for a gas.

    Args:
    ----
        T : [K] Temperature.
        p : [Pa] Pressure.
        x : [mol/mol] Mole fraction of gas components.
        pL : [Pa.m] Pressure path length.

    Raises:
    ------
        ValueError: If less than or more than two components was provided.
        ValueError: If the temperature is out of range (298 K < T < 2500 K).
        ValueError: If the pressure is out of range (50 662.5 Pa (0.5 atm) < p < 202 650 Pa (2 atm)).
        ValueError: If a mole fraction are less than 0.0.
        ValueError: If the sum of mole fractions are greater than 1.00.
        ValueError: If the pressure path length is out of range (0 Pa.m < pL < 500 000 Pa.m)
    """

    T: floatPositive
    p: floatPositive
    x: dict[str, floatFraction]
    pL: floatPositive
    compounds: listCompoundFormulas = Field(default_factory=list)

    @model_validator(mode="after")
    def check_model(self) -> Self:
        self.compounds = list(self.x.keys())

        if len(self.compounds) != 2:
            raise ValueError("Two and only two components should be provided.")

        if self.T < 298 or self.T > 2500:
            raise ValueError("Temperature should be above 298 K and below 2500 K.")

        if self.p < 0.5 * 101325 or self.p > 2 * 101325:
            raise ValueError("Pressure should be above 50 662.5 Pa (0.5 atm) and below 202 650 Pa (2 atm).")

        total_mole_frac = 0
        for comp in self.x:
            if self.x[comp] < 0.0:
                raise ValueError("Mole fractions should be between 0.0 and 1.0.")
            total_mole_frac += self.x[comp]
        if total_mole_frac > 1.0:
            raise ValueError("Sum of mole fractions cannot be greater than 1.00.")

        if self.pL < 0.001 or self.pL > 5e5:
            raise ValueError("Pressure path should be above 0 Pa.m and below 500 000 Pa.m.")

        return self

    def _init(self):
        return
