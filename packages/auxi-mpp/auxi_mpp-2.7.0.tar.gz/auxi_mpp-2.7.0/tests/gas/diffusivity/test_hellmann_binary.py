"""Test HellmannBinary model."""

import warnings

import pytest

from auxi.mpp.gas.D import HellmannBinary

from .test_parameters.binary._binary_testing_inputs import (
    binary_error_test_inputs,
    binary_testing_inputs,
)


# tests that should pass
@pytest.mark.parametrize("temperature, pressure, composition", binary_testing_inputs)
def test_hellmann_binary(temperature: float, pressure: float, composition: dict[str, float]):
    """Test temperature and composition limits."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = HellmannBinary()
        result = model.calculate(T=temperature, p=pressure, x=composition)

        assert abs(result) > 0


# tests that should fail
@pytest.mark.parametrize("temperature, pressure, composition", binary_error_test_inputs)
def test_hellmann_binary_errors(temperature: float, pressure: float, composition: dict[str, float]):
    """Test if invalid inputs will fail."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = HellmannBinary()
        with pytest.raises(ValueError):
            model.calculate(T=temperature, p=pressure, x=composition)


# test if a warning is raised for outside model pressure.
def test_burgess_unary_warning():
    """Test if a warning is raised for outside model pressure."""
    model = HellmannBinary()
    # below 1 atm
    expected_msg = r"HellmannBinary model is only implemented for atmospheric pressure at 101325 Pa\."
    with pytest.warns(UserWarning, match=expected_msg):
        model.calculate(T=1500, p=100000, x={"CO2": 0.5, "H2O": 0.5})

    # above 1 atm
    expected_msg = r"HellmannBinary model is only implemented for atmospheric pressure at 101325 Pa\."
    with pytest.warns(UserWarning, match=expected_msg):
        model.calculate(T=1500, p=101500, x={"CO2": 0.5, "H2O": 0.5})


def test_loaded_parameters():
    """Test if parameters loads normally."""
    model = HellmannBinary()

    assert model.property == "Diffusivity"
    assert model.symbol == "D"
    assert model.display_symbol == "D"
    assert model.units == "\\meter\\squared\\per\\second"
    assert model.material == "Gas"
    assert model.references == [
        "hellmann2019_co2",
        "hellmann2024",
        "hellmann2019_n2",
        "hellmann2020",
        "crusius2018",
    ]

    assert model.data["H2O-N2"]["d3"] == 148.37
    assert sorted(model.system_scope) == sorted(["Ar-H2O", "CO2-H2O", "H2O-N2", "H2O-O2", "CO2-N2"])


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = HellmannBinary()
    result1 = model.calculate(T=1700, x={"CO2": 0.8, "N2": 0.2})
    result2 = model(T=1700, x={"CO2": 0.8, "N2": 0.2})

    assert abs(result1 - result2) < 1e-9
