import math
import io
from shapely import Polygon
import pandas as pd
from django.db import models
from django.utils.safestring import mark_safe
import Terminals.service.Geometry.GeometryLines as gl
from StaticDB.StaticData.SpaceDataRepresentation import SpaceDataRepresentation
from StaticDB.StaticData.SystemChoices import SystemType, CalculationOptions, COLOR_CHOICES
from Terminals.models import DeviceGeometry, EquipmentBase
from django_pandas.io import read_frame
from Terminals.service.Core.ChooseTerminalFromDBModel import ChooseTerminalsInstanceFromDB
from Terminals.service.Core.InsertTerminalsСalculation import InsertTerminals
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.patches import Polygon as mplPolygon
import matplotlib.colors as mcolors
from Terminals.service.PlotePolygons.PlotTerminals import StaticPlots
from dataclasses import dataclass

matplotlib.use('Agg')


@dataclass
class TerminalData:
	family_device_name: str = None
	family_instance_name: str = None
	geometry: str = None
	minimum_device_number: int = None
	dimension1: float = None
	points_2d_plot: list[float] = None
	system_name: str = None


class BaseModel(models.Model):
	creation_stamp = models.DateTimeField(auto_now_add=True, verbose_name="дата создания", null=True)
	update_stamp = models.DateTimeField(auto_now=True, verbose_name="дата изменения", null=True)

	class Meta:
		abstract = True


class SystemName(BaseModel):
	system_type = models.CharField(max_length=200, choices=SystemType.choices(), default=SystemType.choices()[0])
	system_name = models.CharField(max_length=200)
	system_color = models.CharField(max_length=200, choices=COLOR_CHOICES, default=COLOR_CHOICES[0])

	def __str__(self):
		return self.system_name

	class Meta:
		verbose_name = 'Система Наименование'
		verbose_name_plural = 'Система Наименование'


class SystemData(BaseModel, SpaceDataRepresentation):
	choices = SystemType.choices()
	system_type = models.CharField(max_length=20,
	                               choices=choices,
	                               default=choices[0]
	                               )
	space = models.OneToOneField("Spaces.SpaceData", on_delete=models.CASCADE, primary_key=True)
	system_name = models.ForeignKey(SystemName, on_delete=models.CASCADE)
	auto_calculate_flow = models.BooleanField(default=True)
	calculation_options = models.CharField(max_length=200,
	                                       choices=CalculationOptions.choices(),
	                                       default=CalculationOptions.choices()[0])
	family_device_name = models.CharField(max_length=200)
	system_flow = models.FloatField(default=0, null=True, blank=True)
	device_area = models.FloatField(null=True, blank=True)
	directive_terminals = models.FloatField(null=True, blank=True)
	directive_length = models.FloatField(null=True, blank=True)
	geometry_options_model = models.ForeignKey(DeviceGeometry, on_delete=models.CASCADE)
	terminal_base = read_frame(EquipmentBase.objects.all(), verbose=False)

	def _checking_calculation_option(self) -> pd.DataFrame:
		if self.calculation_options == CalculationOptions.directive_terminals_number.name and self.directive_terminals:
			return self._get_terminal_db().get_terminal_from_points_number(self.directive_terminals)
		if self.calculation_options == CalculationOptions.directive_length.name and self.directive_length:
			calculated_points = math.ceil(
				self._create_terminal_instance().get_long_curve_length() / self.directive_length)
			return self._get_terminal_db().get_terminal_from_points_number(calculated_points)
		if self.calculation_options == CalculationOptions.device_area.name and self.device_area:
			calculated_points = math.ceil(self.space.S_area / self.device_area)
			return self._get_terminal_db().get_terminal_from_points_number(calculated_points)
		elif self.calculation_options == CalculationOptions.minimum_terminals.name:
			return self._get_terminal_db().get_minimum_device_number()

	def _get_terminal_db(self):
		return ChooseTerminalsInstanceFromDB(self.terminal_base, self.family_device_name, self.system_flow)

	def _create_offset_polygon(self):
		return self.space.create_polygon().buffer(-self.geometry_options_model.wall_offset, join_style=2)

	def _get_lines_from_polygon(self):
		if isinstance(self._create_offset_polygon(), Polygon):
			return gl.GeometryUtility.get_lines_in_polygon(self._create_offset_polygon().exterior.coords)

	def _create_terminal_instance(self, device_points_number=1) -> InsertTerminals:
		return InsertTerminals(
			self._get_lines_from_polygon(),
			self.geometry_options_model.device_orientation_option1,
			self.geometry_options_model.device_orientation_option2,
			self.geometry_options_model.single_device_orientation,
			device_points_number)

	@property
	def terminal_data(self) -> TerminalData:
		data_list = ['minimum_device_number', 'family_device_name', 'family_instance_name', 'geometry',
		             'minimum_device_number', 'dimension1']
		data_dict = {val: self._checking_calculation_option()[val].iloc[0] for val in data_list}
		terminals = self._create_terminal_instance(device_points_number=data_dict.get('minimum_device_number'))
		terminal_data = TerminalData(**data_dict)
		points_2d_plot = terminals.get_terminals_points_locations()
		terminal_data.points_2d_plot = points_2d_plot
		terminal_data.system_name = self.system_name
		return terminal_data

	def draw_terminals(self, fig=None, ax=None):

		if not fig and not ax:
			fig, ax = plt.subplots()
		points_coordinates = self.terminal_data.points_2d_plot
		StaticPlots.plot_scatters(ax, points_coordinates,
		                          dimension=self.terminal_data.dimension1,
		                          geometry=self.terminal_data.geometry,
		                          color=self.system_name.system_color

		                          )
		StaticPlots.add_text_to_df_terminals_points_column(ax, points_coordinates, self.system_name)
		plt.axis('off')
		return fig

	def calculate_device(self):
		fig, ax = plt.subplots()
		try:
			x, y = self.space.create_polygon().exterior.xy
			ax.plot(x, y, color="blue")
			self.draw_terminals(fig, ax)
			return mark_safe(StaticPlots.save_plot(fig))
		except Exception as e:
			print(e)

	class Meta:
		abstract = True
		ordering = ['system_name']

	def __str__(self):
		return self.system_name.system_name


class SupplySystem(SystemData):
	choices = SystemType.choices()
	system_type = models.CharField(max_length=20,
	                               choices=choices,
	                               default=choices[0]
	                               )

	class Meta:
		verbose_name = f"Система {SystemType.Supply_system.value}"
		verbose_name_plural = f"Система {SystemType.Supply_system.value}"


class ExhaustSystem(SystemData):
	choices = SystemType.choices()
	system_type = models.CharField(max_length=20,
	                               choices=choices,
	                               default=choices[1]
	                               )

	class Meta:
		verbose_name = f"Система {SystemType.Exhaust_system.value}"
		verbose_name_plural = f"Система {SystemType.Exhaust_system.value}"


class FancoilSystem(SystemData):
	choices = SystemType.choices()
	system_type = models.CharField(max_length=20,
	                               choices=choices,
	                               default=choices[2]
	                               )

	class Meta:
		verbose_name = f"Система {SystemType.Fan_coil_system.value}"
		verbose_name_plural = f"Система {SystemType.Fan_coil_system.value}"


class HeatSystem(SystemData):
	choices = SystemType.choices()
	system_type = models.CharField(max_length=20,
	                               choices=choices,
	                               default=choices[3]
	                               )

	class Meta:
		verbose_name = f"Система {SystemType.Heat_system.value}"
		verbose_name_plural = f"Система {SystemType.Heat_system.value}"
