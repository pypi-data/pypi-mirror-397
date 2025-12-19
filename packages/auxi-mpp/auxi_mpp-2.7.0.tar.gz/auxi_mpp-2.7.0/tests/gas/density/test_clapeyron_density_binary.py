"""Test WilkeBinary model."""

import warnings

import pytest

from auxi.mpp.gas.ρ._clapeyron_density_binary import ClapeyronDensityBinary
from auxi.mpp.gas.ρ._clapeyron_density_unary import ClapeyronDensityUnary

from ..test_parameters.binary_multi._binary_testing_inputs import (
    binary_error_test_inputs,
    binary_testing_inputs,
    unary_vs_binary_test_inputs,
)


# tests that should pass
@pytest.mark.parametrize("temperature, pressure, composition", binary_testing_inputs)
def test_clapeyron_density_binary(temperature: float, pressure: float, composition: dict[str, float]):
    """Test temperature and composition limits."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = ClapeyronDensityBinary()
        result = model.calculate(T=temperature, p=pressure, x=composition)

        assert abs(result) > 0


# tests that should fail
@pytest.mark.parametrize("temperature, pressure, composition", binary_error_test_inputs)
def test_clapeyron_density_binary_errors(temperature: float, pressure: float, composition: dict[str, float]):
    """Test if invalid inputs will fail."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = ClapeyronDensityBinary()
        with pytest.raises(ValueError):
            model.calculate(T=temperature, p=pressure, x=composition)


# test against the unary model
@pytest.mark.parametrize("temperature, pressure, composition", unary_vs_binary_test_inputs)
def test_mv_unary_vs_binary(temperature: float, pressure: float, composition: dict[str, float]):
    """Test if unary and binary model agrees."""
    unary_model = ClapeyronDensityUnary()
    binary_model = ClapeyronDensityBinary()

    compound = next(iter(composition.keys()))
    if compound != "CO2":
        two_comps = {"CO2": 0.0, f"{compound}": 1.0}
    else:
        two_comps = {"CO2": 1.0, "H2O": 0.0}

    unary_result = unary_model.calculate(T=temperature, p=pressure, x=composition)
    binary_result = binary_model.calculate(T=temperature, p=pressure, x=two_comps)

    assert abs(binary_result - unary_result) <= 1e-9


def test_loaded_parameters():
    """Test if parameters loads normally."""
    model = ClapeyronDensityBinary()

    assert model.property == "Density"
    assert model.symbol == "ρ"
    assert model.display_symbol == "\\rho"
    assert model.units == "\\kilo\\gram\\per\\cubic\\meter"
    assert model.material == "Gas"
    assert model.references == ["poling2001"]

    assert sorted(model.compound_scope) == ["Ar", "CO", "CO2", "H2", "H2O", "N2", "O2"]


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = ClapeyronDensityBinary()
    result1 = model.calculate(T=1700, x={"CO2": 0.8, "N2": 0.2})
    result2 = model(T=1700, x={"CO2": 0.8, "N2": 0.2})

    assert abs(result1 - result2) < 1e-9
