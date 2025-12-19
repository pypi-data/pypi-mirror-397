import inspect
from abc import abstractmethod
from pathlib import Path
from typing import Any

from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ..core import MaterialPropertyModel
from ..core._material_type import MaterialType


class GasPropertyModel[
    T: floatPositiveOrZero,
    p: floatPositiveOrZero,
    x: dict[str, floatFraction],
](MaterialPropertyModel[T, p, x]):
    material_type: MaterialType = MaterialType.GAS
    material: strNotEmpty = "Gas"

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        if len(GasPropertyModel.data) == 0:
            GasPropertyModel.load_data(path=Path(inspect.getfile(type(self))))

    def __call__(self, T: T = 298.15, p: p = 101325, x: x = {}):
        """
        For details about this method, please refer to the calculate method.
        """
        return self.calculate(T, p, x)

    @abstractmethod
    def calculate(self, T: T, p: p, x: x) -> float:
        """
        Calculate the property.

        Args:
        ----
            T: System temperature.
            p: System pressure.
            x: Chemical composition dictionary.

        Returns:
        -------
            Material property value.
        """
        ...
