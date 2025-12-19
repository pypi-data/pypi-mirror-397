"""Test LemmonHellmannLaeseckeMuznyUnary model."""

import warnings

import pytest

from auxi.mpp.gas.μ._lemmon_hellmann_laesecke_muzny_unary import LemmonHellmannLaeseckeMuznyUnary

from ..test_parameters._unary_testing_inputs import unary_error_test_inputs, unary_testing_inputs


@pytest.mark.parametrize(
    "temperature, pressure, composition",
    unary_testing_inputs,
)
def test_lemmon_hellmann_laesecke_muzny_unary(temperature: float, pressure: float, composition: dict[str, float]):
    """Test temperature limits."""
    # ignore warnings to test only functionality.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = LemmonHellmannLaeseckeMuznyUnary()
        result = model.calculate(T=temperature, p=pressure, x=composition)

        assert result > 0


# tests that should fail
@pytest.mark.parametrize("temperature, pressure, composition", unary_error_test_inputs)
def test_lemmon_hellmann_laesecke_muzny_unary_errors(
    temperature: float, pressure: float, composition: dict[str, float]
):
    """Test if invalid inputs will fail."""
    # ignore warnings in tests to test only functionality of error raising.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = LemmonHellmannLaeseckeMuznyUnary()
        with pytest.raises(ValueError):
            model.calculate(T=temperature, p=pressure, x=composition)


# test if a warning is raised for outside model pressure.
def test_lemmon_hellmann_laesecke_muzny_unary_warning():
    """Test if a warning is raised for outside model pressure."""
    model = LemmonHellmannLaeseckeMuznyUnary()
    expected_msg = r"LaeseckeMuznyUnary model is only implemented for atmospheric pressure at 101325 Pa\."
    with pytest.warns(UserWarning, match=expected_msg):
        model.laesecke_muzny_model.calculate(T=1500, p=101500, x={"CO2": 1.0})


def test_loaded_parameters():
    """Test if parameters loads normally."""
    model = LemmonHellmannLaeseckeMuznyUnary()

    assert model.property == "Dynamic Viscosity"
    assert model.symbol == "μ"
    assert model.display_symbol == "\\mu"
    assert model.units == "\\pascal\\second"
    assert model.material == "Gas"
    assert model.references == ["hellmann2015", "laesecke2017", "lemmon2004", "muzny2013"]

    assert model.hellmann_vogel_model.parameters["H2O"]["a0"] == 3.933738e-2
    assert model.laesecke_muzny_model.parameters["CO2"]["a0"] == 1749.354893188350
    assert model.lemmon_jacobsen_model.parameters["N2"]["b0"] == 0.431
    assert model.muzny_model.parameters["H2"]["a0"] == 2.09630e-1

    assert sorted(model.compound_scope) == ["Ar", "CO", "CO2", "H2", "H2O", "N2", "O2"]


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = LemmonHellmannLaeseckeMuznyUnary()
    result1 = model.calculate(T=1700, x={"CO2": 1.0})
    result2 = model(T=1700, x={"CO2": 1.0})

    assert abs(result1 - result2) < 1e-9
