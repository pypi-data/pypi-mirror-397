import math
from typing import Any, ClassVar

import numpy as np
from auxi.chemistry.validation import strCompoundFormula
from auxi.core.physicalconstants import R, c, h, k_B, σ
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty
from pydantic import Field
from scipy.special import exp1

from ._model import Model


class EdwardsFelskeTienUnary(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], floatPositiveOrZero]
):
    """
    Unary CO gas emissivity model by Edwards, Felske and Tien.

    Returns:
       Emissivity [-].

    References:
        edwards1976, felske1974, modest2013
        All equation references refer to reference modest2013.
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}
    references: ClassVar[list[strNotEmpty]] = ["edwards1976", "felske1974", "modest2013"]
    compound_scope: list[strCompoundFormula] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        self.compound_scope = list(self.data.keys())

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        pL: floatPositiveOrZero = 101325,
    ) -> float:
        """
        Calculate the emissivity of unary CO gas.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"CO": 1.0}.
            pL: Partial pressure path length. [Pa.m]

        Returns:
            Emissivity.
        """
        compound = list(x.keys())
        compound = compound[0]

        # get the relevant bands for the compound and the beam path length
        bands = list(self.data[compound]["λ"].keys())
        if x[compound] != 0.0:
            Length = pL / (p * x[compound])
        else:
            Length = pL / (p * 1e-9)

        # calculate the total emissivity by adding that of the individual bands together
        epsilon = 0.0
        for band in bands:
            epsilon += self._total_band_emissivity(T=T, p=p, x=x, L=Length, band_wavelength=band)

        return epsilon

    def _total_band_emissivity(self, T: float, p: float, x: dict[str, float], L: float, band_wavelength: float):
        compound = list(x.keys())
        compound = compound[0]

        # prepare parameters for calculating tau_0
        M = self.data[compound]["M"]
        if x[compound] != 0.0:
            p_a = p * x[compound]
        else:
            p_a = p * 1e-9
        density = self._density(T, p_a, M)
        X = self._X(density, L)
        omega = self._omega(T, compound, band_wavelength)

        # prepare parameters for calculating beta
        b0: float = self.data[compound]["λ"][band_wavelength]["b"][0]
        b1: float = self.data[compound]["λ"][band_wavelength]["b"][1]
        t_term = float((100 / T) ** 0.5)
        b = b1 * t_term + b0
        n: float = self.data[compound]["λ"][band_wavelength]["n"]
        P_e = self._P_e(p, b, p_a, n)
        beta_0_star: float = self.data[compound]["λ"][band_wavelength]["β_0*"]

        # prepare parameter for calculating band emissivity
        E_b_eta = self._blackbody_emissive_power(T, compound, band_wavelength)

        delta_tuples: list[str] = list(self.data[compound]["λ"][band_wavelength]["δ_m"].keys())
        epsilon_band = 0.0
        for tuple in delta_tuples:
            # calculate tau_0
            alpha_0 = self.data[compound]["λ"][band_wavelength]["α_0"][tuple] * 100
            Psi = self._Psi(T, compound, band_wavelength, tuple)
            Psi_0 = self._Psi(100, compound, band_wavelength, tuple)
            alpha = self._alpha(alpha_0, Psi, Psi_0)
            tau_0 = self._tau(alpha, X, omega)

            # calculate beta
            Phi = self._Phi(T, compound, band_wavelength, tuple)
            Phi_0 = self._Phi(100, compound, band_wavelength, tuple)
            beta = self._beta(T, beta_0_star, Phi, Phi_0, P_e)

            # calculate A
            A_star = self._A_star(tau_0, beta)
            A = self._A(A_star, omega)

            # get band emissivity
            epsilon_band += (E_b_eta * A) / (σ * T**4)
        return epsilon_band

    def _Psi(self, T: float, compound: str, band_wavelength: float, tuple: str):
        # Eq. 11.148
        m = self.data[compound]["m"]
        delta = self.data[compound]["λ"][band_wavelength]["δ_m"][tuple]
        g = self.data[compound]["g_m"]

        # part 1: (1 - exp(-sum(u_k(T) * delta_k)))
        sum_exponent = 0.0
        for k in range(1, m + 1):
            sum_exponent += self._u(k, T, compound) * delta[k]

        part1 = 1.0 - math.exp(-sum_exponent)

        # part 2: numerator / denominator
        product_numerator = 1.0
        product_denominator = 1.0

        for k in range(1, m + 1):
            uk = self._u(k, T, compound)
            gk = g[k]

            # numerator product term
            # this is the numerically truncated sum
            v0k = self._v0k(delta[k])
            product_numerator *= self._inner_sum(uk, delta[k], g[k], v0k, 1.0)

            # denominator product term (closed-form solution)
            # the sum \sum_{v_k=0}^{\infty} \binom{v_k+g_k-1}{v_k} (exp(-u_k))^v_k converges to (1 - exp(-u_k))^{-g_k}
            converged_sum = (1.0 - math.exp(-uk)) ** (-gk)
            product_denominator *= converged_sum

        part2 = product_numerator / product_denominator

        return part1 * part2

    def _Phi(self, T: float, compound: str, band_wavelength: float, tuple: str):
        # Eq. 11.149
        m = self.data[compound]["m"]
        delta = self.data[compound]["λ"][band_wavelength]["δ_m"][tuple]
        g = self.data[compound]["g_m"]

        # numerator / denominator
        product_numerator_phi = 1.0
        product_denominator_phi = 1.0

        for k in range(1, m + 1):
            uk = self._u(k, T, compound)
            gk = g[k]
            deltak_k = delta[k]
            v0k = self._v0k(deltak_k)

            # numerator product term
            product_numerator_phi *= self._inner_sum(uk, deltak_k, gk, v0k, 0.5)

            # denominator product term
            product_denominator_phi *= self._inner_sum(uk, deltak_k, gk, v0k, 1.0)

        # final calculation
        numerator = product_numerator_phi**2

        return numerator / product_denominator_phi

    def _inner_sum(self, uk: float, deltak: int, gk: int, v0k: int, exponent: float):
        # inner sum that applies to Eq 11.148 and 11.149
        total_sum = 0.0
        abs_deltak = math.fabs(deltak)
        v_max_limit: int = 100  # 100 iterations should be sufficiently high

        # to handle the factorials properly, we make us of x = a!/(b!*c!) -> ln(x) = ln(a!) - ln(b!) - ln(c!)
        # and then use ln((x - 1)!) -> lgamma(x), to ensure numerical stability
        ln_denominator1 = math.lgamma(gk)

        for vk in range(v0k, v_max_limit + 1):
            # ln((v_k + g_k + |delta_k| - 1)!) -> lgamma(v_k + g_k + abs_deltak)
            ln_numerator = math.lgamma(vk + gk + abs_deltak)

            # ln(v_k!) -> lgamma(v_k + 1)
            ln_denominator2 = math.lgamma(vk + 1.0)

            # calculate ln of the full term
            # ln(a / (b*c)) = ln(a) - ln(b) - ln(c)
            ln_fraction = ln_numerator - ln_denominator1 - ln_denominator2

            # exponentiate
            total_sum += math.exp((ln_fraction + (-uk * vk)) * exponent)  # exponent = 1/2 for sqrt version

        return total_sum

    def _u(self, k: int, T: float, compound: str):
        # Eq. 11.150a
        eta = self.data[compound]["η_m"]
        ukT = (h * c * eta[k] * 100) / (k_B * T)

        return ukT

    def _v0k(self, delta: int):
        # Eq. 11.150b
        if delta > 0:
            v0k = 0
        else:
            v0k = int(math.fabs(delta))
        return v0k

    def _alpha(self, alpha_0: float, Psi: float, Psi_0: float):
        # Eq. 11.144
        alpha = alpha_0 * (Psi / Psi_0)
        return alpha

    def _density(self, T: float, p_a: float, M: float):
        # Example 11.8
        density = (M * p_a) / (R * T)
        return density

    def _X(self, density: float, L: float):
        # Example 11.8
        return density * L

    def _omega(self, T: float, compound: str, band_wavelength: float):
        # Eq. 11.146
        omega_0 = self.data[compound]["λ"][band_wavelength]["ω_0"] * 100

        omega = omega_0 * (T / 100) ** 0.5

        return omega

    def _tau(self, alpha: float, X: float, omega: float):
        # Example 11.8
        tau = (alpha * X) / omega
        return tau

    def _P_e(self, p: float, b: float, p_a: float, n: float):
        # Eq. 11.147
        P_e = ((p / 101325) * (1 + (b - 1) * (p_a / p))) ** n
        return P_e

    def _beta(self, T: float, beta_0_star: float, Phi: float, Phi_0: float, P_e: float):
        # Eq. 11.145
        t_term = float((100 / T) ** 0.5)

        beta = beta_0_star * t_term * (Phi / Phi_0) * P_e
        return beta

    def _A_star(self, tau_0: float, beta: float) -> float:
        # Eq. 11.156

        # pre-calculate common sub-expressions for clarity
        # this term appears in all arguments
        common_denom_part = 1.0 + (beta / tau_0)

        # this term appears in term2 and term3
        sqrt_part_2_3 = math.sqrt((tau_0 / beta) / common_denom_part)

        # argument for 2*E_1
        term1_arg = math.sqrt((tau_0 * beta) / common_denom_part)

        # argument for E_1
        term2_arg = 0.5 * sqrt_part_2_3

        # argument for -E_1
        term3_arg = float(0.5 * (1.0 + 2.0 * beta) * sqrt_part_2_3)

        # argument for  ln
        ln_arg_denom = common_denom_part * (1.0 + 2.0 * beta)
        ln_arg = (tau_0 * beta) / ln_arg_denom

        # assemble the final A* value
        part1 = 2.0 * exp1(term1_arg)
        part2 = exp1(term2_arg)
        part3 = exp1(term3_arg)
        part4 = math.log(ln_arg)
        part5 = 2.0 * np.euler_gamma

        A_star = part1 + part2 - part3 + part4 + part5
        return A_star

    def _A(self, A_star: float, omega: float):
        # Eq. 11.143
        A = A_star * omega
        return A / 100

    def _blackbody_emissive_power(self, T: float, compound: str, band_wavelength: float):
        # Eq. 1.14
        eta = self.data[compound]["λ"][band_wavelength]["η_c"] * 100
        n = 1

        E_b_eta = (
            (2 * math.pi * h * ((c) ** 2) * (eta**3)) / ((n**2) * (math.exp((h * c * eta) / (n * k_B * T)) - 1))
        ) * 100

        return E_b_eta


EdwardsFelskeTienUnary.load_data()
