from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from .._gas_property_model import GasPropertyModel


class Model[
    T: floatPositiveOrZero,
    p: floatPositiveOrZero,
    x: dict[str, floatFraction],
](GasPropertyModel[T, p, x]):
    """
    Base class for all gas viscosity models.

    In all cases, viscosity is calculated in units of [Pa.s].
    """

    property: strNotEmpty = "Dynamic Viscosity"
    symbol: strNotEmpty = "μ"
    display_symbol: strNotEmpty = "\\mu"
    units: strNotEmpty = "\\pascal\\second"
