.. _essentials:

Essentials
==========

The material physical property models in ``auxi-mpp`` are more than just a mathematical function that takes in material conditions and outputs a property.
Together with the model itself, additional information describing the model and the property it is modelling is packaged with it.
This allows users to not only estimate physical properties, but also access the references from which the model was taken, the parameters used in the model, the units in which the model outputs the property, etc.

To achieve this, the models were packaged into Python classes.
A Python class can contain the model logic itself, as well as the additional information that puts the model in context, so the user knows what is dealt with.
The model logic is accessed through class methods and the additional information through class attributes.

Class Methods
-------------

All material property models have a ``calculate()`` method.
This is the most important method as it is used to estimate the material physical property.

For example, if ``ExampleModel`` is the class name of an electrical conductivity model, the electrical conductivity can be estimated as such;

.. code-block::

   ec_model = ExampleModel()
   result = ec_model.calculate(T=1500, x={"SiO2": 0.7, "MgO": 0.3})
   print(result)

This will print out the estimated electrical conductivity of a 70 % SiO₂ 30% MgO slag at 1500 K and atmospheric pressure.

Alternatively, a more compact line can be used;

.. code-block::

   print(ExampleModel().calculate(T=1500, x={"SiO2": 0.7, "MgO": 0.3}))

It should be noted that for most slag models, a user-defined function will have to be provided when calling the model's class.
See :ref:`binary-class-slag`.
Calling the class name is generally referred to as creating an instance of the class.

Class Attributes
----------------

The class attributes that can be accessed varies between the models; however, the core attributes accessible in all models are the following.

#. **property**

#. **symbol**

#. **display_symbol** - for use in :math:`\LaTeX`

#. **units** - for use in :math:`\LaTeX` (all model outputs are in SI units)

#. **references** - gives the source from which the model was taken

#. **compound_scope/component_scope/system_scope** - gives the scope of materials for which the model can be used

The compound/component/system scope is specific to the class in question.
Most models have either a compound scope (i.e. slag models) or a component scope (i.e. liquid alloy models).

These attributes are callable.
For example, if ``ExampleModel()`` is an instance of a molar volume model;

.. code-block::

   print(ExampleModel().property)

**Output**

.. code-block::

   Molar Volume