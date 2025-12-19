.. _unary-to-multi-classes-liquid-alloy:

Unary, Binary and Multi Classes
==============================

The unary, binary and multi-component model classes all function in the same way.
How to use them will be illustrated using the multi-component class.

Let ``ModelMulti`` represent an abstract multi-component model class.

Creating an Instance
--------------------

To create an instance of ``ModelMulti``, use the following line.

.. code-block::

   ExampleModel = ModelMulti()


Calculating the Physical Property
---------------------------------

To calculate the relevant property, the ``calculate()`` method is called on the model instance, while at the same time providing the conditions.

.. code-block::
   
   ExampleModel.calculate(T=temperature, p=pressure, x=composition)

where

| ``T: floatPositive``
| ``p: floatPositive``
| ``x: dict[str, floatFraction]``

All quantities provided should be in SI units and amount fractions should be given as mole fractions.
And if a temperature or pressure is not provided, standard temperature and pressure will be assumed.


Example; calculating the physical property of a 25% CO₂, 25% CO, 25% O₂, 25% N₂ mixture at 1100 K:

.. code-block::

   result = ExampleModel.calculate(T=1100, x={"CO2": 0.25, "CO": 0.25, "O2": 0.25, "N2": 0.25})

For ease of use,
``ExampleModel(T=temperature, p=pressure, x=composition)`` can also be used.
