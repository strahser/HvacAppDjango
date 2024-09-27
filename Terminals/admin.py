from django.contrib import admin
from AdminUtils import get_standard_display_list
from Terminals.models import DeviceGeometry, EquipmentBase


@admin.register(DeviceGeometry)
class DeviceTypeAdmin(admin.ModelAdmin):
	list_display = get_standard_display_list(DeviceGeometry)


@admin.register(EquipmentBase)
class EquipmentBaseAdmin(admin.ModelAdmin):
	list_display = get_standard_display_list(EquipmentBase)
	list_display_links = ('family_device_name',)
	list_filter = ["system_equipment_type","family_device_name","system_flow_parameter_name",]
