import math
import warnings
from typing import Any, ClassVar

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty
from pydantic import Field

from ._model import Model


class HellmannVogelUnary(Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction]]):
    """
    Unary gas viscosity model for H2O.

    Returns:
       Viscosity in [Pa.s].

    References:
        hellmann2015
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}

    references: ClassVar[list[strNotEmpty]] = ["hellmann2015"]

    parameters: dict[str, dict[str, float]] = Field(default_factory=dict)
    compound_scope: list[strCompoundFormula] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        data = HellmannVogelUnary.data
        self.compound_scope = list(self.data.keys())

        self.parameters: dict[str, dict[str, float]] = {c: data[c]["parameters"] for c in self.compound_scope}

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
    ) -> float:
        """
        Calculate unary H2O gas viscosity.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"H2O":1.0}.

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

        # Implement Equation (3) of hellmann2015.

        # Get parameters from loaded data.
        Tc = self.parameters[compound]["Tc_K"]
        a_coefficients = [self.parameters[compound][f"a{i}"] for i in range(8)]

        # Calculate reduced temperature, T_bar.
        T_bar = T / Tc

        numerator = math.sqrt(T_bar)

        denominator = 0.0
        for i in range(8):
            denominator += a_coefficients[i] * (T_bar ** (-i / 2.0))

        # Equation (3) is defined to yield muPa.s.
        mu_muPa_s = numerator / denominator

        # Convert to Pa.s for return (1 muPa.s = 1e-6 Pa.s).
        mu_Pa_s = mu_muPa_s * 1.0e-6

        return mu_Pa_s


HellmannVogelUnary.load_data()
