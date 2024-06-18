from django.contrib import admin

# Register your models here.
from AdminUtils import get_standard_display_list
from HeatBalance.Models.AirBalance.AirBalanceModel import AirBalance
from HeatBalance.Models.HeatLoadData.HeatLoad import HeatEquipment, HeatLoadEquipment, HeatAdditionalLoad, TotalHeat
from Spaces.admin import StructureInline, SupplySystemInline, FancoilSystemInline, HeatSystemInline, ExhaustSystemInline
from Spaces.models import SpaceData


@admin.register(AirBalance)
class SpaceHeatAdmin(admin.ModelAdmin):
    additional_list = ['supply_air_mult','exhaust_air_mult']
    list_display = SpaceData.short_names + additional_list
    inlines = [StructureInline, SupplySystemInline, ExhaustSystemInline, FancoilSystemInline,
               HeatSystemInline]
    list_filter = get_standard_display_list(AirBalance)
    list_per_page = 20


@admin.register(TotalHeat)
class SpaceHeatAdmin(admin.ModelAdmin):
    additional_list = ['total_equipment_load', 'total_lighting_load',
                       'total_human_load', 'total_radiation_load', 'additional_load', 'total_heat_load']
    list_display = SpaceData.short_names + additional_list
    inlines = [StructureInline, SupplySystemInline, ExhaustSystemInline, FancoilSystemInline,
               HeatSystemInline]
    list_filter = get_standard_display_list(TotalHeat)
    list_per_page = 20


@admin.register(HeatAdditionalLoad)
class HeatEquipmentAdmin(admin.ModelAdmin):
    suffix_list = HeatAdditionalLoad.short_names
    list_filter = get_standard_display_list(HeatAdditionalLoad)

    list_display = suffix_list+get_standard_display_list(HeatAdditionalLoad, excluding_list=['space','id'])


@admin.register(HeatLoadEquipment)
class HeatEquipmentAdmin(admin.ModelAdmin):
    list_filter = get_standard_display_list(HeatLoadEquipment)
    additional_list = ['equipment_load_local', 'summary_equipment_load']
    suffix_list = HeatLoadEquipment.short_names
    list_display = suffix_list + get_standard_display_list(HeatLoadEquipment, excluding_list=['space','id'])


@admin.register(HeatEquipment)
class HeatEquipmentAdmin(admin.ModelAdmin):
    list_filter = get_standard_display_list(HeatEquipment)
    list_display = get_standard_display_list(HeatEquipment)
