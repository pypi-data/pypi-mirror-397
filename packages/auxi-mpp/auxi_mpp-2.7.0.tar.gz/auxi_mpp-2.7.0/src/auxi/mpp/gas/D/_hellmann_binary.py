import math
import warnings
from typing import Any, ClassVar

from auxi.chemistry import stoichiometry as stoic
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty
from pydantic import Field

from ..state._gas_binary_tpx_state import GasBinaryTpxState
from ..ρ._clapeyron_density_binary import ClapeyronDensityBinary
from ._model import Model


class HellmannBinary(Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction]]):
    """
    Gas binary diffusion coefficient model.

    Returns:
        Binary Diffusion Coefficient [m²/s].

    References:
        hellmann2019_co2, hellmann2024, hellmann2019_n2, hellmann2020, crusius2018
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}
    references: ClassVar[list[strNotEmpty]] = [
        "hellmann2019_co2",
        "hellmann2024",
        "hellmann2019_n2",
        "hellmann2020",
        "crusius2018",
    ]
    system_scope: list[strNotEmpty] = Field(default_factory=list)

    density_model: ClapeyronDensityBinary = Field(default_factory=ClapeyronDensityBinary)

    def model_post_init(self, __context: Any) -> None:
        """
        Load data from the YAML file and populates the compound scope.
        """
        super().model_post_init(__context)

        self.system_scope = list(self.data.keys())

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
    ) -> float:
        """
        Calculate binary diffusion coefficients for binary gases.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"H2O": 0.3, "CO2": 0.7}.

        Returns:
            Binary Diffusion Coefficient.
        """
        if p != 101325:
            warnings.warn(
                f"{self.__class__.__name__} model is only implemented for atmospheric pressure at 101325 Pa.",
                UserWarning,
            )

        # validate state
        state = GasBinaryTpxState(T=T, p=p, x=x)

        # get binary pair
        components = sorted(list(state.x.keys()))
        pair = f"{components[0]}-{components[1]}"

        # validate input
        if pair not in self.system_scope:
            raise ValueError(f"{pair} is not a valid pair. Valid options are '{' '.join(self.system_scope)}'.")

        # calculate S(T)
        # set up parameters
        T_bar = T
        T_cbrt = math.pow(T_bar, 1 / 3)  # T^(1/3)
        T_sixth = math.sqrt(T_cbrt)  # T^(1/6)
        params = self.data[pair]
        d1, d2, d3, d4, d5 = params["d1"], params["d2"], params["d3"], params["d4"], params["d5"]

        if pair in {"CO2-H2O", "Ar-H2O"}:
            # Eq. 12 hellmann2019 H2O-CO2

            term_d2 = d2 / T_sixth
            term_d3 = d3 * T_cbrt * math.exp(-T_cbrt)
            term_d4 = d4 * math.exp(-2 * T_cbrt)
            term_d5 = d5 * math.exp(-3 * T_cbrt)
            s_T = d1 + term_d2 + term_d3 + term_d4 + term_d5

        elif pair == "H2O-N2":
            # Eq. 11 hellmann2019 H2O-N2

            term_d2 = d2 / T_sixth
            term_d3 = d3 * math.exp(-T_cbrt)
            s_T = d1 + term_d2 + term_d3

        elif pair == "H2O-O2":
            # Eq. 14 hellmann2020 H2O-O2

            term_d2 = d2 * math.exp(-T_sixth)
            term_d3 = d3 * math.exp(-T_cbrt)
            s_T = d1 + T_sixth * (term_d2 + term_d3)

        else:  # CO2-N2
            # Eq. 14 crusius2018

            term_d2 = d2 / T_sixth
            term_d3 = d3 * T_sixth * math.exp(-T_cbrt)
            s_T = d1 + term_d2 + term_d3

        # Eq. 11 hellmann2019 H2O-CO2
        numerator = math.sqrt(T_bar)
        product_rho_D: float = (numerator / s_T) / 10000.0

        # calculate molar density (rho_m)
        # get density
        rho_kg_m3 = self.density_model.calculate(T=T, p=p, x=x)  # [kg/mol]

        # get average molar mass
        M_mix_kg_mol = 0.0
        for comp, mole_frac in x.items():
            mw = stoic.molar_mass(comp)
            M_mix_kg_mol += mole_frac * (mw / 1000.0)

        # convert to molar density
        rho_molar = rho_kg_m3 / M_mix_kg_mol  # [mol/m^3]

        # get the diffusion coefficient
        D = product_rho_D / rho_molar

        return D


HellmannBinary.load_data()
