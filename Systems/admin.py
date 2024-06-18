from django.contrib import admin

from AdminUtils import get_standard_display_list
from Systems.Forms import DeviceGeometryForm
from Systems.models import SystemName, FancoilSystem, SupplySystem, ExhaustSystem, HeatSystem

admin.site.index_title = "Системы"


@admin.register(SystemName)
class DeviceTypeAdmin(admin.ModelAdmin):
	list_display = get_standard_display_list(SystemName)
	list_filter = get_standard_display_list(SystemName)


@admin.register(HeatSystem)
@admin.register(FancoilSystem)
@admin.register(ExhaustSystem)
@admin.register(SupplySystem)
class DeviceTypeAdmin(admin.ModelAdmin):
	suffix_list = ['Space_ID','Space_name','Space_number']
	list_display = suffix_list+ get_standard_display_list(SupplySystem, excluding_list=['space'])
	form = DeviceGeometryForm
	list_filter = get_standard_display_list(SupplySystem, excluding_list=['space'])
	fieldsets = (
		('Общая информация', {
			'fields': ('space', 'system_type', 'system_name')

		}),

		('Категория', {

			'fields': ('family_device_name', 'calculation_options', 'geometry_options_model',)

		}),
		('Параметры', {
			'fields': ('system_flow', 'device_area', 'directive_terminals', 'directive_length')
		}),

	)

