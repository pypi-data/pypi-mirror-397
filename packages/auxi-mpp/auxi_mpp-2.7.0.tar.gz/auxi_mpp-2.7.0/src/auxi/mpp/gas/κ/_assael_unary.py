import warnings
from typing import Any, ClassVar

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty
from pydantic import Field

from ._model import Model


class AssaelUnary(Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction]]):
    """
    Unary gas thermal conductivity model by Assael et al. (2011).

    Returns:
       Thermal Conductivity [W/(m.K)].

    References:
        assael2011
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}
    references: ClassVar[list[strNotEmpty]] = ["assael2011"]
    compound_scope: list[strCompoundFormula] = Field(default_factory=list)
    parameters: dict[str, dict[str, Any]] = Field(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        self.compound_scope = list(self.data.keys())
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
            x: Chemical composition dictionary. [mol/mol] Eg. {"H2": 1.0}.

        Returns:
            Thermal Conductivity.
        """
        if p != 101325:
            warnings.warn(
                f"{self.__class__.__name__} model is only implemented for atmospheric pressure at 101325 Pa.",
                UserWarning,
            )

        compound = list(x.keys())
        compound = compound[0]

        # Eq. 2
        T_bar = T / self.data[compound]["Tc"]
        A1: dict[int, float] = self.data[compound]["A1"]
        A2: dict[int, float] = self.data[compound]["A2"]

        numerator = 0.0
        for i in list(A1.keys()):
            numerator += A1[i] * (T_bar**i)

        denominator = 0.0
        for i in list(A2.keys()):
            denominator += A2[i] * (T_bar**i)

        kappa = numerator / denominator

        return kappa


AssaelUnary.load_data()
