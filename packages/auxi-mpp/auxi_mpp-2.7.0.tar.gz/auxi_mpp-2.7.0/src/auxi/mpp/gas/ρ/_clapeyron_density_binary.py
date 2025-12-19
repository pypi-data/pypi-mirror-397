from typing import Any, ClassVar

from auxi.chemistry import stoichiometry as stoic
from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty
from pydantic import Field

from ..Vm._clapeyron_binary import ClapeyronBinary
from ._model import Model


class ClapeyronDensityBinary(Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction]]):
    """
    Binary ideal gas density model.

    Returns:
       Density in [kg/m³].

    References:
        poling2001
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}

    references: ClassVar[list[strNotEmpty]] = ["poling2001"]

    compound_scope: list[strCompoundFormula] = Field(default_factory=list)
    molar_volume_binary: ClapeyronBinary = Field(default_factory=ClapeyronBinary)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        self.molar_volume_binary = ClapeyronBinary()
        self.compound_scope = self.molar_volume_binary.compound_scope

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
    ) -> float:
        """
        Calculate ideal gas density for a binary mixture.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"N2": 0.8, "O2": 0.2}.

        Returns:
            Density in [kg/m³].
        """
        mv = self.molar_volume_binary.calculate(T=T, p=p, x=x)
        # calculate average molar mass (M_mix) of the mixture
        M_mix = 0.0
        for compound, mole_fraction in x.items():
            M_mix += mole_fraction * stoic.molar_mass(compound) / 1000  # convert g/mol to kg/mol

        rho_kg_m3 = M_mix / mv

        return rho_kg_m3
