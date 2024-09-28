from dataclasses import dataclass, field

DATA_LIST = ['minimum_device_number',
             'family_device_name',
             'family_instance_name',
             'max_flow', 'geometry',
             'minimum_device_number',
             'dimension1'
             ]

REPORT_LIST = {'family_device_name': 'Семейство',
               'family_instance_name': 'Экземляр',
               'minimum_device_number': 'Кол-во',
               'max_flow': 'Макс. Расход',
               'local_flow': 'Факт. Расход',
               'k_ef': 'Кэф'
               }


@dataclass
class TerminalData:
    family_device_name: str = None
    family_instance_name: str = None
    max_flow: float = None
    geometry: str = None
    minimum_device_number: int = None
    dimension1: float = None
    points_2d_plot: list[float] = None
    system_name: str = None
    system_flow: float = None
    local_flow: float = field(init=False)
    k_ef: float = field(init=False)

    def __post_init__(self):
        if self.system_flow and self.max_flow and self.minimum_device_number:
            self.local_flow = self.system_flow / self.minimum_device_number
            self.k_ef = self.local_flow / self.max_flow
        else:
            self.k_ef = 0
            self.local_flow = 0
