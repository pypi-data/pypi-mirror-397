import math
import warnings
from typing import Any, ClassVar

from auxi.chemistry import stoichiometry as stoic
from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty
from pydantic import Field

from ._model import Model


class MuznyUnary(Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction]]):
    """
    Unary gas viscosity model for H2.

    Returns:
       Viscosity in [Pa.s].

    References:
        muzny2013
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}

    references: ClassVar[list[strNotEmpty]] = ["muzny2013"]

    parameters: dict[str, dict[str, float]] = Field(default_factory=dict)
    compound_scope: list[strCompoundFormula] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        data = MuznyUnary.data
        self.compound_scope = list(self.data.keys())

        self.parameters: dict[str, dict[str, float]] = {c: data[c]["parameters"] for c in self.compound_scope}

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
    ) -> float:
        """
        Calculate unary H2 gas viscosity.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"H2":1.0}.

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

        # Implement Equation (3) and (4).

        # Get parameters from loaded data
        molar_mass = stoic.molar_mass(compound)
        sigma = self.parameters[compound]["sigma"]
        epsilon_k = self.parameters[compound]["epsilon_k"]

        a_coeffs = [self.parameters[compound][f"a{i}"] for i in range(5)]

        # Calculate reduced temperature, T*.
        T_star = T / epsilon_k
        ln_T_star = math.log(T_star)

        # Calculate ln(S*(T*)) using Equation (4).
        ln_S_star = 0.0
        for i in range(5):
            ln_S_star += a_coeffs[i] * (ln_T_star**i)

        S_star = math.exp(ln_S_star)

        numerator = 0.021357 * math.sqrt(molar_mass * T)

        denominator = (sigma**2) * S_star

        # Equation (3) is defined to yield muPa.s.
        mu_uPa_s = numerator / denominator

        # Convert to Pa.s for return (1 muPa.s = 1e-6 Pa.s)
        mu_Pa_s = mu_uPa_s * 1.0e-6

        return mu_Pa_s


MuznyUnary.load_data()
