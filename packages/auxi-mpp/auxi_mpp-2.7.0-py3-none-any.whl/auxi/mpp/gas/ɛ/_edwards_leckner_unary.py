from typing import Any, ClassVar

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty
from pydantic import Field

from ..state import GasUnaryTpxpLState
from ._edwards_felske_tien_unary import EdwardsFelskeTienUnary
from ._leckner_unary import LecknerUnary
from ._model import Model


class EdwardsLecknerUnary(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], floatPositiveOrZero]
):
    """
    Unary gas emissivity model composed of a model by Edwards, Felske and Tien and a model by Leckner.

    Returns:
       Emissivity [-].

    References:
        edwards1976, felske1974, leckner1972, modest2013
    """

    references: ClassVar[list[strNotEmpty]] = ["edwards1976", "felske1974", "leckner1972", "modest2013"]

    leckner_model: LecknerUnary = LecknerUnary()
    edwards_model: EdwardsFelskeTienUnary = EdwardsFelskeTienUnary()
    compound_scope: list[strCompoundFormula] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        self.compound_scope = self.leckner_model.compound_scope + self.edwards_model.compound_scope

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        pL: floatPositiveOrZero = 101325,
    ) -> float:
        """
        Calculate the emissivity of a unary gas.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"H2O":1.0}.
            pL: PARTIAL pressure path length. [Pa.m]

        Returns:
            Emissivity.
        """
        # validate state
        state = GasUnaryTpxpLState(T=T, p=p, x=x, pL=pL)

        # validate input
        if state.compound not in self.compound_scope:
            raise ValueError(
                f"{state.compound} is not a valid formula. Valid options are '{' '.join(self.compound_scope)}'."
            )

        # for either H2O or CO2 use Leckner's model
        if state.compound in self.leckner_model.compound_scope:
            epsilon = self.leckner_model.calculate(T=state.T, p=state.p, x=state.x, pL=state.pL)

        # for CO use Edwards's model
        else:
            epsilon = self.edwards_model.calculate(T=state.T, p=state.p, x=state.x, pL=state.pL)

        return epsilon
