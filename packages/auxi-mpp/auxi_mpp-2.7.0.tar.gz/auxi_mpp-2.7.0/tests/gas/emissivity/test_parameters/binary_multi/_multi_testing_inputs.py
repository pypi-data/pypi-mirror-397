from .composition_parameters._binary_systems import composition_limits_binary
from .composition_parameters._multi_systems import (
    composition_limits_multi,
    composition_limits_multi_err,
)


# positive test temperature and composition tests
temperature_limits = [
    (298, 101325, {"CO2": 0.4, "CO": 0.4, "H2O": 0.2}),
    (2500, 101325, {"CO2": 0.25, "CO": 0.25, "H2O": 0.25}),
]

# positive test pressure tests
pressure_limits = [
    (1200, 50662.5, {"CO2": 0.4, "CO": 0.4, "H2O": 0.2}),
    (1200, 202650, {"CO2": 0.25, "CO": 0.25, "H2O": 0.25}),
]

# compilation of multi tests
multi_testing_inputs = temperature_limits + pressure_limits + composition_limits_multi

temperature_limits_err = [
    (2501, 101325, {"CO2": 0.25, "H2O": 0.25}),
    (297, 101325, {"CO2": 0.2, "H2O": 0.2, "CO": 0.2}),
]
pressure_limits_err = [
    (1200, 50662, {"CO2": 0.4, "CO": 0.4, "H2O": 0.2}),
    (1200, 202651, {"CO2": 0.25, "CO": 0.25, "H2O": 0.25}),
]
component_number_err = [(1200, 101325, {"CO2": 0.6, "CO": 0.4}), (1200, 101325, {"CO2": 1.0})]
invalid_comp_err = [(1200, 101325, {"CO2": 0.4, "N2": 0.4, "CO": 0.2})]

# compilation of multi error tests
multi_error_test_inputs = (
    temperature_limits_err
    + pressure_limits_err
    + composition_limits_multi_err
    + component_number_err
    + invalid_comp_err
)

# test pressure length inputs
pressure_length: list[
    tuple[
        float,
        float,
        dict[str, float],
        float,
    ]
] = [
    (1200, 101325, {"CO2": 0.25, "CO": 0.5, "H2O": 0.25}, 0),
    (1200, 101325, {"CO2": 0.25, "CO": 0.5, "H2O": 0.25}, 100),
    (1200, 101325, {"CO2": 0.25, "CO": 0.5, "H2O": 0.25}, 100000),
    (1200, 101325, {"CO2": 0.25, "CO": 0.5, "H2O": 0.25}, 500000),
]

# temperature limits for binary vs multi
temperature_limits_binary_vs_multi = [(298, 101325, {"CO2": 0.5, "CO": 0.5}), (2500, 101325, {"CO2": 0.5, "H2O": 0.5})]

# compare binary and multi model performance -- compilation of test parameters
binary_vs_multi_test_inputs = temperature_limits_binary_vs_multi + composition_limits_binary

# test for pressure length product range
pressure_length_testing_inputs = [0.001, 100000, 500000]
pressure_length_testing_inputs_err = [0, 500001]
