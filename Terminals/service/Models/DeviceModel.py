from dataclasses import dataclass, field


@dataclass()
class Device:
	space_id: str = None
	space_flow: float = None
	system_type: str = None
	flow_to_device_calculated: float = None
	k_ef: float = None
	system_name: str = None
	db_system_name: str = None
	ceiling_offset: float = None
	device_area: float = None
	directive_terminals: int = None
	directive_length: float = None
	family_device_name: str = None
	calculation_options: str = None
	family_instance_name: str = None
	max_flow: float = None
	geometry: str = None
	color: str = None
	dimension1: str = None
	minimum_device_number: int = None
	point_z: float = None
	point_x_y_list: tuple[tuple[float]] = None
	device_orientation_option1: str = None
	device_orientation_option2: str = None
	single_device_orientation: str = None
	wall_offset: float = None

	def calculate_device_flow_and_k_ef(self):
		if self.max_flow and self.minimum_device_number and self.space_flow:
			self.flow_to_device_calculated = self.space_flow / self.minimum_device_number
			self.k_ef = self.flow_to_device_calculated / self.max_flow
