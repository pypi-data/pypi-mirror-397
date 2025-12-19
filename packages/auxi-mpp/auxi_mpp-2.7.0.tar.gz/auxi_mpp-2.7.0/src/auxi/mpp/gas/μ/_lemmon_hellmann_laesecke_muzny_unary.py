from typing import Any, ClassVar

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty
from pydantic import Field

from ..state import GasUnaryTpxState
from ._hellmann_vogel_unary import HellmannVogelUnary
from ._laesecke_muzny_unary import LaeseckeMuznyUnary
from ._lemmon_jacobsen_unary import LemmonJacobsenUnary
from ._model import Model
from ._muzny_unary import MuznyUnary


class LemmonHellmannLaeseckeMuznyUnary(Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction]]):
    """
    Unary gas viscosity model.

    Returns:
       Viscosity in [Pa.s].

    References:
        hellmann2015, laesecke2017, lemmon2004, muzny2013

    """

    references: ClassVar[list[strNotEmpty]] = ["hellmann2015", "laesecke2017", "lemmon2004", "muzny2013"]

    hellmann_vogel_model: HellmannVogelUnary = HellmannVogelUnary()
    laesecke_muzny_model: LaeseckeMuznyUnary = LaeseckeMuznyUnary()
    muzny_model: MuznyUnary = MuznyUnary()
    lemmon_jacobsen_model: LemmonJacobsenUnary = LemmonJacobsenUnary()
    compound_scope: list[strCompoundFormula] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        self.compound_scope = list(
            set(self.hellmann_vogel_model.compound_scope)
            | set(self.laesecke_muzny_model.compound_scope)
            | set(self.muzny_model.compound_scope)
            | set(self.lemmon_jacobsen_model.compound_scope)
        )

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
    ) -> float:
        """
        Calculate unary gas viscosity.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Gas composition. [mol/mol] Eg. {"CO2": 1.0}.

        Returns:
            Viscosity in [Pa.s].
        """
        # validate state
        state = GasUnaryTpxState(T=T, p=p, x=x)

        # validate input
        if state.compound not in self.compound_scope:
            raise ValueError(
                f"{state.compound} is not a valid formula. Valid options are '{' '.join(self.compound_scope)}'."
            )

        # for H2O vapour
        if state.compound in self.hellmann_vogel_model.compound_scope:
            mu = self.hellmann_vogel_model.calculate(T=state.T, p=state.p, x=state.x)

        # for CO2 gas
        elif state.compound in self.laesecke_muzny_model.compound_scope:
            mu = self.laesecke_muzny_model.calculate(T=state.T, p=state.p, x=state.x)

        # for H2 gas
        elif state.compound in self.muzny_model.compound_scope:
            mu = self.muzny_model.calculate(T=state.T, p=state.p, x=state.x)

        # for Ar, N2, O2 or CO gas
        else:
            mu = self.lemmon_jacobsen_model.calculate(T=state.T, p=state.p, x=state.x)

        return mu
