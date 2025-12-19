.. _esf-example:

Equilibrium Slag Function
======================

The Equilibrium Slag Function (:term:`ESF`) is a user-defined function which should take in temperature, pressure, composition and oxidation conditions, and return equilibrium slag composition and bond fractions.
This function is type sensitive, meaning the inputs and outputs of it should follow a specific type and order -- see :ref:`building-the-function`.

In the context of the slag physical property models in ``auxi-mpp``, bond fractions refer to the abundance of the different cation-oxygen-cation (M-O-M) units.
These bond fractions are essential to describe the short- to medium-range structure in slag, which is an important phenomenon that dictates its physical properties.

However, the precise bond fractions of the various cation combinations do not scale linearly with slag constituent fractions and are therefore not as straightforward to obtain.
`ChemApp for Python <https://python.gtt-technologies.de/doc/chemapp/main.html#>`_ implements the Modified Quasichemical Model (:term:`MQM`) to determine these bond fractions, which is why the :term:`ESF` require it.

Most binary and multi-component slag models require the user to provide an :term:`ESF`.
Here, we provide a condensed guide on how to set up an :term:`ESF` that implements `ChemApp for Python <https://python.gtt-technologies.de/doc/chemapp/main.html#>`_.
We will show how to do an equilibrium calculation, extract the bond fractions from the equilibrated slag, and finally, how to build the complete :term:`ESF`.

.. toctree::
   :maxdepth: 1

   equilibrium-calculation
   extracting-bond-fractions
   building-the-function
