from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from .._gas_property_model import GasPropertyModel


class Model[
    T: floatPositiveOrZero,
    p: floatPositiveOrZero,
    x: dict[str, floatFraction],
](GasPropertyModel[T, p, x]):
    """
    Base class for all gas heat capacity models.

    In all cases, heat capacity is calculated in units of [J/(mol.K)].
    """

    property: strNotEmpty = "Constant Pressure Heat Capacity"
    symbol: strNotEmpty = "Cp"
    display_symbol: strNotEmpty = "C_p"
    units: strNotEmpty = "\\joule\\per\\mole\\per\\kelvin"
