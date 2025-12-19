"""Test EdwardsLecknerMulti model."""

import pytest

from auxi.mpp.gas.ɛ._edwards_leckner_binary import EdwardsLecknerBinary
from auxi.mpp.gas.ɛ._edwards_leckner_multi import EdwardsLecknerMulti

from .test_parameters._pressure_length_inputs import pressure_length_testing_inputs, pressure_length_testing_inputs_err
from .test_parameters.binary_multi._multi_testing_inputs import (
    multi_error_test_inputs,
    multi_testing_inputs,
)
from .test_parameters.binary_multi.composition_parameters._binary_systems import composition_limits_binary


# tests that should pass
@pytest.mark.parametrize("temperature, pressure, composition", multi_testing_inputs)
def test_edwards_leckner_multi(
    temperature: float,
    pressure: float,
    composition: dict[str, float],
):
    """Test temperature and composition limits."""
    model = EdwardsLecknerMulti()
    result = model.calculate(T=temperature, p=pressure, x=composition)

    assert result > 0


# tests that should fail
@pytest.mark.parametrize("temperature, pressure, composition", multi_error_test_inputs)
def test_edwards_leckner_multi_errors(
    temperature: float,
    pressure: float,
    composition: dict[str, float],
):
    """Test if invalid inputs will fail."""
    model = EdwardsLecknerMulti()
    with pytest.raises(ValueError):
        model.calculate(T=temperature, p=pressure, x=composition)


@pytest.mark.parametrize(
    "pressure_length_product",
    pressure_length_testing_inputs,
)
def test_edwards_leckner_unary_pL(pressure_length_product: float):
    """Test temperature limits."""
    model = EdwardsLecknerMulti()
    result = model.calculate(T=1200, p=101325, x={"CO2": 0.4, "H2O": 0.3, "CO": 0.3}, pL=pressure_length_product)

    assert result > 0


# pL tests that should fail
@pytest.mark.parametrize(
    "pressure_length_product",
    pressure_length_testing_inputs_err,
)
def test_edwards_leckner_unary_pL_errors(pressure_length_product: float):
    """Test if invalid inputs will fail."""
    model = EdwardsLecknerMulti()
    with pytest.raises(ValueError):
        model.calculate(T=1200, p=101325, x={"CO2": 0.4, "H2O": 0.3, "CO": 0.3}, pL=pressure_length_product)


# test against the binary model
@pytest.mark.parametrize("temperature, pressure, composition", composition_limits_binary)
def test_ɛ_binary_vs_multi(temperature: float, pressure: float, composition: dict[str, float]):
    """Test if the binary and multi model agrees."""
    binary_model = EdwardsLecknerBinary()
    multi_model = EdwardsLecknerMulti()

    six_comps = {"CO2": 0.0, "CO": 0.0, "H2O": 0.0}
    for comp, value in composition.items():
        if comp in six_comps:
            six_comps[comp] = value

    binary_result = binary_model.calculate(T=temperature, p=pressure, x=composition)
    multi_result = multi_model.calculate(T=temperature, p=pressure, x=six_comps)

    assert abs(multi_result - binary_result) <= 1e-9


def test_loaded_parameters():
    """Test if parameters loads normally."""
    model = EdwardsLecknerMulti()

    assert model.property == "Total Emissivity"
    assert model.symbol == "ɛ"
    assert model.display_symbol == ""
    assert model.units == ""
    assert model.material == "Gas"
    assert model.references == ["edwards1976", "felske1974", "leckner1972", "modest2013"]

    assert sorted(model.compound_scope) == sorted(["CO", "H2O", "CO2"])


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = EdwardsLecknerMulti()
    result1 = model.calculate(T=1700, x={"CO2": 0.25, "CO": 0.25, "H2O": 0.25})
    result2 = model(T=1700, x={"CO2": 0.25, "CO": 0.25, "H2O": 0.25})

    assert abs(result1 - result2) < 1e-9
