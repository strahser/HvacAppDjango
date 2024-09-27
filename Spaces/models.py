from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.safestring import mark_safe
from matplotlib import pyplot as plt

from Config.models import Building
from django.contrib import admin

from HvacAppDjango.models.BaseModel import BaseModel
from Systems.models import ExhaustSystem, SupplySystem, FancoilSystem
from shapely import Polygon

from Terminals.service.PlotePolygons.PlotTerminals import StaticPlots
from Terminals.service.PlotePolygons.plote_settings import text_style, box_2


class SpaceData(BaseModel):
	report_display_names = ['S_ID', 'S_Number', 'S_Name']  # for reports
	S_ID = models.CharField(primary_key=True, max_length=200)
	building = models.ForeignKey(Building, null=True, blank=True, on_delete=models.SET_NULL,verbose_name="Здание")
	space_category = models.ForeignKey("StaticDB.SpaceCategory", null=True, blank=True,
	                                   on_delete=models.SET_NULL, verbose_name="Категория пространства")
	S_Number = models.CharField(max_length=200,null=True, blank=True, verbose_name="Ном.пом.")
	S_Name = models.CharField(max_length=200, null=True, blank=True, verbose_name="Наим.Пом.")
	S_height = models.FloatField(null=True, blank=True, verbose_name="Высота Пом.")
	S_area = models.FloatField(null=True, blank=True, verbose_name="Площ.Пом.")
	S_Volume = models.FloatField(null=True, blank=True, verbose_name="Объем Пом.")
	S_level = models.CharField(max_length=200, null=True, blank=True, verbose_name="Уровень")
	human_number = models.FloatField(null=True, blank=True, default=1, verbose_name="Кол-во людей")
	geometry_data = models.JSONField(null=True, blank=True, verbose_name='Геометрия')

	def _update_system(self, system_type, _total_heat_load: float) -> None:
		"""обновляет system_flow=_total_heat_load"""
		try:
			system = system_type.objects \
				.filter(space__S_ID=self.S_ID) \
				.filter(auto_calculate_flow=True)
			system.update(system_flow=_total_heat_load)
		except Exception as e:
			print(e)

	@property
	def system_list(self):
		return self.SupplySystemDisplay(), self.ExhaustSystemDisplay(), self.FancoilSystemDisplay()

	def button_link(url: str, name: str = "изменить", cls='info'):
		return f'<a href="{url}"class="btn btn-{cls} mr-5"   role="button">{name}</a>'

	def get_space_text(self, ax):
		url_reverse = reverse('admin:Spaces_spacedata_change', args=(self.S_ID,))
		ax.annotate(f'{self.S_ID}',
		            xy=(self._pcx, self._pcy),
		            xytext=(self._pcx, self._pcy),
		            url=url_reverse,
		            bbox=box_2,
		            **text_style,
		            )

	@property
	def _px(self):
		if isinstance(self.geometry_data, dict):
			return self.geometry_data.get('px')

	@property
	def _py(self):
		if isinstance(self.geometry_data, dict):
			return self.geometry_data.get('py')

	@property
	def _pcx(self):
		if isinstance(self.geometry_data, dict):
			return self.geometry_data.get('pcx')

	@property
	def _pcy(self):
		if isinstance(self.geometry_data, dict):
			return self.geometry_data.get('pcy')

	def create_polygon(self) -> Polygon:
		return Polygon([(x, y) for x, y in zip(self._px, self._py)])

	@staticmethod
	def render_modal_window(pk: int, title: str, modal_body: str, button_name='Детали'):
		"""созадаем модльное окно которое можем вызывать из таблицы"""
		context = dict(pk=pk, title=title, modal_body=modal_body, button_name=button_name)
		return render_to_string(template_name='modal.html', context=context)

	@admin.display(description='Схема', ordering="supplysystem__system_name")
	def draw_space_polygons(self, fig=None, ax=None):
		if not fig and not ax:
			fig, ax = plt.subplots()
		try:
			x, y = self.create_polygon().exterior.xy
			ax.plot(x, y, color="grey")
			for system in self.system_list:
				if system:
					system._draw_terminals(fig, ax)
			plt.axis('off')
			saving_fig = StaticPlots.save_plot(fig)
			# plt.clf()
			return mark_safe(saving_fig)
		except Exception as e:
			print(e)

	@admin.display(description='Вытяжная', ordering="exhaustsystem__system_name")
	def ExhaustSystemDisplay(self):
		return ExhaustSystem.objects.filter(space=self.pk).first()

	@admin.display(description='Приточная', ordering="supplysystem__system_name")
	def SupplySystemDisplay(self) -> SupplySystem:
		return SupplySystem.objects.filter(space=self.pk).first()

	@admin.display(description='Кондиционирование', ordering="fancoilsystem__system_name")
	def FancoilSystemDisplay(self):
		return FancoilSystem.objects.filter(space=self.pk).first()

	@property
	def t_min(self):
		if self.space_category.min_temp:
			return self.space_category.min_temp

	@property
	def t_out_max(self):
		if self.building and self.building.climate_data.t_out_max:
			return self.building.climate_data.t_out_max

	def __str__(self):
		return f"id:{self.S_ID},пом.:{self.S_Name},№пом.:{self.S_Number}"

	class Meta:
		verbose_name = 'Помещение'
		verbose_name_plural = 'Помещения'
		ordering = ["S_ID"]


class SpaceSystem(SpaceData):
	class Meta:
		proxy = True
		verbose_name = 'Схемы систем'
		verbose_name_plural = 'Схемы систем'
		ordering = ["S_ID"]
