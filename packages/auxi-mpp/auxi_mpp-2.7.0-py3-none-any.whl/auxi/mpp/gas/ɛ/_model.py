from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from .._gas_radiation_property_model import GasRadiationPropertyModel


class Model[
    T: floatPositiveOrZero,
    p: floatPositiveOrZero,
    x: dict[str, floatFraction],
    pL: floatPositiveOrZero,
](GasRadiationPropertyModel[T, p, x, pL]):
    """
    Base class for all gas emissivity models.

    In all cases, total emissivity is calculated in units of [-].
    """

    property: strNotEmpty = "Total Emissivity"
    symbol: strNotEmpty = "ɛ"
    display_symbol: strNotEmpty = ""
    units: strNotEmpty = ""
