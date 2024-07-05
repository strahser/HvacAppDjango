from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Any


@dataclass()
class StructureData:
	structure_name: str
	class_value: object


class StructureTypeData(Enum):
	Wall: str = "Стена"
	Door: str = "Дверь"
	Window: str = "Окно"
	Skylight: str = "Зенитный фонарь"# -Зенитных фонарей
	Floor: str = "Перекрытие"# Покрытий и перекрытий над проездами
	Roof: str = "Кровля"# Перекрытий чердачных, над неотапливаемыми подпольями и подвалами

	@classmethod
	def choices(cls) -> List[Tuple[str, Any]]:
		return [(item.name, item.value) for item in cls]
