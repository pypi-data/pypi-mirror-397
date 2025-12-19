from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from .._gas_property_model import GasPropertyModel


class Model[
    T: floatPositiveOrZero,
    p: floatPositiveOrZero,
    x: dict[str, floatFraction],
](GasPropertyModel[T, p, x]):
    """
    Base class for all gas density models.

    In all cases, density is calculated in units of [kg/m³].
    """

    property: strNotEmpty = "Density"
    symbol: strNotEmpty = "ρ"
    display_symbol: strNotEmpty = "\\rho"
    units: strNotEmpty = "\\kilo\\gram\\per\\cubic\\meter"
