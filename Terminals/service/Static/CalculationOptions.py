import enum


class CalculationOptions(enum.Enum):
	directive_terminals: str = 'directive_terminals'
	device_area: str = 'device_area'
	minimum_terminals: str = 'minimum_terminals'
	directive_length: str = 'directive_length'

	@classmethod
	def get_list_of_enum_values(cls):
		return list(map(lambda c: c.value, cls))
