import math
from typing import Any, ClassVar

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty
from pydantic import Field

from ..state._gas_binary_tpx_pl_state import GasBinaryTpxpLState
from ._leckner_unary import LecknerUnary
from ._model import Model


class LecknerBinary(Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], floatPositiveOrZero]):
    """
    Binary H₂O and CO₂ gas emissivity model by Leckner.

    Returns:
       Emissivity [-].

    References:
        leckner1972, modest2013
    """

    references: ClassVar[list[strNotEmpty]] = ["leckner1972", "modest2013"]
    leckner_model: LecknerUnary = LecknerUnary()
    compound_scope: list[strCompoundFormula] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        self.compound_scope = self.leckner_model.compound_scope

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        pL: floatPositiveOrZero = 101325,
    ) -> float:
        """
        Calculate the emissivity of the binary H₂O and CO₂ gas mixture.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"H2O": 0.5, "CO2": 0.5}.
            pL: Pressure ath length. [Pa.m]

        Returns:
            Emissivity.
        """
        # validate inputs
        state = GasBinaryTpxpLState(T=T, p=p, x=x, pL=pL)

        # use the unary Leckner model
        pathLength = state.pL / state.p

        # H2O
        if state.x["H2O"] == 0.0:
            epsilon_H2O = 0.0
        else:
            p_a_H2O = state.p * state.x["H2O"]
            epsilon_H2O = self.leckner_model.calculate(
                T=state.T, p=state.p, x={"H2O": state.x["H2O"]}, pL=p_a_H2O * pathLength
            )
        # CO2
        if state.x["CO2"] == 0.0:
            epsilon_CO2 = 0.0
        else:
            p_a_CO2 = state.p * state.x["CO2"]
            epsilon_CO2 = self.leckner_model.calculate(
                T=state.T, p=state.p, x={"CO2": state.x["CO2"]}, pL=p_a_CO2 * pathLength
            )

        # get the correction due to band overlap
        delta_epsilon = self._delta_epsilon(p, x, pL)

        # final calculation
        epsilon = epsilon_H2O + epsilon_CO2 - delta_epsilon

        return epsilon

    def _delta_epsilon(self, p: float, x: dict[str, float], pL: float) -> float:
        # Eq. 11.179
        p_H2O: float = p * x["H2O"]
        p_CO2: float = p * x["CO2"]
        if p_H2O == 0.0 or p_CO2 == 0.0:
            return 0.0
        zeta = self._zeta(p_H2O, p_CO2)

        # first bracket
        bracket_1 = (zeta / (10.7 + 101 * zeta)) - 0.0089 * (zeta**10.4)

        # second bracket
        L = pL / p
        log10_inside = ((p_H2O + p_CO2) * L) / 1000  # (p_aL)_0 = 1000 Pa.m

        # for very low pressure length products, there will be zero interference
        if log10_inside < 1.0:
            return 0.0

        log_term = math.log10(log10_inside)
        bracket_2 = log_term**2.76

        # final calculation
        delta_epsilon = bracket_1 * bracket_2
        return delta_epsilon

    def _zeta(self, p_H2O: float, p_CO2: float):
        # Eq. 11.180
        zeta = p_H2O / (p_H2O + p_CO2)
        return zeta
