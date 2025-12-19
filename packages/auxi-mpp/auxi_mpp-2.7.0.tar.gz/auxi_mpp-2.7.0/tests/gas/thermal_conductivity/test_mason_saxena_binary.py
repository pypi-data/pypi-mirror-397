"""Test MasonSaxenaBinary model."""

import warnings

import pytest

from auxi.mpp.gas.κ import ChungLemmonHuberAssaelUnary, MasonSaxenaBinary

from ..test_parameters.binary_multi._binary_testing_inputs import (
    binary_error_test_inputs,
    binary_testing_inputs,
    unary_vs_binary_test_inputs,
)


# tests that should pass
@pytest.mark.parametrize("temperature, pressure, composition", binary_testing_inputs)
def test_mason_saxena_binary(temperature: float, pressure: float, composition: dict[str, float]):
    """Test temperature and composition limits."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = MasonSaxenaBinary()
        result = model.calculate(T=temperature, p=pressure, x=composition)

        assert abs(result) > 0


# tests that should fail
@pytest.mark.parametrize("temperature, pressure, composition", binary_error_test_inputs)
def test_mason_saxena_binary_errors(temperature: float, pressure: float, composition: dict[str, float]):
    """Test if invalid inputs will fail."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = MasonSaxenaBinary()
        with pytest.raises(ValueError):
            model.calculate(T=temperature, p=pressure, x=composition)


# test against the unary model
@pytest.mark.parametrize("temperature, pressure, composition", unary_vs_binary_test_inputs)
def test_tc_unary_vs_binary(temperature: float, pressure: float, composition: dict[str, float]):
    """Test if unary and binary model agrees."""
    unary_model = ChungLemmonHuberAssaelUnary()
    binary_model = MasonSaxenaBinary()

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
    model = MasonSaxenaBinary()

    assert model.property == "Thermal Conductivity"
    assert model.symbol == "κ"
    assert model.display_symbol == "\\kappa"
    assert model.units == "\\watt\\per\\meter\\per\\kelvin"
    assert model.material == "Gas"
    assert model.references == ["mason1958", "chung1988", "lemmon2004", "assael2011", "huber2012"]

    assert sorted(model.compound_scope) == ["Ar", "CO", "CO2", "H2", "H2O", "N2", "O2"]
    assert model.chung_lemmon_huber_assael_model.assael_model.parameters["H2"]["Tc"] == 33.145
    assert model.aly_cp_model.parameters["CO"]["B"] == 6.95854


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = MasonSaxenaBinary()
    result1 = model.calculate(T=1700, x={"CO2": 0.8, "N2": 0.2})
    result2 = model(T=1700, x={"CO2": 0.8, "N2": 0.2})

    assert abs(result1 - result2) < 1e-9
