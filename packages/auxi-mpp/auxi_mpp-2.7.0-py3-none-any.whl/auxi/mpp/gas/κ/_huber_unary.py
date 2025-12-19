import math
import warnings
from typing import Any, ClassVar

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty
from pydantic import Field

from ._model import Model


class HuberUnary(Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction]]):
    """
    Unary gas thermal conductivity model by Huber et al. (2012).

    Returns:
       Thermal Conductivity [W/(m.K)].

    References:
        huber2012
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}
    references: ClassVar[list[strNotEmpty]] = ["huber2012"]
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
            x: Chemical composition dictionary. [mol/mol] Eg. {"H2O": 1.0}.

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

        # Eq. 4
        T_bar = T / self.data[compound]["Tc"]
        numerator = math.sqrt(T_bar)

        Lk: dict[int, float] = self.data[compound]["Lk"]
        denominator = 0.0
        for k, Lk_value in Lk.items():
            denominator += Lk_value / (T_bar**k)

        kappa = numerator / denominator

        return kappa / 1000  # convert from mW to W


HuberUnary.load_data()
