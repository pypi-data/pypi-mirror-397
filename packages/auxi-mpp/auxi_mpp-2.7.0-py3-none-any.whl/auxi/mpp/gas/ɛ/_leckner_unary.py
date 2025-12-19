import math
from typing import Any, ClassVar

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty
from pydantic import Field

from ._model import Model


class LecknerUnary(Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], floatPositiveOrZero]):
    """
    Unary H₂O or CO₂ gas emissivity model by Leckner.

    Returns:
       Emissivity [-].

    References:
        leckner1972, modest2013
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}

    references: ClassVar[list[strNotEmpty]] = ["leckner1972", "modest2013"]

    compound_scope: list[strCompoundFormula] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        self.compound_scope = list(self.data.keys())

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        pL: floatPositiveOrZero = 101325,
    ) -> float:
        """
        Calculate the emissivity of unary H₂O or CO₂ gas.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"H2O": 1.0}.
            pL: Partial pressure path length. [Pa.m]

        Returns:
            Emissivity.
        """
        compound = list(x.keys())
        compound = compound[0]

        # get the partial pressure and length variable
        p_a = p * x[compound]

        epsilon_0 = self._epsilon_0(T, pL, compound)
        epsilon_over_epsilon_0 = self._epsilon_over_epsilon_0(T, p, p_a, pL, compound)

        epsilon = epsilon_0 * epsilon_over_epsilon_0

        return epsilon

    def _epsilon_0(self, T: float, pL: float, compound: str):
        # Eq. 11.177
        M: int = self.data[compound]["M"]
        N: int = self.data[compound]["N"]
        c_ji: dict[int, dict[int, float]] = self.data[compound]["c_ji"]

        # calculate the two bracket terms
        term_T = T / 1000  # T_0 = 1000 K
        term_pL = pL / 1000  # (p_aL)_0 = 1000 Pa.m
        log_term_p_aL = math.log10(term_pL)

        # perform the double summation
        total_sum = 0.0
        for i in range(M + 1):
            for j in range(N + 1):
                # get the coefficient
                c = c_ji[j][i]

                # calculate the power terms
                T_power_term = term_T**j
                pL_power_term = log_term_p_aL**i

                # add to the total sum
                total_sum += c * T_power_term * pL_power_term

        # return the final exponentiated result
        return math.exp(total_sum)

    def _epsilon_over_epsilon_0(self, T: float, p: float, p_a: float, pL: float, compound: str) -> float:
        # Eq. 11.178

        # get parameters from Table 11.4
        a, b, c, P_e, p_aLm_P_aL0 = self._get_params(T, p, p_a, compound)

        # the fraction
        fraction_term = ((a - 1) * (1 - P_e)) / (a + b - 1 + P_e)

        # exponential term
        # inside the exponent
        p_aLm = p_aLm_P_aL0 * 1000  # P_aL0 = 1000 Pa.m
        log_term = math.log10(p_aLm / (pL))
        exponent = -c * (log_term**2)

        # the exponential itself
        e_term = math.exp(exponent)

        # final calculation
        result = 1 - (fraction_term * e_term)

        return result

    def _get_params(self, T: float, p: float, p_a: float, compound: str):
        # Table 11.4

        t = T / 1000
        P_e = self._P_e(t, p, p_a, compound)
        p_aLm_P_aL0 = self._p_aLm_P_aL0(t, compound)
        a = self._a(t, compound)
        b = self.data[compound]["b"]["x1"] * t ** self.data[compound]["b"]["x2"]
        c = self.data[compound]["c"]

        return a, b, c, P_e, p_aLm_P_aL0

    def _P_e(self, t: float, p: float, p_a: float, compound: str):
        # Table 11.4
        # P_e can be expressed as (p + (x*p_a)*t**y)/p_0, where p_0 = 100 000 Pa

        P_e = (p + (self.data[compound]["P_E"]["x"] * p_a) * t ** self.data[compound]["P_E"]["y"]) / 100000
        return P_e

    def _p_aLm_P_aL0(self, t: float, compound: str):
        if t > 0.7:
            x1: float = self.data[compound]["pLm/pL0"]["greater"]["x1"]
            x2: float = self.data[compound]["pLm/pL0"]["greater"]["x2"]
        else:
            x1: float = self.data[compound]["pLm/pL0"]["lesser"]["x1"]
            x2: float = self.data[compound]["pLm/pL0"]["lesser"]["x2"]
        return x1 * t**x2

    def _a(self, t: float, compound: str):
        if t > 0.75:
            x0: float = self.data[compound]["a"]["greater"][0]
            x1: float = self.data[compound]["a"]["greater"][1]
            x2: float = self.data[compound]["a"]["greater"][2]
            x3: float = self.data[compound]["a"]["greater"][3]
        else:
            x0: float = self.data[compound]["a"]["lesser"][0]
            x1: float = self.data[compound]["a"]["lesser"][1]
            x2: float = self.data[compound]["a"]["lesser"][2]
            x3: float = self.data[compound]["a"]["lesser"][3]
        return x0 + x1 * (math.log10(t) ** x2) * t**x3


LecknerUnary.load_data()
