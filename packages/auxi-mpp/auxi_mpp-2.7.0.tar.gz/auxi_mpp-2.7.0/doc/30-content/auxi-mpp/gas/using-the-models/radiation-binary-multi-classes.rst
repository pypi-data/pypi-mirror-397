.. _unary-to-multi-classes-liquid-alloy:

Radiation Binary and Multi Classes
==================================

The binary and multi-component gas mixture radiation property classes for gas function in the same way.

Let ``ModelBinary`` represent an abstract radiation binary class.

Creating an Instance
--------------------

To create an instance of ``ModelBinary``, use the following line.

.. code-block::

   ExampleModel = ModelBinary()


Calculating the Radiation Physical Property
-------------------------------------------

To calculate the relevant radiation property, the ``calculate()`` method is called on the model instance, while at the same time providing the conditions.

.. code-block::
   
   ExampleModel.calculate(T=temperature, p=pressure, x=composition, pL=pressure path length)

where

| ``T: floatPositive``
| ``p: floatPositive``
| ``x: dict[str, floatFraction]``
| ``pL: floatPositive``

All quantities provided should be in SI units and amount fractions should be given as mole fractions.
The partial pressures of the gases in the mixture are calculated from the amount fractions.
The pressure path length is the product of the total pressure and the beam length.
And if a temperature or pressure is not provided, standard temperature and pressure will be assumed.

.. note::
   Unlike with other models in ``auxi-mpp``, here the composition fractions does **not** need to add up to unity.
   For radiation properties, only the composition fractions of the radiating components are needed.
   Fractions of components regarded as transparent, like H\ :sub:`2`\, N\ :sub:`2`\, and O\ :sub:`2`\, can therefore be omitted.

Usage example:

.. code-block::

   result = ExampleModel.calculate(T=1200, p=101325, x={"CO": 0.2, "CO2": 0.4}, pL=300)

For ease of use,
``ExampleModel(T=temperature, p=pressure, x=composition, pL=pressure path length)`` can also be used.
