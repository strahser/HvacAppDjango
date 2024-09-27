import enum
from typing import Any, List, Tuple
from django.db import connection
from dataclasses import dataclass, field

COLOR_CHOICES = [
    ('b', 'синий'),
    ('g', 'зеленый'),
    ('r', 'красный'),
    ('c', 'голубой'),
    ('m', 'пурпурный'),
    ('y', 'желтый'),
    ('k', 'черный'),
    ('w', 'белый'),
    # Добавленные цвета из matplotlib
    ('tab:blue', 'темно-синий'),
    ('tab:orange', 'оранжевый'),
    ('tab:green', 'темно-зеленый'),
    ('tab:red', 'темно-красный'),
    ('tab:purple', 'темно-фиолетовый'),
    ('tab:brown', 'коричневый'),
    ('tab:pink', 'розовый'),
    ('tab:gray', 'серый'),
    ('tab:olive', 'оливковый'),
    ('tab:cyan', 'голубовато-зеленый'),
    ('lime', 'зеленый лайм'),
    ('teal', 'сине-зеленый'),
    ('navy', 'темно-синий'),
    ('magenta', 'пурпурный'),
    ('gold', 'золотой'),
    ('silver', 'серебристый'),
]


class ChoicesBase(enum.Enum):
    @classmethod
    def choices(cls) -> List[Tuple[str, Any]]:
        return [(item.name, item.value) for item in cls]


class CenterOrientation(ChoicesBase):
    corner = 'Угол'
    center = 'Центр'


class Orientation(ChoicesBase):
    up = "верх"
    down = "вниз"
    left = "лево"
    right = "вправо"
    center_horizontal = "центр горизонт."
    center_vertical = "центр вертикал."
    center = 'центр'
    corner = 'угол'


class CalculationOptions(ChoicesBase):
    minimum_terminals = "расчетный минимум"
    directive_terminals_number = "заданное колличество"
    directive_length = "заданная длина"
    device_area = "заданная площадь"


class SystemType(ChoicesBase):
    Supply_system = "Приточная"
    Exhaust_system = "Вытяжная"
    Fan_coil_system = "Кондиционирование"
    Heat_system = "Отопление"


def equipment_choices() -> List[Tuple[str, str]]:
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT family_device_name  from Terminals_equipmentbase ")
    queryset = cursor.fetchall()
    choices = [(val[0], val[0]) for val in queryset]
    return choices


@dataclass
class SystemProperty:
    system_type: str
    system_name_column: str
    system_flow_column: str
    equipment_id_column: str


SYSTEM_DICTIONARY: dict[str, SystemProperty] = {
    SystemType.Supply_system.name: SystemProperty("Supply_system", "S_supply_name", "S_SA_max", "supply_equipment_id"),
    SystemType.Exhaust_system.name: SystemProperty("Exhaust_system", "S_exhaust_name", "S_EA_max",
                                                   "exhaust_equipment_id"),
    SystemType.Fan_coil_system.name: SystemProperty("Fan_coil_system", "S_cold_name", "S_Cold_Load",
                                                    "fancoil_equipment_id"),
}
