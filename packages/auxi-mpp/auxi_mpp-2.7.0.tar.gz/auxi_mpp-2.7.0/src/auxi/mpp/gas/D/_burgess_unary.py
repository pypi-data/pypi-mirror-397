import math
import warnings
from typing import Any, ClassVar

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty
from pydantic import Field

from ..state._gas_unary_tpx_state import GasUnaryTpxState
from ._model import Model


class BurgessUnary(Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction]]):
    """
    Gas self-diffusion coefficient model.

    Returns:
        Self-Diffusion Coefficient [m²/s].

    References:
        burgess2024, hellmann2023, suárez-iglesias2015
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}
    references: ClassVar[list[strNotEmpty]] = ["burgess2024", "hellmann2023", "suárez-iglesias2015"]
    compound_scope: list[strCompoundFormula] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        self.compound_scope = list(self.data.keys())

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
    ) -> float:
        """
        Calculate self-diffusion coefficients for a pure gas.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"H2": 1.0}.

        Returns:
            Self-Diffusion Coefficient.
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

        parameters = self.data[compound]

        # extended diffusion expression burgess2024
        ln_D = parameters["A"] + (parameters["B"] / T) + (parameters["C"] * math.log(T))

        D = math.exp(ln_D) / 10000  # convert from cm² to m²

        return D


BurgessUnary.load_data()
