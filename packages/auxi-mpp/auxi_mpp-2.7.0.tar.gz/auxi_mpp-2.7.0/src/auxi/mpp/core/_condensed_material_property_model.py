from abc import abstractmethod
from typing import Any

from auxi.core.validation import floatFraction, floatPositiveOrZero

from ._material_property_model import MaterialPropertyModel


class CondensedMaterialPropertyModel[
    T: floatPositiveOrZero,
    p: floatPositiveOrZero,
    x: dict[str, floatFraction],
    a: dict[str, dict[str, floatFraction]],
](MaterialPropertyModel[T, p, x]):
    """
    Base class of models that describe the variation of a specific condensed material physical property.
    """

    def model_post_init(self, __context: Any) -> None:
        return super().model_post_init(__context)

    def __call__(self, T: T = 298.15, p: p = 101325, x: x = {}, a: a = {}):
        """
        For details about this method, please refer to the calculate method.
        """
        return self.calculate(T, p, x, a)

    @abstractmethod
    def calculate(self, T: T, p: p, x: x, a: a) -> float:
        """
        Calculate the property.

        Args:
        ----
            T: System temperature.
            p: System pressure.
            x: Chemical composition dictionary.
            a: Phase constituents activity dictionary.

        Returns:
        -------
            Material property value.
        """
        ...
