import math
import warnings
from typing import Any, ClassVar

from auxi.chemistry.validation import strCompoundFormula
from auxi.core import physicalconstants
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty
from pydantic import Field

from ..Cp._aly_unary import AlyUnary
from ..state._gas_tpx_state import GasTpxState
from ._chung_lemmon_huber_assael_unary import ChungLemmonHuberAssaelUnary
from ._model import Model


class MasonSaxenaMulti(Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction]]):
    """
    Multi component gas thermal conductivity mixing rule by Mason and Saxena (1958), applied to unary models by Chung et al. (1988), Lemmon and Jacobsen (2004), Assael et al. (2011), and Huber et al. (2012).

    Returns:
       Thermal Conductivity [W/(m.K)].

    References:
        mason1958, chung1988, lemmon2004, assael2011, huber2012
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}
    references: ClassVar[list[strNotEmpty]] = ["mason1958", "chung1988", "lemmon2004", "assael2011", "huber2012"]
    compound_scope: list[strCompoundFormula] = Field(default_factory=list)
    parameters: dict[str, dict[str, float]] = Field(default_factory=dict)

    chung_lemmon_huber_assael_model: ChungLemmonHuberAssaelUnary = ChungLemmonHuberAssaelUnary()
    aly_cp_model: AlyUnary = AlyUnary()

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        self.compound_scope = list(
            set(self.chung_lemmon_huber_assael_model.compound_scope) & set(self.aly_cp_model.compound_scope)
        )
        self.parameters: dict[str, dict[str, float]] = {c: self.data[c] for c in self.compound_scope}

        warnings.warn(
            f"{self.__class__.__name__} model logic is validated for binary systems only. Application to multi-component systems is untested and may yield inaccurate results.",
            UserWarning,
        )

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
    ) -> float:
        """
        Calculate the thermal conductivty of a multi-component gas.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"CO2": 0.5, "H2O": 0.4, "O2": 0.1}.

        Returns:
            Thermal Conductivity.
        """
        # validate inputs
        state = GasTpxState(T=T, p=p, x=x)
        for c in state.x:
            if c not in self.compound_scope:
                raise ValueError(f"{c} is not a valid formula. Valid options are '{' '.join(self.compound_scope)}'.")

        # get pure component properties
        components = [comp for comp, _ in x.items()]
        unary_properties = self._unary_properties(T=T, p=p, components=components)

        # Eq. 20
        kappa_mix: float = 0.0
        for i in components:
            x_i = x[i]

            # avoid division by zero
            if x_i == 0.0:
                continue

            inner_sum = 0.0
            for k in components:
                if i == k:
                    continue

                x_k = x[k]
                G_ik = self._G_ik(
                    M_i=unary_properties[i]["M"],
                    M_k=unary_properties[k]["M"],
                    kappa_i_0=unary_properties[i]["kappa_0"],
                    kappa_k_0=unary_properties[k]["kappa_0"],
                )

                inner_sum += G_ik * (x_k / x_i)

            kappa_mix += unary_properties[i]["kappa"] / (1.0 + inner_sum)

        return kappa_mix

    def _unary_properties(self, T: float, p: float, components: list[str]):
        unary_properties: dict[str, dict[str, float]] = {}
        for comp in components:
            # get pure component thermal conductivity
            kappa = self.chung_lemmon_huber_assael_model.calculate(T=T, p=p, x={comp: 1.0})

            # Eq. 23
            C_pi = self.aly_cp_model.calculate(T=T, p=p, x={comp: 1.0})
            E_i = self._E_i(C_pi)
            kappa_0 = kappa / E_i

            # get molar mass
            M: float = self.data[comp]["M"]

            unary_properties[comp] = {"kappa": kappa, "kappa_0": kappa_0, "M": M}

        return unary_properties

    def _G_ik(self, M_i: float, M_k: float, kappa_i_0: float, kappa_k_0: float):
        # Eq. 21
        term1 = 1.065 / (2.0 * math.sqrt(2.0))
        term2 = (1.0 + M_i / M_k) ** (-0.5)

        term3_inner = ((kappa_i_0 / kappa_k_0) ** (0.5)) * ((M_i / M_k) ** (0.25))
        term3 = (1.0 + term3_inner) ** 2

        return term1 * term2 * term3

    def _E_i(self, C_pi: float):
        # Eq. 24
        E_i = 0.115 + 0.354 * (C_pi / physicalconstants.R)
        return E_i


MasonSaxenaMulti.load_data()
