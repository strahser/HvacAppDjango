from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.safestring import mark_safe
from matplotlib import pyplot as plt

from Config.models import Building
from django.contrib import admin

from Systems.models import ExhaustSystem, SupplySystem, FancoilSystem
from shapely import Polygon

from Terminals.service.PlotePolygons.PlotTerminals import StaticPlots
from Terminals.service.PlotePolygons.plote_settings import text_style, box_2


class BaseModel(models.Model):
	creation_stamp = models.DateTimeField(auto_now_add=True, verbose_name="дата создания", null=True)
	update_stamp = models.DateTimeField(auto_now=True, verbose_name="дата изменения", null=True)

	class Meta:
		abstract = True


class SpaceData(BaseModel):
	building = models.ForeignKey(Building, on_delete=models.PROTECT)
	S_ID = models.CharField(primary_key=True, max_length=200)
	S_Number = models.IntegerField(null=True, blank=True)
	S_Name = models.CharField(max_length=200, null=True, blank=True)
	S_height = models.FloatField(null=True, blank=True)
	S_area = models.FloatField(null=True, blank=True)
	S_Volume = models.FloatField(null=True, blank=True)
	S_level = models.CharField(max_length=200, null=True, blank=True)
	human_number = models.FloatField(null=True, blank=True, default=1)
	space_category = models.ForeignKey("StaticDB.SpaceCategory", on_delete=models.PROTECT)
	short_names = ['S_ID', 'S_Number', 'S_Name']
	geometry_data = models.JSONField(null=True, blank=True, verbose_name='Геометрия')

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

	def create_polygon(self):
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
					system.draw_terminals(fig, ax)
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
		return self.space_category.min_temp

	@property
	def t_out_max(self):
		return self.building.climate_data.t_out_max

	def __str__(self):
		return f"id:{self.S_ID},пом.:{self.S_Name},№пом.:{self.S_Number}"

	class Meta:
		verbose_name = 'Помещение'
		verbose_name_plural = 'Помещения'


class SpaceSystem(SpaceData):
	class Meta:
		proxy = True
