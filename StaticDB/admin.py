from django.contrib import admin
from AdminUtils import get_standard_display_list, duplicate_event
from StaticDB.models.BuildingType import BuildingType, BuildingProperty
from StaticDB.models.ClimateData import ClimateData
from StaticDB.models.SpaceCategory import SpaceCategory
from StaticDB.models.SunRadiationData import SunRadiationData


@admin.register(ClimateData)
class ClimateDataAdmin(admin.ModelAdmin):
	list_display = get_standard_display_list(ClimateData)
	list_display_links = ('id', 'name')
	ordering = ['name']
	list_per_page = 10
	actions = [duplicate_event]


@admin.register(SunRadiationData)
class SunRadiationDataAdmin(admin.ModelAdmin):
	list_display = get_standard_display_list(SunRadiationData)
	list_display_links = ['name']
	list_per_page = 10
	actions = [duplicate_event]


@admin.register(SpaceCategory)
class SpaceCategoryAdmin(admin.ModelAdmin):
	list_display = get_standard_display_list(SpaceCategory)
	list_display_links = ['name']
	list_per_page = 10
	actions = [duplicate_event]

	@admin.register(BuildingType)
	class StructureTypeAdmin(admin.ModelAdmin):
		list_display = get_standard_display_list(BuildingType)
		list_per_page = 10
		actions = [duplicate_event]


@admin.register(BuildingProperty)
class BuildingPropertyAdmin(admin.ModelAdmin):
	list_display = get_standard_display_list(BuildingProperty)
	list_per_page = 10
	actions = [duplicate_event]
