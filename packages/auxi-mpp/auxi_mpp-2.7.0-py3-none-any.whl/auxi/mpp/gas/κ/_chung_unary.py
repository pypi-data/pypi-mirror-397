from typing import Any, ClassVar

from auxi.chemistry.validation import strCompoundFormula
from auxi.core import physicalconstants
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty
from pydantic import Field

from ..Cp._aly_unary import AlyUnary
from ..μ._lemmon_hellmann_laesecke_muzny_unary import LemmonHellmannLaeseckeMuznyUnary
from ._model import Model


class ChungUnary(Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction]]):
    """
    Unary gas thermal conductivity model by Chung et al. (1988).

    Returns:
       Thermal Conductivity [W/(m.K)].

    References:
        chung1988, aly1981
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}
    references: ClassVar[list[strNotEmpty]] = ["chung1988", "aly1981"]
    compound_scope: list[strCompoundFormula] = Field(default_factory=list)
    parameters: dict[str, dict[str, float]] = Field(default_factory=dict)

    lemmon_hellmann_laesecke_muzny_model: LemmonHellmannLaeseckeMuznyUnary = LemmonHellmannLaeseckeMuznyUnary()
    aly_cp_model: AlyUnary = AlyUnary()

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        self.compound_scope = list(
            set(self.data.keys())
            & set(self.aly_cp_model.compound_scope)
            & set(self.lemmon_hellmann_laesecke_muzny_model.compound_scope)
        )
        self.parameters: dict[str, dict[str, float]] = {c: self.data[c] for c in self.compound_scope}

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
            x: Chemical composition dictionary. [mol/mol] Eg. {"CO2": 1.0}.

        Returns:
            Thermal Conductivity.
        """
        compound = list(x.keys())
        compound = compound[0]

        # Eq. 9
        # get alpha, beta, Z to calculate Psi
        alpha = self._alpha(T, p, x)
        beta = self._beta(compound)
        Z = self._Z(T, compound)

        Psi = self._Psi(alpha, beta, Z)
        mu = self.lemmon_hellmann_laesecke_muzny_model.calculate(T=T, p=p, x=x)
        M = self.data[compound]["M"]

        kappa = (3.75 * mu * Psi * physicalconstants.R) / M  # adjusted for SI units

        return kappa

    def _Psi(self, alpha: float, beta: float, Z: float):
        numerator = 0.215 + 0.28288 * alpha - 1.061 * beta + 0.26665 * Z
        denominator = 0.6366 + beta * Z + 1.061 * alpha * beta

        Psi = 1 + alpha * (numerator / denominator)

        return Psi

    def _alpha(self, T: float, p: float, x: dict[str, float]):
        Cp = self.aly_cp_model.calculate(T=T, p=p, x=x)
        Cv = Cp - physicalconstants.R

        alpha = (Cv / physicalconstants.R) - (3 / 2)

        return alpha

    def _beta(self, compound: str):
        omega = self.data[compound]["ω"]

        beta = 0.7862 - 0.7109 * omega + 1.3168 * omega**2

        return beta

    def _Z(self, T: float, compound: str):
        Tc = self.data[compound]["Tc"]

        Z = 2.0 + 10.5 * (T / Tc) ** 2

        return Z


ChungUnary.load_data()
