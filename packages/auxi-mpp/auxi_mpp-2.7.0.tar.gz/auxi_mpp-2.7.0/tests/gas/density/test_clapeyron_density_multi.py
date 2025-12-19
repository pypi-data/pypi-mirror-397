"""Test MasonSaxenaMulti model."""

import warnings

import pytest

from auxi.mpp.gas.ρ import ClapeyronDensityBinary, ClapeyronDensityMulti

from ..test_parameters.binary_multi._multi_testing_inputs import (
    binary_vs_multi_test_inputs,
    multi3_vs_multi7_test_inputs,
    multi_error_test_inputs,
    multi_testing_inputs,
)


# tests that should pass
@pytest.mark.parametrize("temperature, pressure, composition", multi_testing_inputs)
def test_clapeyron_density_multi(temperature: float, pressure: float, composition: dict[str, float]):
    """Test temperature and composition limits."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = ClapeyronDensityMulti()
        result = model.calculate(T=temperature, p=pressure, x=composition)

        assert abs(result) > 0


# tests that should fail
@pytest.mark.parametrize("temperature, pressure, composition", multi_error_test_inputs)
def test_clapeyron_density_multi_errors(temperature: float, pressure: float, composition: dict[str, float]):
    """Test if invalid inputs will fail."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = ClapeyronDensityMulti()
        with pytest.raises(ValueError):
            model.calculate(T=temperature, p=pressure, x=composition)


# test against the binary model
@pytest.mark.parametrize("temperature, pressure, composition", binary_vs_multi_test_inputs)
def test_density_binary_vs_multi(temperature: float, pressure: float, composition: dict[str, float]):
    """Test if the binary and multi model agrees."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        binary_model = ClapeyronDensityBinary()
        multi_model = ClapeyronDensityMulti()

        seven_comps = {"CO2": 0.0, "H2O": 0.0, "N2": 0.0, "O2": 0.0, "H2": 0.0, "CO": 0.0, "Ar": 0.0}
        for comp, value in composition.items():
            if comp in seven_comps:
                seven_comps[comp] = value

        binary_result = binary_model.calculate(T=temperature, p=pressure, x=composition)
        multi_result = multi_model.calculate(T=temperature, p=pressure, x=seven_comps)

        assert abs(multi_result - binary_result) <= 1e-9


# test three and seven component input for the same three component system
@pytest.mark.parametrize("temperature, pressure, composition", multi3_vs_multi7_test_inputs)
def test_density_multi3_vs_multi7(temperature: float, pressure: float, composition: dict[str, float]):
    """Test if the multi model agrees when three and seven components are specified."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        multi3_model = ClapeyronDensityMulti()
        multi7_model = ClapeyronDensityMulti()

        seven_comps = {"CO2": 0.0, "H2O": 0.0, "N2": 0.0, "O2": 0.0, "H2": 0.0, "CO": 0.0, "Ar": 0.0}
        for comp, value in composition.items():
            if comp in seven_comps:
                seven_comps[comp] = value

        multi3_result = multi3_model.calculate(T=temperature, p=pressure, x=composition)
        multi7_result = multi7_model.calculate(T=temperature, p=pressure, x=seven_comps)

        assert abs(multi7_result - multi3_result) <= 1e-9


# test if a warning is raised for calling the class
def test_clapeyron_density_multi_warning():
    """Test if a warning is raised for calling the class."""
    expected_msg = r"ClapeyronMulti model logic is validated for binary systems only. Application to multi-component systems is untested and may yield inaccurate results\."
    with pytest.warns(UserWarning, match=expected_msg):
        ClapeyronDensityMulti().molar_volume_multi


def test_loaded_parameters():
    """Test if parameters loads normally."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = ClapeyronDensityMulti()

        assert model.property == "Density"
        assert model.symbol == "ρ"
        assert model.display_symbol == "\\rho"
        assert model.units == "\\kilo\\gram\\per\\cubic\\meter"
        assert model.material == "Gas"
        assert model.references == ["poling2001"]

        assert sorted(model.compound_scope) == ["Ar", "CO", "CO2", "H2", "H2O", "N2", "O2"]


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        model = ClapeyronDensityMulti()
        result1 = model.calculate(T=1700, x={"CO2": 0.6, "H2O": 0.2, "N2": 0.2})
        result2 = model(T=1700, x={"CO2": 0.6, "H2O": 0.2, "N2": 0.2})

        assert abs(result1 - result2) < 1e-9
