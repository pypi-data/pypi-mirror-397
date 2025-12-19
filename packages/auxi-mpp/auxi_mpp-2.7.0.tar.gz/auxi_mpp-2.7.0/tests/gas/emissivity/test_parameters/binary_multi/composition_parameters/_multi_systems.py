# multi systems -- positive tests
co2_co_h2o = [
    (1200, 101325, {"CO2": 1.0, "CO": 0.0, "H2O": 0.0}),
    (1200, 101325, {"CO2": 0.0, "CO": 1.0, "H2O": 0.0}),
    (1200, 101325, {"CO2": 0.0, "CO": 0.0, "H2O": 1.0}),
    (1200, 101325, {"CO2": 0.5, "CO": 0.5, "H2O": 0.0}),
    (1200, 101325, {"CO2": 0.0, "CO": 0.5, "H2O": 0.5}),
    (1200, 101325, {"CO2": 0.5, "CO": 0.0, "H2O": 0.5}),
    (1200, 101325, {"CO2": 0.34, "CO": 0.33, "H2O": 0.33}),
    (1200, 101325, {"CO2": 0.3, "CO": 0.3, "H2O": 0.3}),
]

# compilation of multi positive test parameters
composition_limits_multi = co2_co_h2o

# multi systems -- error tests
co2_co_h2o_err = [
    (1200, 101325, {"CO2": 1.01, "CO": -0.01, "H2O": 0.0}),
    (1200, 101325, {"CO2": 0.0, "CO": 1.01, "H2O": -0.01}),
    (1200, 101325, {"CO2": -0.01, "CO": 0.0, "H2O": 1.01}),
    (1200, 101325, {"CO2": 1.01, "CO": 0.0, "H2O": -0.01}),
    (1200, 101325, {"CO2": -0.01, "CO": 1.01, "H2O": 0.0}),
    (1200, 101325, {"CO2": 0.0, "CO": -0.01, "H2O": 1.01}),
    (1200, 101325, {"CO2": 0.34, "CO": 0.34, "H2O": 0.33}),
    (1200, 101325, {"CO2": 0.2, "CO": -0.01, "H2O": 0.2}),
]


# compilation of multi positive test parameters
composition_limits_multi_err = co2_co_h2o_err
