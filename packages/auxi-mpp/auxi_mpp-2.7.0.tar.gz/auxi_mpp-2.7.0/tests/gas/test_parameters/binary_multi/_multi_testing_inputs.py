from .composition_parameters._binary_systems import composition_limits_binary
from .composition_parameters._multi_systems import (
    composition_limits_multi,
    composition_limits_multi_err,
)


# positive test temperature and composition tests
temperature_limits = [
    (298, 101325, {"CO2": 0.4, "H2O": 0.4, "N2": 0.2}),
    (2500, 101325, {"CO2": 0.25, "H2O": 0.25, "N2": 0.25, "CO": 0.25}),
]

# compilation of multi tests
multi_testing_inputs = temperature_limits + composition_limits_multi

temperature_limits_err = [
    (2501, 101325, {"CO2": 0.25, "N2": 0.25, "CO": 0.25, "O2": 0.25}),
    (297, 101325, {"CO2": 0.2, "N2": 0.2, "CO": 0.2, "O2": 0.2, "H2O": 0.2}),
]
add_to_unity_err = [
    (1200, 101325, {"CO2": 0.2, "H2O": 0.2, "N2": 0.2, "CO": 0.2, "O2": 0.1}),  # 68
    (1200, 101325, {"CO2": 0.2, "H2O": 0.2, "N2": 0.2, "CO": 0.2, "H2": 0.3}),
]
component_number_err = [(1200, 101325, {"CO2": 0.6, "H2O": 0.4}), (1200, 101325, {"CO2": 1.0})]
invalid_comp_err = [(1200, 101325, {"CO2": 0.4, "NO": 0.4, "H2O": 0.2})]  # 71

# compilation of multi error tests
multi_error_test_inputs = (
    temperature_limits_err + composition_limits_multi_err + add_to_unity_err + component_number_err + invalid_comp_err
)

# temperature limits for binary vs multi
temperature_limits_binary_vs_multi = [(298, 101325, {"CO2": 0.5, "H2O": 0.5}), (2500, 101325, {"CO2": 0.5, "N2": 0.5})]

# compare binary and multi model performance -- compilation of test parameters
binary_vs_multi_test_inputs = temperature_limits_binary_vs_multi + composition_limits_binary

# compare 3 vs 4 compounds provided with the same composition
multi3_vs_multi7_test_inputs = [
    (298, 101325, {"CO2": 0.4, "H2O": 0.4, "N2": 0.2}),
    (2500, 101325, {"CO2": 0.4, "N2": 0.4, "H2": 0.2}),
    (1200, 101325, {"CO2": 0.4, "H2": 0.4, "O2": 0.2}),
    (1200, 101325, {"CO2": 0.4, "O2": 0.4, "CO": 0.2}),
    (1200, 101325, {"CO2": 0.4, "CO": 0.4, "H2O": 0.2}),
    (1200, 101325, {"CO2": 0.4, "Ar": 0.4, "H2O": 0.2}),
    (1200, 101325, {"CO2": 0.4, "Ar": 0.4, "CO": 0.2}),
]
