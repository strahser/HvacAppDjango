from dataclasses import dataclass


@dataclass
class DeviceModelExport:
    S_ID: str = None
    family_device_name: str = None
    family_instance_name: str = None
    minimum_device_number: float = None
    flow_to_device_calculated: float = None
    system_name: str = None
    instance_points: list[float] = None

    def __init__(self, json_data: dict, points):
        self.S_ID = json_data["S_ID"]
        self.family_device_name: str = json_data["family_device_name"]
        self.family_instance_name: str = json_data["family_instance_name"]
        self.minimum_device_number: float = json_data["minimum_device_number"]
        self.flow_to_device_calculated: float = json_data["flow_to_device_calculated"]
        self.system_name: str = json_data["system_name"]
        self.instance_points: list[float] = points
