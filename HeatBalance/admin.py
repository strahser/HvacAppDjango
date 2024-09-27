from django.contrib import admin

# Register your models here.
from django.db.models import F

from AdminUtils import get_standard_display_list
from HeatBalance.Models.AirBalance.AirBalanceModel import AirBalance
from HeatBalance.Models.HeatLoadData.HeatLoad import HeatEquipment, HeatLoadEquipment, HeatAdditionalLoad, HeatBalance
from Spaces.admin import StructureInline, SupplySystemInline, FancoilSystemInline, HeatSystemInline, ExhaustSystemInline
from Spaces.models import SpaceData

INLINES = [StructureInline, SupplySystemInline, ExhaustSystemInline, FancoilSystemInline,
           HeatSystemInline]

class HeatSystemInline(admin.TabularInline):
	model = HeatLoadEquipment
	extra = 0

class AdditionalHeatSystemInline(admin.TabularInline):
	model = HeatAdditionalLoad
	extra = 0

@admin.register(AirBalance)
class SpaceHeatAdmin(admin.ModelAdmin):
	additional_list = ['supply_air_mult', 'exhaust_air_mult', 'total_supply_air_balance', 'total_exhaust_air_balance']
	list_display = SpaceData.report_display_names + additional_list
	list_filter = get_standard_display_list(AirBalance)
	list_per_page = 20

	def get_queryset(self, request):
		queryset = super().get_queryset(request)
		queryset = queryset.annotate(
			_supply_air_mult=F("space_category__Sup_air_mult") * F("S_Volume"),
			_exhaust_air_mult=F("space_category__Ex_air_mult") * F("S_Volume"),
			_total_supply_air_balance=F('_supply_air_mult'),
			_total_exhaust_air_balance=F('_exhaust_air_mult')
		)
		return queryset


@admin.register(HeatBalance)
class HeatBalance(admin.ModelAdmin):
	additional_list = ['total_equipment_load', 'total_lighting_load',
	                   'total_human_load', 'total_radiation_load', 'additional_load', 'total_heat_load']
	inlines = [HeatSystemInline,AdditionalHeatSystemInline]
	list_display = SpaceData.report_display_names + additional_list
	list_filter = get_standard_display_list(HeatBalance)
	list_per_page = 20


@admin.register(HeatAdditionalLoad)
class HeatEquipmentAdmin(admin.ModelAdmin):
	suffix_list = HeatAdditionalLoad.short_names
	list_filter = get_standard_display_list(HeatAdditionalLoad)

	list_display = suffix_list + get_standard_display_list(HeatAdditionalLoad, excluding_list=['space', 'id'])


@admin.register(HeatLoadEquipment)
class HeatEquipmentAdmin(admin.ModelAdmin):
	list_filter = get_standard_display_list(HeatLoadEquipment)
	additional_list = ['equipment_load_local', 'summary_equipment_load']
	suffix_list = HeatLoadEquipment.short_names
	list_display = suffix_list + get_standard_display_list(HeatLoadEquipment, excluding_list=['space', 'id'])


@admin.register(HeatEquipment)
class HeatEquipmentAdmin(admin.ModelAdmin):
	list_filter = get_standard_display_list(HeatEquipment)
	list_display = get_standard_display_list(HeatEquipment)
