from django.contrib import admin

from AdminUtils import get_standard_display_list
from Config.models import Building


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
	list_display = get_standard_display_list(Building) + ['GSOP']
	list_display_links = ('id', 'name')
	list_filter = ['climate_data__name']

