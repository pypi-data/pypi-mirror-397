"""Test EdwardsLecknerBinary model."""

import pytest

from auxi.mpp.gas.ɛ._edwards_leckner_binary import EdwardsLecknerBinary
from auxi.mpp.gas.ɛ._edwards_leckner_unary import EdwardsLecknerUnary

from .test_parameters._pressure_length_inputs import pressure_length_testing_inputs, pressure_length_testing_inputs_err
from .test_parameters.binary_multi._binary_testing_inputs import (
    binary_error_test_inputs,
    binary_testing_inputs,
    unary_vs_binary_test_inputs,
)


# tests that should pass
@pytest.mark.parametrize("temperature, pressure, composition", binary_testing_inputs)
def test_edwards_leckner_binary(
    temperature: float,
    pressure: float,
    composition: dict[str, float],
):
    """Test temperature and composition limits."""
    model = EdwardsLecknerBinary()
    result = model.calculate(T=temperature, p=pressure, x=composition)

    assert result >= 0


# tests that should fail
@pytest.mark.parametrize("temperature, pressure, composition", binary_error_test_inputs)
def test_edwards_leckner_binary_errors(
    temperature: float,
    pressure: float,
    composition: dict[str, float],
):
    """Test if invalid inputs will fail."""
    model = EdwardsLecknerBinary()
    with pytest.raises(ValueError):
        model.calculate(T=temperature, p=pressure, x=composition)


@pytest.mark.parametrize(
    "pressure_length_product",
    pressure_length_testing_inputs,
)
def test_edwards_leckner_unary_pL(pressure_length_product: float):
    """Test temperature limits."""
    model = EdwardsLecknerBinary()
    result = model.calculate(T=1200, p=101325, x={"CO2": 0.5, "H2O": 0.5}, pL=pressure_length_product)

    assert result > 0


# pL tests that should fail
@pytest.mark.parametrize(
    "pressure_length_product",
    pressure_length_testing_inputs_err,
)
def test_edwards_leckner_unary_pL_errors(pressure_length_product: float):
    """Test if invalid inputs will fail."""
    model = EdwardsLecknerBinary()
    with pytest.raises(ValueError):
        model.calculate(T=1200, p=101325, x={"CO2": 0.5, "H2O": 0.5}, pL=pressure_length_product)


# test against the unary model
@pytest.mark.parametrize("temperature, pressure, composition", unary_vs_binary_test_inputs)
def test_ɛ_unary_vs_binary(temperature: float, pressure: float, composition: dict[str, float]):
    """Test if unary and binary model agrees."""
    unary_model = EdwardsLecknerUnary()
    binary_model = EdwardsLecknerBinary()

    compound = list(composition.keys())
    compound = compound[0]
    other_comps = ["CO2", "H2O", "CO"]
    other_comps.remove(compound)

    for comp in other_comps:
        unary_result = unary_model.calculate(T=temperature, p=pressure, x=composition)
        binary_result = binary_model.calculate(T=temperature, x={compound: composition[compound], comp: 0.0})

        assert abs(binary_result - unary_result) <= 1e-9


def test_loaded_parameters():
    """Test if parameters loads normally."""
    model = EdwardsLecknerBinary()

    assert model.property == "Total Emissivity"
    assert model.symbol == "ɛ"
    assert model.display_symbol == ""
    assert model.units == ""
    assert model.material == "Gas"
    assert model.references == ["edwards1976", "felske1974", "leckner1972", "modest2013"]

    assert sorted(model.compound_scope) == sorted(["CO", "H2O", "CO2"])


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = EdwardsLecknerBinary()
    result1 = model.calculate(T=1700, x={"CO2": 0.5, "CO": 0.5})
    result2 = model(T=1700, x={"CO2": 0.5, "CO": 0.5})

    assert abs(result1 - result2) < 1e-9
