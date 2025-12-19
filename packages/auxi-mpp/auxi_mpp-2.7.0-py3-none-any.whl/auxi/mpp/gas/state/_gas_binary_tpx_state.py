from typing import Any, Self

from auxi.chemistry.validation import listCompoundFormulas
from auxi.core.validation import floatFraction, floatPositiveOrZero
from pydantic import Field, model_validator

from ...core.material_state import MaterialState


class GasBinaryTpxState(MaterialState):
    """
    Binary temperature, pressure and composition state for a gas.

    Args:
    ----
        T : [K] Temperature.
        p : [Pa] Pressure.
        x : Mole fraction of gas components.

    Raises:
    ------
        ValueError: If less than or more than two components was provided.
        ValueError: If the temperature is out of range (298 K < T < 2500 K).
        ValueError: If the pressure is out of range (50 662.5 Pa (0.5 atm) < p < 202 650 Pa (2 atm)).
        ValueError: If the sum of mole fractions does not equal 1.00.
    """

    T: floatPositiveOrZero
    p: floatPositiveOrZero
    x: dict[str, floatFraction]
    compounds: listCompoundFormulas = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

    @model_validator(mode="after")
    def check_model(self) -> Self:
        self.compounds = list(self.x.keys())

        if len(self.compounds) != 2:
            raise ValueError("Two and only two components should be provided.")

        if self.T < 298 or self.T > 2500:
            raise ValueError("Temperature should be above 298 K and below 2500 K.")

        if self.p < 0.5 * 101325 or self.p > 2 * 101325:
            raise ValueError("Pressure should be above 50 662.5 Pa (0.5 atm) and below 202 650 Pa (2 atm).")

        if self.p < 0:
            raise ValueError("Pressure cannot be nagative.")

        total_mole_frac = 0
        for comp in self.x:
            total_mole_frac += self.x[comp]
        if abs(total_mole_frac - 1.00) > 1e-9:
            raise ValueError("Mole fractions should add up to 1.00.")

        return self

    def _init(self):
        return
