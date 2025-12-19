"""Test ChungLemmonHuberAssaelUnary model."""

import warnings

import pytest

from auxi.mpp.gas.κ import ChungLemmonHuberAssaelUnary

from ..test_parameters._unary_testing_inputs import unary_error_test_inputs, unary_testing_inputs


@pytest.mark.parametrize(
    "temperature, pressure, composition",
    unary_testing_inputs,
)
def test_chung_lemmon_huber_assael_unary(temperature: float, pressure: float, composition: dict[str, float]):
    """Test temperature limits."""
    # ignore warnings to test only functionality.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = ChungLemmonHuberAssaelUnary()
        result = model.calculate(T=temperature, p=pressure, x=composition)

        assert result > 0


# tests that should fail
@pytest.mark.parametrize("temperature, pressure, composition", unary_error_test_inputs)
def test_chung_lemmon_huber_assael_unary_errors(temperature: float, pressure: float, composition: dict[str, float]):
    """Test if invalid inputs will fail."""
    # ignore warnings in tests to test only functionality of error raising.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = ChungLemmonHuberAssaelUnary()
        with pytest.raises(ValueError):
            model.calculate(T=temperature, p=pressure, x=composition)


# test if a warning is raised for outside model pressure.
def test_chung_lemmon_huber_assael_unary_warning():
    """Test if a warning is raised for outside model pressure."""
    model = ChungLemmonHuberAssaelUnary()
    # test huberunary
    # below 1 atm
    expected_msg = r"AssaelUnary model is only implemented for atmospheric pressure at 101325 Pa\."
    with pytest.warns(UserWarning, match=expected_msg):
        model.assael_model.calculate(T=1500, p=100000, x={"H2": 1.0})

    # above 1 atm
    expected_msg = r"AssaelUnary model is only implemented for atmospheric pressure at 101325 Pa\."
    with pytest.warns(UserWarning, match=expected_msg):
        model.assael_model.calculate(T=1500, p=101500, x={"H2": 1.0})

    # test assaelunary
    # below 1 atm
    expected_msg = r"HuberUnary model is only implemented for atmospheric pressure at 101325 Pa\."
    with pytest.warns(UserWarning, match=expected_msg):
        model.huber_model.calculate(T=1500, p=100000, x={"H2O": 1.0})

    # above 1 atm
    expected_msg = r"HuberUnary model is only implemented for atmospheric pressure at 101325 Pa\."
    with pytest.warns(UserWarning, match=expected_msg):
        model.huber_model.calculate(T=1500, p=101500, x={"H2O": 1.0})


def test_loaded_parameters():
    """Test if parameters loads normally."""
    model = ChungLemmonHuberAssaelUnary()

    assert model.property == "Thermal Conductivity"
    assert model.symbol == "κ"
    assert model.display_symbol == "\\kappa"
    assert model.units == "\\watt\\per\\meter\\per\\kelvin"
    assert model.material == "Gas"
    assert model.references == ["chung1988", "lemmon2004", "assael2011", "huber2012"]

    assert model.chung_model.parameters["CO"]["ω"] == 0.0497
    assert model.lemmon_jacobsen_unary.parameters["O2"]["N"][3] == -4.262
    assert model.huber_model.parameters["H2O"]["Lk"][0] == 2.443221e-3
    assert model.assael_model.parameters["H2"]["Tc"] == 33.145

    assert sorted(model.compound_scope) == ["Ar", "CO", "CO2", "H2", "H2O", "N2", "O2"]


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = ChungLemmonHuberAssaelUnary()
    result1 = model.calculate(T=1700, x={"CO2": 1.0})
    result2 = model(T=1700, x={"CO2": 1.0})

    assert abs(result1 - result2) < 1e-9
