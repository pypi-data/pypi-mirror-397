from typing import Any, ClassVar

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty
from pydantic import Field

from ..state import GasUnaryTpxState
from ._assael_unary import AssaelUnary
from ._chung_unary import ChungUnary
from ._huber_unary import HuberUnary
from ._lemmon_jacobsen_unary import LemmonJacobsenUnary
from ._model import Model


class ChungLemmonHuberAssaelUnary(Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction]]):
    """
    Unary gas thermal conductivity model composed of models by Chung et al. (1988), Lemmon and Jacobsen (2004), Assael et al. (2011), and Huber et al. (2012).

    Returns:
       Thermal Conductivity [W/(m.K)].

    References:
        chung1988, lemmon2004, assael2011, huber2012
    """

    references: ClassVar[list[strNotEmpty]] = ["chung1988", "lemmon2004", "assael2011", "huber2012"]
    compound_scope: list[strCompoundFormula] = Field(default_factory=list)

    assael_model: AssaelUnary = AssaelUnary()
    chung_model: ChungUnary = ChungUnary()
    huber_model: HuberUnary = HuberUnary()
    lemmon_jacobsen_unary: LemmonJacobsenUnary = LemmonJacobsenUnary()

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        self.compound_scope = sorted(
            list(
                set(
                    self.assael_model.compound_scope
                    + self.chung_model.compound_scope
                    + self.huber_model.compound_scope
                    + self.lemmon_jacobsen_unary.compound_scope
                )
            )
        )

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
    ) -> float:
        """
        Calculate the thermal conductivty of a unary gas.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"CO2": 1.0}.

        Returns:
            Thermal Conductivity.
        """
        # validate state
        state = GasUnaryTpxState(T=T, p=p, x=x)

        # validate input
        if state.compound not in self.compound_scope:
            raise ValueError(
                f"{state.compound} is not a valid formula. Valid options are '{' '.join(self.compound_scope)}'."
            )

        # for H2O vapour
        if state.compound in self.huber_model.compound_scope:
            kappa = self.huber_model.calculate(T=state.T, p=state.p, x=state.x)

        # for H2 gas
        elif state.compound in self.assael_model.compound_scope:
            kappa = self.assael_model.calculate(T=state.T, p=state.p, x=state.x)

        # for N2 or O2 gas
        elif state.compound in self.lemmon_jacobsen_unary.compound_scope:
            kappa = self.lemmon_jacobsen_unary.calculate(T=state.T, p=state.p, x=state.x)

        # for CO or CO2 gas
        else:
            kappa = self.chung_model.calculate(T=state.T, p=state.p, x=state.x)

        return kappa
