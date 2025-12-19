from typing import Any, ClassVar

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty
from pydantic import Field

from ..μ._lemmon_hellmann_laesecke_muzny_unary import LemmonHellmannLaeseckeMuznyUnary
from ._model import Model


class LemmonJacobsenUnary(Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction]]):
    """
    Unary gas thermal conductivity model by Lemmon and Jacobsen (2004).

    Returns:
       Thermal Conductivity [W/(m.K)].

    References:
        lemmon2004
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}
    references: ClassVar[list[strNotEmpty]] = ["lemmon2004"]
    compound_scope: list[strCompoundFormula] = Field(default_factory=list)
    parameters: dict[str, dict[str, Any]] = Field(default_factory=dict)

    lemmon_jacobsen_model: LemmonHellmannLaeseckeMuznyUnary = LemmonHellmannLaeseckeMuznyUnary()

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        self.compound_scope = list(set(self.data.keys()) & set(self.lemmon_jacobsen_model.compound_scope))
        self.parameters: dict[str, dict[str, Any]] = {c: self.data[c] for c in self.compound_scope}

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
    ) -> float:
        """
        Calculate the thermal conductivty of unary gas.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"O2": 1.0}.

        Returns:
            Thermal Conductivity.
        """
        compound = list(x.keys())
        compound = compound[0]

        # Eq. 5
        tau = self.data[compound]["Tc"] / T
        N = self.data[compound]["N"]
        t = self.data[compound]["t"]
        mu = self.lemmon_jacobsen_model.calculate(T=T, p=p, x=x)

        term1 = N[1] * (mu / 1e-6)
        term2 = N[2] * tau ** t[2]
        term3 = N[3] * tau ** t[3]

        kappa = term1 + term2 + term3

        return kappa / 1000  # convert from mW to W


LemmonJacobsenUnary.load_data()
