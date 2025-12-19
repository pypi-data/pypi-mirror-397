from typing import Any, ClassVar

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.physicalconstants import R
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty
from pydantic import Field

from ..state._gas_binary_tpx_state import GasBinaryTpxState
from ._model import Model


class ClapeyronBinary(Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction]]):
    """
    Binary mixture, ideal gas molar volume model.

    Returns:
       Molar Volume in [m³/mol].

    References:
        poling2001
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}

    references: ClassVar[list[strNotEmpty]] = ["poling2001"]

    compound_scope: list[strCompoundFormula] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        data = ClapeyronBinary.data
        self.compound_scope = list(data.keys())

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
    ) -> float:
        """
        Calculate ideal binary gas mixture molar volume.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"N2":1.0}.

        Returns:
            Molar Volume in [m³/mol].
        """
        # validate state
        state = GasBinaryTpxState(T=T, p=p, x=x)

        # validate input
        for c in state.x:
            if c not in self.compound_scope:
                raise ValueError(f"{c} is not a valid formula. Valid options are '{' '.join(self.compound_scope)}'.")

        # ideal gas law
        mv_m3_mol = (R * state.T) / state.p

        return mv_m3_mol


ClapeyronBinary.load_data()
