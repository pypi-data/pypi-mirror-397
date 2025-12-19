import math
import warnings
from typing import Any, ClassVar

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty
from pydantic import Field

from ._model import Model


class LaeseckeMuznyUnary(Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction]]):
    """
    Unary gas viscosity model for CO2.

    Returns:
       Dynamic viscosity in [Pa.s].

    References:
        laesecke2017
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}

    references: ClassVar[list[strNotEmpty]] = ["laesecke2017"]

    parameters: dict[str, dict[str, float]] = Field(default_factory=dict)
    compound_scope: list[strCompoundFormula] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        data = LaeseckeMuznyUnary.data
        self.compound_scope = list(self.data.keys())

        self.parameters: dict[str, dict[str, float]] = {c: data[c]["parameters"] for c in self.compound_scope}

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
    ) -> float:
        """
        Calculate unary CO2 gas viscosity.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"CO2":1.0}.

        Returns:
            Viscosity in [Pa.s].
        """
        if p != 101325:
            warnings.warn(
                f"{self.__class__.__name__} model is only implemented for atmospheric pressure at 101325 Pa.",
                UserWarning,
            )

        compound = list(x.keys())
        compound = compound[0]

        # Implement Equation (4) of laesecke2017.

        # Get parameters from loaded data.
        scaling_factor = self.parameters[compound]["scaling_factor"]
        a0 = self.parameters[compound]["a0"]
        a1 = self.parameters[compound]["a1"]
        a2 = self.parameters[compound]["a2"]
        a3 = self.parameters[compound]["a3"]
        a4 = self.parameters[compound]["a4"]
        a5 = self.parameters[compound]["a5"]
        a6 = self.parameters[compound]["a6"]

        # Pre-calculate temperature terms for Equation (4).
        T_1_6 = T ** (1 / 6)
        T_1_3 = T ** (1 / 3)
        T_sqrt = math.sqrt(T)
        exp_T_1_3 = math.exp(T_1_3)

        numerator = scaling_factor * T_sqrt

        term0 = a0
        term1 = a1 * T_1_6
        term2 = a2 * math.exp(a3 * T_1_3)
        term3 = (a4 + a5 * T_1_3) / exp_T_1_3
        term4 = a6 * T_sqrt

        denominator = term0 + term1 + term2 + term3 + term4

        # Equation (4) is defined to yield mPa.s.
        mu_mPa_s = numerator / denominator

        # Convert to Pa.s for return (1 mPa.s = 1e-3 Pa.s).
        mu_Pa_s = mu_mPa_s / 1000.0

        return mu_Pa_s


LaeseckeMuznyUnary.load_data()
