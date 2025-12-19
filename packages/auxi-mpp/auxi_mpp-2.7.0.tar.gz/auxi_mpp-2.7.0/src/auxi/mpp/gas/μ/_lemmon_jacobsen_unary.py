import math
import warnings
from typing import Any, ClassVar

from auxi.chemistry import stoichiometry as stoic
from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty
from pydantic import Field

from ._model import Model


class LemmonJacobsenUnary(Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction]]):
    """
    Unary gas viscosity model for Ar, CO, N2, and O2.

    Returns:
       Viscosity in [Pa.s].

    References:
        lemmon2004
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}

    references: ClassVar[list[strNotEmpty]] = ["lemmon2004"]

    parameters: dict[str, dict[str, float]] = Field(default_factory=dict)
    compound_scope: list[strCompoundFormula] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        data = LemmonJacobsenUnary.data
        self.compound_scope = list(self.data.keys())

        self.parameters: dict[str, dict[str, float]] = {c: data[c]["parameters"] for c in self.compound_scope}

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
    ) -> float:
        """
        Calculate unary gas viscosity for Ar, CO, N2, or O2.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"N2":1.0}.

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

        # Implement Equation (2).

        # Get parameters from loaded data for the specific compound
        molar_mass = stoic.molar_mass(compound)
        sigma = self.parameters[compound]["sigma"]
        epsilon_k = self.parameters[compound]["epsilon_k"]

        # Get coefficients b_0 to b_4
        b_coefficients = [self.parameters[compound][f"b{i}"] for i in range(5)]  # b0, b1, b2, b3, b4

        # Calculate reduced temperature, T* = T / (epsilon/k)
        T_star = T / epsilon_k

        ln_T_star = math.log(T_star)

        # Calculate ln(Omega(T*)).
        ln_Omega = 0.0
        for i in range(5):
            ln_Omega += b_coefficients[i] * (ln_T_star**i)

        # Calculate Omega(T*)
        Omega = math.exp(ln_Omega)

        numerator = 0.0266958 * math.sqrt(molar_mass * T)

        denominator = (sigma**2) * Omega

        # Calculate viscosity in muPa.s (microPascal-seconds)
        mu_uPa_s = numerator / denominator

        # Convert to Pa.s for return (1 muPa.s = 1e-6 Pa.s)
        mu_Pa_s = mu_uPa_s * 1.0e-6

        return mu_Pa_s


LemmonJacobsenUnary.load_data()
