from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Any


@dataclass()
class StructureData:
	structure_name: str
	class_value: object


class StructureTypeData(Enum):
	wall: str = "Стена"
	door: str = "Дверь"
	window: str = "Окно"
	skylight: str = "Зенитный фонарь"# -Зенитных фонарей
	floor: str = "Перекрытие"# Покрытий и перекрытий над проездами
	roof: str = "Кровля"# Перекрытий чердачных, над неотапливаемыми подпольями и подвалами

	@classmethod
	def choices(cls) -> List[Tuple[str, Any]]:
		return [(item.name, item.value) for item in cls]
