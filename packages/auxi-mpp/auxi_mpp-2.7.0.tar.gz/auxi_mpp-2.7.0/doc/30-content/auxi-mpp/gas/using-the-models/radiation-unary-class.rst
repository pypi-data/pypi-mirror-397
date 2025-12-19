.. _unary-to-multi-classes-liquid-alloy:

Radiation Unary Class
=====================

The unary gas radiation property class functions similar to the binary and multi-component classes, with the only difference lying in the definition of the pressure path length input, as we shall see shortly.

Let ``ModelUnary`` represent an abstract radiation unary class.

Creating an Instance
--------------------

To create an instance of ``ModelUnary``, use the following line.

.. code-block::

   ExampleModel = ModelUnary()


Calculating the Radiation Physical Property
-------------------------------------------

To calculate the relevant radiation property, the ``calculate()`` method is called on the model instance, while at the same time providing the conditions.

.. code-block::
   
   ExampleModel.calculate(T=temperature, p=pressure, x=composition, pL=PARTIAL pressure path length)

where

| ``T: floatPositive``
| ``p: floatPositive``
| ``x: dict[str, floatFraction]``
| ``pL: floatPositive``

All quantities provided should be in SI units and amount fractions should be given as mole fractions.
The partial pressure of the gas are calculated from the provided amount fraction.
The pressure path length here is the product of the **partial pressure** and the beam length.
And if a temperature or pressure is not provided, standard temperature and pressure will be assumed.

.. note::
   Providing a mole fraction for a pure gas other than 1.0 is indeed unphysical.
   However, this allows calculation of the radiation property at the zero partial pressure limit, representing a standardised output of the model which is used for performance testing. 

.. note::
   Unlike with other models in ``auxi-mpp``, here the composition fractions does **not** need to add up to unity.
   For radiation properties, only the composition fractions of the radiating components are needed.
   Fractions of components regarded as transparent, like H\ :sub:`2`\, N\ :sub:`2`\, and O\ :sub:`2`\, can therefore be omitted.

Example; calculating the zero partial pressure limit of water vapour at 1500 K, 100000 Pa and with a partial pressure path length of 1000 Pa.m:

.. code-block::

   result = ExampleModel.calculate(T=1500, p=100000, x={"H2O": 0.0}, pL=1000)

For ease of use,
``ExampleModel(T=temperature, p=pressure, x=composition, pL=PARTIAL pressure path length)`` can also be used.
