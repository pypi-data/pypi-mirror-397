import inspect
from abc import abstractmethod
from pathlib import Path
from typing import Any

from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ..core import MaterialPropertyModel
from ..core._material_type import MaterialType


class GasRadiationPropertyModel[
    T: floatPositiveOrZero,
    p: floatPositiveOrZero,
    x: dict[str, floatFraction],
    pL: floatPositiveOrZero,
](MaterialPropertyModel[T, p, x]):
    material_type: MaterialType = MaterialType.GAS
    material: strNotEmpty = "Gas"

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        if len(GasRadiationPropertyModel.data) == 0:
            GasRadiationPropertyModel.load_data(path=Path(inspect.getfile(type(self))))

    def __call__(self, T: T = 298.15, p: p = 101325, x: x = {}, pL: pL = 101325):
        """
        For details about this method, please refer to the calculate method.
        """
        return self.calculate(T, p, x, pL)

    @abstractmethod
    def calculate(self, T: T, p: p, x: x, pL: pL) -> float:
        """
        Calculate the radiative property.

        Args:
        ----
            T: System temperature.
            p: System pressure.
            x: Chemical composition dictionary.
            pL: Pressure path length.

        Returns:
        -------
            Material property value.
        """
        ...
