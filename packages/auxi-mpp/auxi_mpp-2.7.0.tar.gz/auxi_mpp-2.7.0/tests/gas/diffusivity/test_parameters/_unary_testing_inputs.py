unary_testing_inputs = [
    # temperature and pressure limits
    (298, 101325, {"CO2": 1.0}),
    (298, 101325, {"CO": 1.0}),
    (1200, 101325, {"CO2": 1.0}),
    (1200, 101325, {"CO": 1.0}),
    (1200, 50662.5, {"CO2": 1.0}),
    (1200, 202650, {"CO2": 1.0}),
    (2500, 101325, {"CO2": 1.0}),
    (2500, 101325, {"CO": 1.0}),
]

unary_error_test_inputs = [
    # inside T boundaries?
    (2501, 101325, {"CO2": 1.0}),
    (297, 101325, {"CO": 1.0}),
    # inside p boundaries?
    (1200, 50662, {"CO2": 1.0}),
    (1200, 202651, {"CO": 1.0}),
    # inside x boundaries?
    (1200, 101325, {"Ar": -0.1}),
    (1200, 101325, {"CO2": 1.1}),
    # invalid compound provided
    (1200, 101325, {"NO": 1.0}),
    # too many compounds provided
    (1200, 101325, {"CO2": 0.5, "O2": 0.5}),
]
