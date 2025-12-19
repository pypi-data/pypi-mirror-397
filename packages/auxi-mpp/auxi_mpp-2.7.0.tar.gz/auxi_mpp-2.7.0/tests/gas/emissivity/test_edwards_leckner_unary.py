"""Test EdwardsLecknerUnary model."""

import pytest

from auxi.mpp.gas.ɛ._edwards_leckner_unary import EdwardsLecknerUnary

from .test_parameters._pressure_length_inputs import pressure_length_testing_inputs, pressure_length_testing_inputs_err
from .test_parameters._unary_testing_inputs import (
    unary_error_test_inputs,
    unary_testing_inputs,
)


@pytest.mark.parametrize(
    "temperature, pressure, composition",
    unary_testing_inputs,
)
def test_edwards_leckner_unary(temperature: float, pressure: float, composition: dict[str, float]):
    """Test temperature limits."""
    model = EdwardsLecknerUnary()
    result = model.calculate(T=temperature, p=pressure, x=composition)

    assert result > 0


# tests that should fail
@pytest.mark.parametrize("temperature, pressure, composition", unary_error_test_inputs)
def test_edwards_leckner_unary_errors(temperature: float, pressure: float, composition: dict[str, float]):
    """Test if invalid inputs will fail."""
    model = EdwardsLecknerUnary()
    with pytest.raises(ValueError):
        model.calculate(T=temperature, p=pressure, x=composition)


@pytest.mark.parametrize(
    "pressure_length_product",
    pressure_length_testing_inputs,
)
def test_edwards_leckner_unary_pL(pressure_length_product: float):
    """Test temperature limits."""
    model = EdwardsLecknerUnary()
    result = model.calculate(T=1200, p=101325, x={"CO2": 1.0}, pL=pressure_length_product)

    assert result > 0


# pL tests that should fail
@pytest.mark.parametrize(
    "pressure_length_product",
    pressure_length_testing_inputs_err,
)
def test_edwards_leckner_unary_pL_errors(pressure_length_product: float):
    """Test if invalid inputs will fail."""
    model = EdwardsLecknerUnary()
    with pytest.raises(ValueError):
        model.calculate(T=1200, p=101325, x={"CO2": 1.0}, pL=pressure_length_product)


def test_loaded_parameters():
    """Test if parameters loads normally."""
    model = EdwardsLecknerUnary()

    assert model.property == "Total Emissivity"
    assert model.symbol == "ɛ"
    assert model.display_symbol == ""
    assert model.units == ""
    assert model.material == "Gas"
    assert model.references == ["edwards1976", "felske1974", "leckner1972", "modest2013"]

    assert sorted(model.compound_scope) == sorted(["CO", "H2O", "CO2"])


def test_abstract_calc():
    """Test if calling the calculate() method works correctly."""
    model = EdwardsLecknerUnary()
    result1 = model.calculate(T=1700, x={"CO2": 1.0})
    result2 = model(T=1700, x={"CO2": 1.0})

    assert abs(result1 - result2) < 1e-9
