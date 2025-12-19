.. _gas:

Gas
===

Physical Property Models
------------------------

The physical properties covered and the model classes available to model the properties are listed below.

#. **Molar Volume** Models

    To import gas molar volume model classes:

    .. code-block:: 

        from auxi.mpp.gas.Vm import (
            ClapeyronUnary,
            ClapeyronBinary,
            ClapeyronMulti
        )

#. **Density** Models

    To import gas density model classes:

    .. code-block:: 

        from auxi.mpp.gas.ρ import (
            ClapeyronDensityUnary,
            ClapeyronDensityBinary,
            ClapeyronDensityMulti
            )

#. **Viscosity** Models

    To import gas viscosity model classes:

    .. code-block:: 

        from auxi.mpp.gas.μ import (
            LemmonHellmannLaeseckeMuznyUnary,
            WilkeBinary
            )

#. **Thermal Conductivity** Models

    To import gas thermal conductivity model classes:

    .. code-block:: 

        from auxi.mpp.gas.κ import (
            ChungLemmonHuberAssaelUnary,
            MasonSaxenaBinary,
            MasonSaxenaMulti
            )

#. **Diffusivity** Models

    To import gas diffusivity model classes:

    .. code-block:: 

        from auxi.mpp.gas.D import (
            BurgessUnary,
            HellmannBinary
            )

#. **Total Emissivity** Models

    To import gas total emissivity model classes:

    .. code-block:: 

        from auxi.mpp.gas.ɛ import (
            EdwardsLecknerUnary,
            EdwardsLecknerBinary,
            EdwardsLecknerMulti
            )

#. **Constant Pressure Heat Capacity** Model

    To import the gas constant pressure heat capacity model class:

    .. code-block:: 

        from auxi.mpp.gas.Cp import AlyUnary


Using the Models
----------------

Calculating a physical property is as simple as creating an instance of a physical property model and calling the ``calculate()`` method on it, through which the conditions can be specified.
All models are subdivided into unary, binary and multi-component models, from which model instances can be created.

Radiative gas properties, like the total emissivity, function slightly different as a pressure path length input also needs to be provided, for example.
These where therefore given their own class type and how they work is explained below.

.. toctree::
   :maxdepth: 1

   using-the-models/unary-binary-multi-class
   using-the-models/radiation-unary-class
   using-the-models/radiation-binary-multi-classes
