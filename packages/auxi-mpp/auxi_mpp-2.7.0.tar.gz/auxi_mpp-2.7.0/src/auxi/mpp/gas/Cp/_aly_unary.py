import math
import warnings
from typing import Any, ClassVar

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty
from pydantic import Field

from ..state import GasUnaryTpxState
from ._model import Model


class AlyUnary(Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction]]):
    """
    Unary gas constant pressure heat capacity model by Aly and Lee (1981).

    Returns:
       Constant Pressure Heat Capacity [J/(mol.K)].

    References:
        aly1981
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}
    references: ClassVar[list[strNotEmpty]] = ["aly1981"]
    compound_scope: list[strCompoundFormula] = Field(default_factory=list)
    parameters: dict[str, dict[str, float]] = Field(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        self.compound_scope = list(self.data.keys())
        self.parameters: dict[str, dict[str, float]] = {c: self.data[c] for c in self.compound_scope}

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
    ) -> float:
        """
        Calculate the constant pressure heat capacity of a unary gas.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"CO2": 1.0}.

        Returns:
            Constant Pressure Heat Capacity.
        """
        if p != 101325:
            warnings.warn(
                f"{self.__class__.__name__} model is only implemented for atmospheric pressure at 101325 Pa.",
                UserWarning,
            )

        # validate state
        state = GasUnaryTpxState(T=T, p=p, x=x)

        # validate input
        if state.compound not in self.compound_scope:
            raise ValueError(
                f"{state.compound} is not a valid formula. Valid options are '{' '.join(self.compound_scope)}'."
            )

        compound = list(x.keys())
        compound = compound[0]

        # Eq. 11
        Cp_params = self.data[compound]

        B = Cp_params["B"]
        C = Cp_params["C"]
        D = Cp_params["D"]
        E = Cp_params["E"]
        F = Cp_params["F"]

        # prevent division by zero errors
        if D == 0.0:
            term2 = C * 1.0
        else:
            term2 = C * ((D / T) / (math.sinh(D / T))) ** 2

        # prevent division by zero errors
        if F == 0.0:
            term3 = E * 1.0
        else:
            term3 = E * ((F / T) / (math.cosh(F / T))) ** 2

        Cp = B + term2 + term3

        return Cp * 4.184  # convert from cal to joule


AlyUnary.load_data()
