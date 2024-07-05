from django.contrib import admin
from django.utils.safestring import mark_safe
from Structures.Utils.AdminUtils import get_standard_display_list
from Structures.forms import StructureForm
from Structures.models.BaseStructure import BaseStructure
from Structures.models.Structure import Structure, StructureRadiation

admin.site.site_header = "Панель администрирования"
admin.site.index_title = "Kласс энергоэффективности"


@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
	additional_list = ['standard_structure_type', 'K_real', 't_in', "t_out", "k_orient",
	                   'corner_space_coefficient', 'calculate_heat_loss']
	excluding_list = ['name', 'space', 'base_structures', 'id']
	list_display = Structure.short_names + get_standard_display_list(Structure, additional_list=additional_list,
	                                                                 excluding_list=excluding_list)
	list_editable = get_standard_display_list(Structure, excluding_list=['id', 'space'] + excluding_list)
	form = StructureForm
	list_filter = ['space', 'name', 'base_structures', 'orientation', ]


@admin.register(StructureRadiation)
class StructureRadiationAdmin(admin.ModelAdmin):
	additional_list = ['standard_structure_type','name','orientation','area','radiation_data','calculate_radiation']
	list_display = Structure.short_names + additional_list


@admin.register(BaseStructure)
class BaseStructureAdmin(admin.ModelAdmin):
	list_display = get_standard_display_list(BaseStructure,
	                                         excluding_list=['structure_picture'],
	                                         additional_list=['post_photo',
	                                                          'calculate_heat_resistance_normative']
	                                         )
	list_display_links = ('id', 'name')
	list_filter = ['standard_structure_type']
	readonly_fields = ['post_photo']

	@admin.display(description="Фотография")
	def post_photo(self, structure_type: BaseStructure):
		if structure_type.structure_picture:
			return mark_safe(f"<img src='{structure_type.structure_picture.url}' width=100>")
		else:
			return "Без изображения"
