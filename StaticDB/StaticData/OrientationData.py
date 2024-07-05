from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Any


@dataclass
class OrientationDataOptions:
    verbose_name: str
    k_heat: float


class OrientationData(Enum):
    ND: str = OrientationDataOptions("Нет данных", 1)
    N: str = OrientationDataOptions("С", 1.1)
    NE: str = OrientationDataOptions("СВ", 1.05)
    E: str = OrientationDataOptions("В", 1.05)
    SE: str = OrientationDataOptions("ЮВ", 1)
    S: str = OrientationDataOptions("Ю", 1)
    SW: str = OrientationDataOptions("ЮЗ", 1)
    W: str = OrientationDataOptions("З", 1.1)
    NW: str = OrientationDataOptions("СЗ", 1.1)
    horizontal: str = OrientationDataOptions("Горизонтальная", 1)

    @classmethod
    def choices(cls) -> List[Tuple[str, Any]]:
        return [(item.name, item.value.verbose_name) for item in cls]
