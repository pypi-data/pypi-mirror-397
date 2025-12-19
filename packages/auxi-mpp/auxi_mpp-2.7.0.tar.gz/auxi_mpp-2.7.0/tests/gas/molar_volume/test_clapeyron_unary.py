"""Test LemmonHellmannLaeseckeMuznyUnary model."""

import warnings

import pytest

from auxi.mpp.gas.Vm._clapeyron_unary import ClapeyronUnary

from ..test_parameters._unary_testing_inputs import unary_error_test_inputs, unary_testing_inputs


@pytest.mark.parametrize(
    "temperature, pressure, composition",
    unary_testing_inputs,
)
def test_clapeyron_unary(temperature: float, pressure: float, composition: dict[str, float]):
    """Test temperature limits."""
    # ignore warnings to test only functionality.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = ClapeyronUnary()
        result = model.calculate(T=temperature, p=pressure, x=composition)

        assert result > 0


# tests that should fail
@pytest.mark.parametrize("temperature, pressure, composition", unary_error_test_inputs)
def test_clapeyron_unary_errors(temperature: float, pressure: float, composition: dict[str, float]):
    """Test if invalid inputs will fail."""
    # ignore warnings in tests to test only functionality of error raising.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = ClapeyronUnary()
        with pytest.raises(ValueError):
            model.calculate(T=temperature, p=pressure, x=composition)


def test_loaded_parameters():
    """Test if parameters loads normally."""
    model = ClapeyronUnary()

    assert model.property == "Molar Volume"
    assert model.symbol == "Vm"
    assert model.display_symbol == "\\bar{V}"
    assert model.units == "\\cubic\\meter\\per\\mol"
    assert model.material == "Gas"
    assert model.references == ["poling2001"]

    assert sorted(model.compound_scope) == ["Ar", "CO", "CO2", "H2", "H2O", "N2", "O2"]


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = ClapeyronUnary()
    result1 = model.calculate(T=1700, x={"CO2": 1.0})
    result2 = model(T=1700, x={"CO2": 1.0})

    assert abs(result1 - result2) < 1e-9
