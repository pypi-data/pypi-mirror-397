from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from .._gas_property_model import GasPropertyModel


class Model[
    T: floatPositiveOrZero,
    p: floatPositiveOrZero,
    x: dict[str, floatFraction],
](GasPropertyModel[T, p, x]):
    """
    Base class for all gas thermal conductivity models.

    In all cases, thermal conductivity is calculated in units of [W/(m.K)].
    """

    property: strNotEmpty = "Thermal Conductivity"
    symbol: strNotEmpty = "κ"
    display_symbol: strNotEmpty = "\\kappa"
    units: strNotEmpty = "\\watt\\per\\meter\\per\\kelvin"
