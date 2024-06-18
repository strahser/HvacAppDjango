from Terminals.service.Static.CalculationOptions import CalculationOptions


class DevicePropertiesName:
	# from device model fields
	selected_df_columns_name = [
		"space_id", "family_instance_name", "flow_to_device_calculated", "system_name",
		"minimum_device_number", "calculation_options", "k_ef"
	]
	df_device_result_columns = [
		'S_ID',
		'S_Number',
		'S_Name',
		'S_level',
		'family_device_name',
		'family_instance_name',
		'minimum_device_number',
		'flow_to_device_calculated',
		'k_ef',
		'calculation_option',
	]
	json_df_columns = [
		'S_ID',
		'family_device_name',
		'family_instance_name',
		'minimum_device_number',
		'flow_to_device_calculated',
		'system_name',
		'instance_points',
	]
	calculation_options = CalculationOptions.get_list_of_enum_values()
	device_property_columns_names: list[str] = [
		"type_index",
		'device_orientation_option1',
		'device_orientation_option2',
		'single_device_orientation',
		'wall_offset',
		'ceiling_offset',
		'family_device_name',
		'calculation_options',
		"device_area",
		"directive_terminals",
		"directive_length"
	]
	additional_columns = [
		'family_instance_name', 'calculated_device_number',
		'k_ef', 'flow_to_device_calculated',
		'space_param_name'
	]
