.. _examples:

Examples
========

We here present a few examples of how to integrate ``auxi-mpp`` into your Python code, how it can be used directly for estimating physical properties, as well as using it in a loop to generate a graph.

Integrable Function
-------------------

Let's say we need to integrate a single function, that can estimate slag viscosity based on a temperature and composition input, into our existing Python code.
Since ``auxi-mpp`` provides three separate model classes for unary, binary and multi-component systems, we will have to combine these:

.. code-block::

    from auxi.mpp.slag.μ import GrundyKimBroschBinary, GrundyKimBroschMulti, GrundyKimBroschUnary

    def my_viscosity_function(T: float, x: dict[str, float]):
        """My viscosity function."""

        # if only one component was provided, use the unary model class
        if len(x) == 1:
            model = GrundyKimBroschUnary()
            result = model.calculate(T=T, x=x)

        # if two components were provided, use the binary model class
        elif len(x) == 2:
            model = GrundyKimBroschBinary(esf=my_esf)
            result = model.calculate(T=T, x=x)

        # for 3 or more components, use the multi-component class
        else:
            model = GrundyKimBroschMulti(esf=my_esf)
            result = model.calculate(T=T, x=x)

        return result


This Python function, ``my_viscosity_function(T, x)``, will return the viscosity of a slag of any number of components and can be integrated into any other set of Python code where it can be called iteratively.

The Equilibrium Slag Function (:term:`ESF`) in this example has the label of ``my_esf``, and it will take the form:

.. code-block::

    def my_esf(
        T: float, p: float, x: dict[str, float], a: dict[str, dict[str, float]]
    ) -> tuple[dict[str, float], dict[str, float]]:
        """My Equilibrium Slag Function."""
        # function logic

        return normalised_eq_composition, bond_fractions

See the :ref:`esf-example` section for a guide on setting it up.


Direct Estimation
-----------------

Let's say we simply want to quickly estimate the thermal conductivity of pure liquid iron without needing to integrate a thermal conductivity calculator into our code.
We can then take the following approach:

.. code-block::

    from auxi.mpp.liquid_alloy import κ

    model = κ.WiedemannFranzUnary()
    result = model(T=1500, x={"Fe": 1.0})

    print(f"Pure Iron Thermal Conductivity at 1500 K: {result:.2f} {model.units}")

This should print out ``Pure Iron Thermal Conductivity at 1500 K: 28.28 \watt\per\meter\per\kelvin``.

Notice how the model instance was created here; the line ``model = κ.WiedemannFranzUnary()`` was used.
Calling the model class from the physical property symbol like this can enhance code readability, as we immediately know that the ``WiedemannFranzUnary`` model class is a thermal conductivity model, as it is called from ``κ`` (kappa).


Generating a Graph
------------------

Let's say we would like to generate a graph of the electrical conductivity versus silica content of a CAS (CaO-Al₂O₃-SiO₂) system at 1700 K, where the ratio of calcium oxide and alumina is one.
For this, we need to conduct multiple calculations as we incrementally change the silica content.

For our example we use the ``HundermarkMulti`` model class:

.. code-block::

    import matplotlib.pyplot as plt
    import numpy as np
    from auxi.mpp.slag.σ import HundermarkMulti


    # my electrical conductivity function
    def electrical_conductivity_function(T: float, x_SiO2: float):
        model = HundermarkMulti()

        Al2O3_CaO_frac = (1 - x_SiO2) / 2
        result = model(T=T, x={"SiO2": x_SiO2, "Al2O3": Al2O3_CaO_frac, "CaO": Al2O3_CaO_frac})

        return result


    # create the input range for SiO2 from 0.0 to 1.0 with 21 steps
    x_SiO2_values = np.linspace(0.0, 1.0, 21)

    # calculate the electrical conductivity values by applying the function to the x_SiO2_values
    y_values: list[float] = []
    for x_SiO2 in x_SiO2_values:
        y_values.append(electrical_conductivity_function(1700, x_SiO2))

    # plot the results
    plt.figure(figsize=(8, 6))
    plt.plot(x_SiO2_values, y_values)
    plt.title("Electrical Conductivity vs SiO2 content for the CAS system.")
    plt.xlabel("SiO2 mole fraction")
    plt.ylabel("Electrical Conductivity (S/m)")

    # display the plot
    plt.show()

This should generate the following:

.. figure:: ./ec-vs-sio2-cas-example.png
   :width: 800
   :alt: Graph output of the above example.
   :align: center

   The output of the above example.