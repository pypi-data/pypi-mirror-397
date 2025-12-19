import math
from typing import Any, ClassVar

from auxi.chemistry import stoichiometry as stoic
from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty
from pydantic import Field

from ..state._gas_binary_tpx_state import GasBinaryTpxState
from ._hellmann_vogel_unary import HellmannVogelUnary
from ._laesecke_muzny_unary import LaeseckeMuznyUnary
from ._lemmon_jacobsen_unary import LemmonJacobsenUnary
from ._model import Model
from ._muzny_unary import MuznyUnary


class WilkeBinary(Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction]]):
    """
    Binary gas viscosity model.

    Returns:
       Viscosity in [Pa.s].

    References:
        poling2001, wilke1950
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}  # Loaded from YAML

    references: ClassVar[list[strNotEmpty]] = ["poling2001", "wilke1950"]  # Reference to Poling et al. and Wilke

    hellmann_vogel_model: HellmannVogelUnary = HellmannVogelUnary()
    laesecke_muzny_model: LaeseckeMuznyUnary = LaeseckeMuznyUnary()
    muzny_model: MuznyUnary = MuznyUnary()
    lemmon_jacobsen_model: LemmonJacobsenUnary = LemmonJacobsenUnary()
    compound_scope: list[strCompoundFormula] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        self.compound_scope = (
            self.hellmann_vogel_model.compound_scope
            + self.laesecke_muzny_model.compound_scope
            + self.muzny_model.compound_scope
            + self.lemmon_jacobsen_model.compound_scope
        )

    def _calculate_phi_ij(
        self,
        mu_i: floatPositiveOrZero,
        mu_j: floatPositiveOrZero,
        M_i: floatPositiveOrZero,
        M_j: floatPositiveOrZero,
    ) -> floatPositiveOrZero:
        """
        Calculate the interaction parameter phi_ij.

        Returns:
            Interaction parameter phi_ij (dimensionless).
        """
        visc_ratio = mu_i / mu_j
        molar_mass_ratio_ji = M_j / M_i
        molar_mass_ratio_ij = M_i / M_j

        numerator = (1 + math.sqrt(visc_ratio) * (molar_mass_ratio_ji**0.25)) ** 2
        denominator = math.sqrt(8 * (1 + molar_mass_ratio_ij))

        phi_ij: floatPositiveOrZero = numerator / denominator
        return phi_ij

    def _calculate_mu_unary(
        self,
        compound: strCompoundFormula,
        T: floatPositiveOrZero,
        p: floatPositiveOrZero,
    ) -> floatPositiveOrZero:
        """
        Calculate unary gas viscosity for a given compound.

        Returns:
            Viscosity in [Pa.s].
        """
        mu_unary: floatPositiveOrZero = 0.0

        if compound == "H2":
            mu_unary = self.muzny_model.calculate(T=T, p=p, x={compound: 1.0})
        elif compound == "H2O":
            mu_unary = self.hellmann_vogel_model.calculate(T=T, p=p, x={compound: 1.0})
        elif compound == "CO2":
            mu_unary = self.laesecke_muzny_model.calculate(T=T, p=p, x={compound: 1.0})
        elif compound in ["N2", "O2", "Ar", "CO"]:
            mu_unary = self.lemmon_jacobsen_model.calculate(T=T, p=p, x={compound: 1.0})

        return mu_unary

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
    ) -> float:
        """
        Calculate binary gas mixture viscosity.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary (mole fractions). [mol/mol] Eg. {"N2": 0.8, "O2": 0.2}.

        Returns:
            Viscosity in [Pa.s].
        """
        # Validate state (T, p, x)
        state = GasBinaryTpxState(T=T, p=p, x=x)
        for c in state.x:
            if c not in self.compound_scope:
                raise ValueError(f"{c} is not a valid formula. Valid options are '{' '.join(self.compound_scope)}'.")

        # Calculate mixture viscosity using Wilke's method.
        mu_mix_Pa_s = 0.0

        for i in state.x.keys():
            denominator_sum = 0.0

            mu_i = self._calculate_mu_unary(compound=i, T=T, p=p)
            M_i = stoic.molar_mass(i)

            for j in state.x.keys():
                mu_j = self._calculate_mu_unary(compound=j, T=T, p=p)

                M_j = stoic.molar_mass(j)

                if i == j:
                    phi_ij = 1.0
                else:
                    phi_ij = self._calculate_phi_ij(mu_i, mu_j, M_i, M_j)

                denominator_sum += state.x[j] * phi_ij

            mu_mix_Pa_s += (state.x[i] * mu_i) / denominator_sum

        return mu_mix_Pa_s
