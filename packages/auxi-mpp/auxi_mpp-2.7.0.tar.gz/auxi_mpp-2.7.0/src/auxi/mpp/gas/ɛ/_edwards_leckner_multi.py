from typing import Any, ClassVar

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty
from pydantic import Field

from ..state import GasTpxpLState
from ._edwards_felske_tien_unary import EdwardsFelskeTienUnary
from ._leckner_binary import LecknerBinary
from ._leckner_unary import LecknerUnary
from ._model import Model


class EdwardsLecknerMulti(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], floatPositiveOrZero]
):
    """
    Multi component gas emissivity model composed of a model by Edwards, Felske and Tien and a model by Leckner.

    Returns:
       Emissivity [-].

    References:
        edwards1976, felske1974, leckner1972, modest2013
    """

    references: ClassVar[list[strNotEmpty]] = ["edwards1976", "felske1974", "leckner1972", "modest2013"]

    leckner_model: LecknerUnary = LecknerUnary()
    leckner_binary_model: LecknerBinary = LecknerBinary()
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
        Calculate the emissivity of a multi component gas mixture.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"H2O": 0.5, "CO2": 0.3, "CO": 0.2}.
            pL: Pressure path length. [Pa.m]

        Returns:
            Emissivity.
        """
        # validate state
        state = GasTpxpLState(T=T, p=p, x=x, pL=pL)

        # validate input
        for comp in state.compounds:
            if comp not in self.compound_scope:
                raise ValueError(f"{comp} is not a valid formula. Valid options are '{' '.join(self.compound_scope)}'.")

        # if both CO2 and H2O are present, use Leckner's binary model which accounts for band overlap
        pathLength = state.pL / state.p
        if set(self.leckner_model.compound_scope).issubset(set(state.compounds)):
            epsilon = self.leckner_binary_model.calculate(T=T, p=p, x={"CO2": x["CO2"], "H2O": x["H2O"]}, pL=pL)

            # get epsilon for the rest of the compounds
            non_co2_h2o_compounds = [x for x in state.compounds if x not in {"CO2", "H2O"}]
            for comp in non_co2_h2o_compounds:
                # if the partial pressure of a component in the mixture is zero, there should be zero contribution
                if state.x[comp] == 0.0:
                    epsilon += 0.0
                    continue
                # if comp = 'CO' use Edward's model to calculate
                if comp in self.edwards_model.compound_scope:
                    p_a = state.p * state.x[comp]
                    epsilon += self.edwards_model.calculate(
                        T=state.T, p=state.p, x={comp: state.x[comp]}, pL=p_a * pathLength
                    )

        # if both CO2 and H2O are NOT present
        else:
            epsilon = 0.0
            for comp in state.compounds:
                # if the partial pressure of a component in the mixture is zero, there should be zero contribution
                if state.x[comp] == 0.0:
                    epsilon += 0.0
                    continue
                # for either H2O or CO2 use Leckner's model
                if comp in self.leckner_model.compound_scope:
                    p_a = state.p * state.x[comp]
                    epsilon += self.leckner_model.calculate(
                        T=state.T, p=state.p, x={comp: state.x[comp]}, pL=p_a * pathLength
                    )
                # for CO use Edwards's model
                elif comp in self.edwards_model.compound_scope:
                    p_a = state.p * state.x[comp]
                    epsilon += self.edwards_model.calculate(
                        T=state.T, p=state.p, x={comp: state.x[comp]}, pL=p_a * pathLength
                    )

        return epsilon
