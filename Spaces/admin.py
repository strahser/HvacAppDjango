from django.db.models import Count, Sum
from django.urls import reverse
from django.utils.html import format_html
from Structures.forms import StructureForm
from django.contrib.admin import SimpleListFilter
import os
from django.contrib import admin
from django.utils.safestring import mark_safe
from AdminUtils import get_standard_display_list
from HeatBalance.Models.HeatLoadData.HeatLoad import TotalHeat
from Spaces.models import SpaceData, SpaceSystem
from Structures.models.Structure import Structure
from StaticDB.StaticData.SystemChoices import SystemType
from django.contrib import messages
from typing import List
from admin_form_action import form_action
from Systems.Forms import SystemForm, DeviceGeometryForm
from Systems.models import SupplySystem, ExhaustSystem, FancoilSystem, HeatSystem, SystemData
import adminactions.actions as actions
from django.contrib.admin import site
from matplotlib import pyplot as plt

from Terminals.service.PlotePolygons.PlotTerminals import StaticPlots

actions.add_to_site(site)


class SystemInlineBase(admin.StackedInline):
	form = DeviceGeometryForm
	extra = 0


class SupplySystemInline(SystemInlineBase):
	model = SupplySystem


class ExhaustSystemInline(SystemInlineBase):
	model = ExhaustSystem


class FancoilSystemInline(SystemInlineBase):
	model = FancoilSystem


class HeatSystemInline(SystemInlineBase):
	model = HeatSystem
	extra = 0


class StructureInline(admin.StackedInline):
	model = Structure
	# form = StructureForm
	extra = 0


class HeatLoadInline(admin.StackedInline):
	model = TotalHeat
	# fields = ['total_equipment_load', 'lighting_load', 'total_heat_load']
	extra = 0


class BaseSystemFilter(admin.SimpleListFilter):
	title = None
	parameter_name = None

	def lookups(self, request, model_admin):
		res = [(getattr(i, self.parameter_name)().system_name, getattr(i, self.parameter_name)().system_name)
		       for i in SpaceData.objects.all() if getattr(i, self.parameter_name)()]
		return list(set(res))

	def queryset(self, request, queryset):
		if self.value():
			res = []
			for val in queryset:
				if getattr(val, self.parameter_name)() and str(
						getattr(val, self.parameter_name)().system_name) == self.value():
					res.append(val)
			id_list = [val.pk for val in res]
			qs_filter = queryset.filter(S_ID__in=id_list)
			return qs_filter


class SupplySystemDisplayFilter(BaseSystemFilter):
	title = 'Приточная система'
	parameter_name = 'SupplySystemDisplay'


class ExhaustSystemDisplayFilter(BaseSystemFilter):
	title = 'Вытяжная система'
	parameter_name = 'ExhaustSystemDisplay'


class FancoilDisplayFilter(BaseSystemFilter):
	title = 'Фанкойл система'
	parameter_name = 'FancoilSystemDisplay'


@admin.register(SpaceSystem)
class SpaceDataAdmin(admin.ModelAdmin):
	change_list_template = 'jazzmin/admin/change_list.html'

	def changelist_view(self, request, extra_context=None):
		response = super().changelist_view(
			request,
			extra_context=extra_context,
		)

		try:
			qs = response.context_data['cl'].queryset
		except (AttributeError, KeyError):
			return response
		level_list = qs.values_list("S_level", flat=True).distinct().order_by()
		level_figures = []
		for level in level_list:
			qs_filter = qs.filter(S_level=level)
			fig, ax = plt.subplots()
			fig.set_size_inches(20, 20)
			for space in qs_filter:
				space.draw_space_polygons(fig, ax)
				space.get_space_text(ax)
			level_fig = mark_safe(StaticPlots.save_plot(fig))
			level_figures.append(level_fig)
		response.context_data['filter_data'] = [(_level, _fig) for _level, _fig in zip(level_list, level_figures)]
		return response


@admin.register(SpaceData)
class SpaceDataAdmin(admin.ModelAdmin):
	additional_list = ["SupplySystemDisplay", "ExhaustSystemDisplay", "FancoilSystemDisplay", ]
	excluding_list = ['geometry_data', "building"]
	additional_list_filter = [SupplySystemDisplayFilter, ExhaustSystemDisplayFilter, FancoilDisplayFilter]
	list_display = get_standard_display_list(SpaceData, additional_list=additional_list, excluding_list=excluding_list)
	list_display_links = ('S_ID', 'S_Name')
	list_filter = get_standard_display_list(SpaceData, excluding_list=excluding_list) + additional_list_filter
	inlines = [StructureInline, SupplySystemInline, ExhaustSystemInline, FancoilSystemInline, HeatSystemInline]
	actions = ['add_system']
	change_form_template = 'jazzmin/admin/change_form.html'

	def change_view(self, request, object_id, form_url='', extra_context=None):
		extra_context = extra_context or {}
		_filter = SpaceData.objects.filter(S_ID=object_id).first()
		extra_context['polygons'] = _filter.draw_space_polygons()
		return super().change_view(request, object_id, form_url, extra_context=extra_context)

	@form_action(SystemForm)
	@admin.action(description='Добавить систему')
	def add_system(self, request, queryset: List[SpaceData]):
		def _add_message(space_data: SpaceData, system: SystemData):
			return messages.success(request, f"обновлены следующие помещения {space_data.S_ID} "
			                                 f"добавлена система {system.system_type} имя {system.system_name}")

		def create_abstract_system(system: SystemData,
		                           _space: SpaceData,
		                           _defaults: dict[str, str],
		                           _create_defaults: dict[str, str]):
			system, created = system.objects.update_or_create(space=_space, create_defaults=_create_defaults,
			                                                  defaults=_defaults)
			_add_message(_space, system)

		system_dict = {
			SystemType.Supply_system.name: SupplySystem,
			SystemType.Exhaust_system.name: ExhaustSystem,
			SystemType.Fan_coil_system.name: FancoilSystem,
			SystemType.Heat_system.name: HeatSystem
		}

		form = request.form
		create_defaults = {val: form.cleaned_data[val] for val in
		                   get_standard_display_list(SystemData, excluding_list=['space'])}
		defaults = dict(system_name=form.cleaned_data['system_name'])
		sys_type = form.cleaned_data['system_type']
		for space in queryset:
			create_abstract_system(system_dict.get(sys_type), space, _defaults=defaults,
			                       _create_defaults=create_defaults, )
