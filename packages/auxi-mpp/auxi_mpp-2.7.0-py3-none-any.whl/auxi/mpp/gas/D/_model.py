from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from .._gas_property_model import GasPropertyModel


class Model[
    T: floatPositiveOrZero,
    p: floatPositiveOrZero,
    x: dict[str, floatFraction],
](GasPropertyModel[T, p, x]):
    """
    Base class for all gas diffusivity models.

    In all cases, diffusivity is calculated in units of [m²/s].
    """

    property: strNotEmpty = "Diffusivity"
    symbol: strNotEmpty = "D"
    display_symbol: strNotEmpty = "D"
    units: strNotEmpty = "\\meter\\squared\\per\\second"
