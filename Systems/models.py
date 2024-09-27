import math
import numpy as np
import pandas as pd
from django.db import models
from django.utils.safestring import mark_safe
import Terminals.service.Geometry.GeometryLines as gl
from HvacAppDjango.models.BaseModel import BaseModel
from StaticDB.StaticData.SpaceDataRepresentation import SpaceDataRepresentation
from StaticDB.StaticData.SystemChoices import SystemType, CalculationOptions, COLOR_CHOICES
from Terminals.models import DeviceGeometry, EquipmentBase
from django_pandas.io import read_frame
from Terminals.service.Core.ChooseTerminalFromDBModel import ChooseTerminalsInstanceFromDB
from Terminals.service.Core.InsertTerminalsСalculation import InsertTerminals
import matplotlib
from matplotlib import pyplot as plt
from Terminals.service.PlotePolygons.PlotTerminals import StaticPlots
from dataclasses import dataclass, field
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

matplotlib.use('Agg')
from loguru import logger

DATA_LIST = ['minimum_device_number',
             'family_device_name',
             'family_instance_name',
             'max_flow', 'geometry',
             'minimum_device_number',
             'dimension1'
             ]

REPORT_LIST = {'family_device_name': 'Семейство',
               'family_instance_name': 'Экземляр',
               'minimum_device_number': 'Кол-во',
               'max_flow': 'Макс. Расход',
               'local_flow': 'Факт. Расход',
               'k_ef': 'Кэф'
               }


@dataclass
class TerminalData:
	family_device_name: str = None
	family_instance_name: str = None
	max_flow: float = None
	geometry: str = None
	minimum_device_number: int = None
	dimension1: float = None
	points_2d_plot: list[float] = None
	system_name: str = None
	system_flow: float = None
	local_flow: float = field(init=False)
	k_ef: float = field(init=False)

	def __post_init__(self):
		if self.system_flow and self.max_flow and self.minimum_device_number:
			self.local_flow = self.system_flow / self.minimum_device_number
			self.k_ef = self.local_flow / self.max_flow
		else:
			self.k_ef = 0
			self.local_flow = 0


class SystemName(BaseModel):
	system_type = models.CharField(max_length=200, choices=SystemType.choices(), default=SystemType.choices()[0])
	system_name = models.CharField(max_length=200)
	system_color = models.CharField(max_length=200, choices=COLOR_CHOICES, default=COLOR_CHOICES[0])

	def __str__(self):
		return self.system_name

	class Meta:
		verbose_name = 'Система Наименование'
		verbose_name_plural = 'Система Наименование'


class SystemData(SpaceDataRepresentation):
	system_type_choices = SystemType.choices()
	system_type = models.CharField(max_length=20,
	                               choices=system_type_choices,
	                               default=system_type_choices[0]
	                               )
	space = models.OneToOneField("Spaces.SpaceData", on_delete=models.CASCADE, primary_key=True)
	system_name = models.ForeignKey(SystemName, on_delete=models.CASCADE)
	auto_calculate_flow = models.BooleanField(default=True)
	calculation_options = models.CharField(max_length=200,
	                                       choices=CalculationOptions.choices(),
	                                       default=CalculationOptions.choices()[0], null=True, blank=True
	                                       )
	family_device_name = models.ForeignKey('DeviceFamily', on_delete=models.SET_NULL, null=True, blank=True)
	system_flow = models.FloatField(default=0, null=True, blank=True)
	device_area = models.FloatField(null=True, blank=True)
	directive_terminals = models.FloatField(null=True, blank=True)
	directive_length = models.FloatField(null=True, blank=True)
	geometry_options_model = models.ForeignKey(DeviceGeometry, on_delete=models.SET_NULL, null=True, blank=True)
	calculation_result = models.JSONField(null=True, blank=True, verbose_name='Результаты расчета')

	def save(self, *args, **kwargs):
		# Преобразуйте данные в словарь
		if isinstance(self.create_terminal_data(), TerminalData):
			self.calculation_result = self.create_terminal_data().__dict__
		super().save(*args, **kwargs)

	@property
	def convert_equipment_base_to_DF(self) -> pd.DataFrame:
		return read_frame(EquipmentBase.objects.all(), verbose=False)

	def _checking_calculation_option(self) -> pd.DataFrame:
		terminal_instance = ChooseTerminalsInstanceFromDB(self.convert_equipment_base_to_DF,
		                                                  self.family_device_name.family_device_name,
		                                                  self.system_flow)
		# заданное количество
		if self.calculation_options == CalculationOptions.directive_terminals_number.name and self.directive_terminals:
			return terminal_instance.get_terminal_from_points_number(self.directive_terminals)
		# заданная длина
		if (
				self.calculation_options == CalculationOptions.directive_length.name
				and self._is_space_has_polygon()
				and self.directive_length
		):
			calculated_points = math.ceil(
				self._create_terminal_instance().get_long_curve_length() / self.directive_length)
			return terminal_instance.get_terminal_from_points_number(calculated_points)
		# заданная площадь
		if self.calculation_options == CalculationOptions.device_area.name and self.device_area:
			calculated_points = math.ceil(self.space.S_area / self.device_area)
			return terminal_instance.get_terminal_from_points_number(calculated_points)
		# минимальное количество
		if self.calculation_options == CalculationOptions.minimum_terminals.name:
			return terminal_instance.get_minimum_device_number()
		# минимальное количество
		else:
			return terminal_instance.get_minimum_device_number()

	def _is_space_has_polygon(self) -> bool:
		try:
			self.space.create_polygon()
			return True
		except Exception as e:
			logger.error(f"Ошибка при создании полигона: {e}")
			return False

	def _get_lines_from_polygon(self):
		polygon = self.space.create_polygon()
		try:
			offset_polygon = polygon.buffer(-self.geometry_options_model.wall_offset, join_style=2)
			if offset_polygon:
				return gl.GeometryUtility.get_lines_in_polygon(offset_polygon.exterior.coords)
			else:
				return gl.GeometryUtility.get_lines_in_polygon(polygon.exterior.coords)
		except Exception as e:
			logger.error(f"Ошибка при создании полигона {self.space.S_ID}': {e}")

	def _create_terminal_instance(self, device_points_number=1) -> InsertTerminals:
		perimeter_curve = self._get_lines_from_polygon()

		return InsertTerminals(
			perimeter_curve,
			self.geometry_options_model.device_orientation_option1,
			self.geometry_options_model.device_orientation_option2,
			self.geometry_options_model.single_device_orientation,
			device_points_number)

	def create_terminal_data(self) -> TerminalData:
		data_dict = {}

		def repeat_tuple(tuple_to_repeat: tuple[float, float], times: int) -> list[tuple[float, float]]:
			if times and tuple_to_repeat:
				return [tuple_to_repeat] * int(times)

		def _encoder(obj):
			if isinstance(obj, (np.int64, np.float64)):
				return float(obj)  # Преобразуем в float для обоих типов
			else:
				return obj

		try:
			# получаем первое значение из DF из столбцов data_list
			data_dict = {val: _encoder(self._checking_calculation_option()[val].iloc[0]) for val in DATA_LIST}

		except Exception as e:
			logger.error(f"Ошибка при получении данных terminal_data из DataFrame: {e}")
			if data_dict:
				try:
					terminal_data = TerminalData(**data_dict,
					                             system_flow=self.system_flow,
					                             system_name=self.system_name.system_name)
					terminals = self._create_terminal_instance(
						device_points_number=data_dict.get('minimum_device_number'))
					points_2d_plot = terminals.get_terminals_points_locations()
					terminal_data.points_2d_plot = points_2d_plot
					return terminal_data

				except Exception as e:
					terminal_data = TerminalData(**data_dict,
					                             system_flow=self.system_flow,
					                             system_name=self.system_name.system_name)
					terminal_data.points_2d_plot = repeat_tuple(
						(self.space.geometry_data.get('pcx'),
						 self.space.geometry_data.get('pcy'),
						 ), terminal_data.minimum_device_number)
					logger.error(f"Ошибка при создания класса TerminalData : {e}")
					return terminal_data

	def represented_terminal_data(self) -> pd.DataFrame:

		try:
			return pd.DataFrame([self.create_terminal_data()])[REPORT_LIST.keys()].rename(REPORT_LIST, axis=1)
		except Exception as e:
			logger.error(f"Ошибка при созаднии DataFrame {self.space.S_ID}: {e}")
			return pd.DataFrame()

	def _draw_terminals(self, fig=None, ax=None):
		if not fig and not ax:
			fig, ax = plt.subplots()
		points_coordinates = self.calculation_result.get('points_2d_plot')
		if points_coordinates:
			StaticPlots.plot_scatters(ax, points_coordinates,
			                          dimension=self.calculation_result.get('dimension1'),
			                          geometry=self.calculation_result.get('geometry'),
			                          color=self.system_name.system_color
			                          )
			StaticPlots.add_text_to_df_terminals_points_column(ax, points_coordinates, self.system_name)
			plt.axis('off')
			return fig
		else:
			return fig

	def draw_terminals_and_polygons(self):
		fig, ax = plt.subplots()
		try:
			x, y = self.space.create_polygon().exterior.xy
			ax.plot(x, y, color="blue")
			self._draw_terminals(fig, ax)
			return mark_safe(StaticPlots.save_plot(fig))
		except Exception as e:
			logger.error(f"""Ошибка при отрисовки терминалов и полигонов в matplotlib space {self.space.S_ID}  
            system name {self.system_name} system name {self.system_type}: {e}
            """)

	class Meta:
		abstract = True
		ordering = ['system_name']

	def __str__(self):
		return self.system_name.system_name


class SupplySystem(SystemData):
	system_type = models.CharField(max_length=20,
	                               choices=SystemData.system_type_choices,
	                               default=SystemData.system_type_choices[0]
	                               )

	class Meta:
		verbose_name = f"Система {SystemType.Supply_system.value}"
		verbose_name_plural = f"Система {SystemType.Supply_system.value}"


class ExhaustSystem(SystemData):
	system_type = models.CharField(max_length=20,
	                               choices=SystemData.system_type_choices,
	                               default=SystemData.system_type_choices[1]
	                               )

	class Meta:
		verbose_name = f"Система {SystemType.Exhaust_system.value}"
		verbose_name_plural = f"Система {SystemType.Exhaust_system.value}"


class FancoilSystem(SystemData):
	system_type = models.CharField(max_length=20,
	                               choices=SystemData.system_type_choices,
	                               default=SystemData.system_type_choices[2]
	                               )

	class Meta:
		verbose_name = f"Система {SystemType.Fan_coil_system.value}"
		verbose_name_plural = f"Система {SystemType.Fan_coil_system.value}"


class HeatSystem(SystemData):
	system_type = models.CharField(max_length=20,
	                               choices=SystemData.system_type_choices,
	                               default=SystemData.system_type_choices[3]
	                               )

	class Meta:
		verbose_name = f"Система {SystemType.Heat_system.value}"
		verbose_name_plural = f"Система {SystemType.Heat_system.value}"


class DeviceFamily(models.Model):
	"""Вспомогательная модель для хранения уникальных названий семейств устройств."""
	system_equipment_type = models.CharField(max_length=200)
	family_device_name = models.CharField(max_length=300, unique=True)

	def __str__(self):
		return self.family_device_name


@receiver(post_save, sender=EquipmentBase, dispatch_uid='update_device_families')
def update_device_families(sender: EquipmentBase, instance: EquipmentBase, created, **kwargs):
	"""Обновляет модель DeviceFamily при создании или обновлении EquipmentBase.
    """

	# Создаем или обновляем запись в DeviceFamily
	DeviceFamily.objects.update_or_create(
		system_equipment_type=instance.system_equipment_type,
		family_device_name=instance.family_device_name,
		defaults={
			'system_equipment_type': instance.system_equipment_type,
			'family_device_name': instance.family_device_name,
		},
	)


@receiver(post_delete, sender=EquipmentBase, dispatch_uid='delete_device_family')
def delete_device_family(sender, instance, **kwargs):
	"""Удаляет DeviceFamily, если она больше не используется EquipmentBase.
    """
	# Проверяем, есть ли еще записи EquipmentBase с таким же family_device_name
	if not EquipmentBase.objects.filter(family_device_name=instance.family_device_name).exists():
		# Если нет, удаляем DeviceFamily
		try:
			DeviceFamily.objects.get(family_device_name=instance.family_device_name).delete()
		except DeviceFamily.DoesNotExist:
			pass  # DeviceFamily уже удалена


@receiver(pre_save, sender=SystemName)
def set_unique_color(sender, instance, **kwargs):
	"""
    При создании SystemName устанавливает уникальный цвет из COLOR_CHOICES.
    """
	if not instance.pk:  # Проверяем, что объект создается, а не обновляется
		all_colors = set([color[0] for color in COLOR_CHOICES])
		taken_colors = set(SystemName.objects.values_list('system_color', flat=True))
		available_colors = list(all_colors - taken_colors)
		if available_colors:
			instance.system_color = available_colors[0]
