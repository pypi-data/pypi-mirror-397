"""Test WilkeBinary model."""

import warnings

import pytest

from auxi.mpp.gas.μ._lemmon_hellmann_laesecke_muzny_unary import LemmonHellmannLaeseckeMuznyUnary
from auxi.mpp.gas.μ._wilke_binary import WilkeBinary

from ..test_parameters.binary_multi._binary_testing_inputs import (
    binary_error_test_inputs,
    binary_testing_inputs,
    unary_vs_binary_test_inputs,
)


# tests that should pass
@pytest.mark.parametrize("temperature, pressure, composition", binary_testing_inputs)
def test_wilke_binary(temperature: float, pressure: float, composition: dict[str, float]):
    """Test temperature and composition limits."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = WilkeBinary()
        result = model.calculate(T=temperature, p=pressure, x=composition)

        assert abs(result) > 0


# tests that should fail
@pytest.mark.parametrize("temperature, pressure, composition", binary_error_test_inputs)
def test_wilke_binary_errors(temperature: float, pressure: float, composition: dict[str, float]):
    """Test if invalid inputs will fail."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = WilkeBinary()
        with pytest.raises(ValueError):
            model.calculate(T=temperature, p=pressure, x=composition)


# test if a warning is raised for outside model pressure.
def test_wilke_binary_warning():
    """Test if a warning is raised for outside model pressure."""
    model = WilkeBinary()

    # with warnings.catch_warnings():
    #     warnings.simplefilter("always")
    expected_msg_1 = r"LaeseckeMuznyUnary model is only implemented for atmospheric pressure at 101325 Pa\."
    expected_msg_2 = r"LemmonJacobsenUnary model is only implemented for atmospheric pressure at 101325 Pa\."

    with pytest.warns(UserWarning, match=expected_msg_1):
        # test warning of individual sub-models
        model.laesecke_muzny_model.calculate(T=1500, p=101500, x={"CO2": 1.0})
    with pytest.warns(UserWarning, match=expected_msg_2):
        model.lemmon_jacobsen_model.calculate(T=1500, p=101500, x={"N2": 1.0})


# test against the unary model
@pytest.mark.parametrize("temperature, pressure, composition", unary_vs_binary_test_inputs)
def test_mv_unary_vs_binary(temperature: float, pressure: float, composition: dict[str, float]):
    """Test if unary and binary model agrees."""
    unary_model = LemmonHellmannLaeseckeMuznyUnary()
    binary_model = WilkeBinary()

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
    model = WilkeBinary()

    assert model.property == "Dynamic Viscosity"
    assert model.symbol == "μ"
    assert model.display_symbol == "\\mu"
    assert model.units == "\\pascal\\second"
    assert model.material == "Gas"
    assert model.references == ["poling2001", "wilke1950"]

    assert sorted(model.compound_scope) == ["Ar", "CO", "CO2", "H2", "H2O", "N2", "O2"]
    assert model.hellmann_vogel_model.parameters["H2O"]["a0"] == 3.933738e-2
    assert model.laesecke_muzny_model.parameters["CO2"]["a0"] == 1749.354893188350
    assert model.lemmon_jacobsen_model.parameters["N2"]["b0"] == 0.431
    assert model.muzny_model.parameters["H2"]["a0"] == 2.09630e-1


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = WilkeBinary()
    result1 = model.calculate(T=1700, x={"CO2": 0.8, "N2": 0.2})
    result2 = model(T=1700, x={"CO2": 0.8, "N2": 0.2})

    assert abs(result1 - result2) < 1e-9
