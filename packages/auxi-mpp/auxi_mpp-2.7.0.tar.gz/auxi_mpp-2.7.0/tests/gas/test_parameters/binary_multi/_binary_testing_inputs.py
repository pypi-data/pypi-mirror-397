from .composition_parameters._binary_systems import composition_limits_binary, composition_limits_binary_err


# positive test temperature and composition tests
temperature_limits = [(298, 101325, {"CO2": 0.5, "N2": 0.5}), (2500, 101325, {"CO2": 0.5, "N2": 0.5})]

# positive test pressure tests
pressure_limits = [(1200, 50662.5, {"CO2": 0.5, "N2": 0.5}), (1200, 202650, {"CO2": 0.5, "N2": 0.5})]

# compilation of binary tests
binary_testing_inputs = temperature_limits + pressure_limits + composition_limits_binary

# error tests
temperature_limits_err = [(2501, 101325, {"CO2": 0.5, "N2": 0.5}), (297, 101325, {"CO2": 0.5, "H2O": 0.5})]
pressure_limits_err = [(1200, 50662, {"CO2": 0.5, "N2": 0.5}), (1200, 202651, {"CO2": 0.5, "H2O": 0.5})]
component_number_err = [(1200, 101325, {"CO2": 1.0}), (1200, 101325, {"CO2": 0.4, "H2O": 0.4, "N2": 0.2})]
invalid_comp_err = [(1200, 101325, {"CO2": 0.5, "NO": 0.5})]

# compilation of binary error tests
binary_error_test_inputs = (
    temperature_limits_err
    + pressure_limits_err
    + composition_limits_binary_err
    + component_number_err
    + invalid_comp_err
)

# compare unary and binary model performance
unary_vs_binary_test_inputs = [
    # temperature limits
    (298, 101325, {"CO2": 1.0}),
    (2500, 101325, {"CO2": 1.0}),
    # pure substance conditions
    (1200, 101325, {"CO2": 1.0}),
    (1200, 101325, {"N2": 1.0}),
    (1200, 101325, {"H2O": 1.0}),
    (1200, 101325, {"CO": 1.0}),
    (1200, 101325, {"H2": 1.0}),
    (1200, 101325, {"O2": 1.0}),
    (1200, 101325, {"Ar": 1.0}),
]
