"""Test BurgessUnary model."""

import warnings

import pytest

from auxi.mpp.gas.D import BurgessUnary

from .test_parameters._unary_testing_inputs import unary_error_test_inputs, unary_testing_inputs


@pytest.mark.parametrize(
    "temperature, pressure, composition",
    unary_testing_inputs,
)
def test_burgess_unary(temperature: float, pressure: float, composition: dict[str, float]):
    """Test temperature limits."""
    # ignore warnings to test only functionality.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = BurgessUnary()
        result = model.calculate(T=temperature, p=pressure, x=composition)

        assert result > 0


# tests that should fail
@pytest.mark.parametrize("temperature, pressure, composition", unary_error_test_inputs)
def test_burgess_unary_errors(temperature: float, pressure: float, composition: dict[str, float]):
    """Test if invalid inputs will fail."""
    # ignore warnings in tests to test only functionality of error raising.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = BurgessUnary()
        with pytest.raises(ValueError):
            model.calculate(T=temperature, p=pressure, x=composition)


# test if a warning is raised for outside model pressure.
def test_burgess_unary_warning():
    """Test if a warning is raised for outside model pressure."""
    model = BurgessUnary()
    # below 1 atm
    expected_msg = r"BurgessUnary model is only implemented for atmospheric pressure at 101325 Pa\."
    with pytest.warns(UserWarning, match=expected_msg):
        model.calculate(T=1500, p=100000, x={"H2": 1.0})

    # above 1 atm
    expected_msg = r"BurgessUnary model is only implemented for atmospheric pressure at 101325 Pa\."
    with pytest.warns(UserWarning, match=expected_msg):
        model.calculate(T=1500, p=101500, x={"H2": 1.0})


def test_loaded_parameters():
    """Test if parameters loads normally."""
    model = BurgessUnary()

    assert model.property == "Diffusivity"
    assert model.symbol == "D"
    assert model.display_symbol == "D"
    assert model.units == "\\meter\\squared\\per\\second"
    assert model.material == "Gas"
    assert model.references == ["burgess2024", "hellmann2023", "suárez-iglesias2015"]

    assert model.data["CO2"]["A"] == 0.015
    assert sorted(model.compound_scope) == ["Ar", "CO", "CO2", "H2", "N2", "O2"]


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = BurgessUnary()
    result1 = model.calculate(T=1700, x={"CO2": 1.0})
    result2 = model(T=1700, x={"CO2": 1.0})

    assert abs(result1 - result2) < 1e-9
