"""Test AlyUnary model."""

import warnings

import pytest

from auxi.mpp.gas.Cp import AlyUnary

from ..test_parameters._unary_testing_inputs import unary_error_test_inputs, unary_testing_inputs


@pytest.mark.parametrize(
    "temperature, pressure, composition",
    unary_testing_inputs,
)
def test_aly_unary(temperature: float, pressure: float, composition: dict[str, float]):
    """Test temperature limits."""
    # ignore warnings to test only functionality.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = AlyUnary()
        result = model.calculate(T=temperature, p=pressure, x=composition)

        assert result > 0


# tests that should fail
@pytest.mark.parametrize("temperature, pressure, composition", unary_error_test_inputs)
def test_aly_unary_errors(temperature: float, pressure: float, composition: dict[str, float]):
    """Test if invalid inputs will fail."""
    # ignore warnings in tests to test only functionality of error raising.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = AlyUnary()
        with pytest.raises(ValueError):
            model.calculate(T=temperature, p=pressure, x=composition)


# test if a warning is raised for outside model pressure.
def test_aly_unary_warning():
    """Test if a warning is raised for outside model pressure."""
    model = AlyUnary()
    # test huberunary
    # below 1 atm
    expected_msg = r"AlyUnary model is only implemented for atmospheric pressure at 101325 Pa\."
    with pytest.warns(UserWarning, match=expected_msg):
        model.calculate(T=1500, p=100000, x={"CO2": 1.0})

    # above 1 atm
    expected_msg = r"AlyUnary model is only implemented for atmospheric pressure at 101325 Pa\."
    with pytest.warns(UserWarning, match=expected_msg):
        model.calculate(T=1500, p=101500, x={"N2": 1.0})


def test_loaded_parameters():
    """Test if parameters loads normally."""
    model = AlyUnary()

    assert model.property == "Constant Pressure Heat Capacity"
    assert model.symbol == "Cp"
    assert model.display_symbol == "C_p"
    assert model.units == "\\joule\\per\\mole\\per\\kelvin"
    assert model.material == "Gas"
    assert model.references == ["aly1981"]

    assert model.parameters["H2O"]["D"] == 2572.63

    assert sorted(model.compound_scope) == sorted(["Ar", "CO", "CO2", "H2", "H2O", "N2", "O2"])


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = AlyUnary()
    result1 = model.calculate(T=1700, x={"CO2": 1.0})
    result2 = model(T=1700, x={"CO2": 1.0})

    assert abs(result1 - result2) < 1e-9
