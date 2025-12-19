from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from .._gas_property_model import GasPropertyModel


class Model[
    T: floatPositiveOrZero,
    p: floatPositiveOrZero,
    x: dict[str, floatFraction],
](GasPropertyModel[T, p, x]):
    """
    Base class for all gas molar volume models.

    In all cases, molar volume is calculated in units of [m³/mol].
    """

    property: strNotEmpty = "Molar Volume"
    symbol: strNotEmpty = "Vm"
    display_symbol: strNotEmpty = "\\bar{V}"
    units: strNotEmpty = "\\cubic\\meter\\per\\mol"
