from django.db import models
from Spaces.models import SpaceData
from django.contrib import admin

from StaticDB.StaticData.SpaceDataRepresentation import SpaceDataRepresentation
from StaticDB.StaticData.StructureTypeData import StructureTypeData
from Structures.models.Structure import Structure
import logging
from Systems.models import FancoilSystem

logging.basicConfig()
FANCOIL_ID_LIST = FancoilSystem.objects.all().values_list('space', flat=True)


class TotalHeat(SpaceData):

	@admin.display(description='Освещение,Вт.')
	def total_lighting_load(self) -> float:
		return round(self.space_category.lighting * self.S_area, 1)

	@admin.display(description='Люди,Вт.')
	def total_human_load(self) -> float:
		if self.space_category.human_heat and self.human_number:
			return round(self.space_category.human_heat * self.human_number, 1)
		else:
			return 0.0

	@admin.display(description='Радиация,Вт.')
	def total_radiation_load(self) -> float:
		structures = Structure.objects.filter(space=self). \
			filter(base_structures__standard_structure_type=StructureTypeData.Window.name).all()
		data = []
		for structure in structures:
			try:
				radiation_value = getattr(self.building.climate_data.sun_radiation, structure.orientation)
				radiation = structure.area * radiation_value
				data.append(radiation)
			except Exception as e:
				logging.error(e, exc_info=True)
				data.append(0)
		return sum(data)

	@admin.display(description='Оборудование,Вт.')
	def total_equipment_load(self) -> float:
		load = HeatLoadEquipment.objects.filter(space=self).all()
		return sum([val.summary_equipment_load() for val in load])

	@admin.display(description='Дополнительные,Вт.')
	def additional_load(self) -> float:
		load = HeatAdditionalLoad.objects.filter(space=self).all()
		return sum([val.heat_load for val in load])

	@admin.display(description='Всего,Вт.')
	def total_heat_load(self) -> float:
		def __update_cooling_system():
			if self.pk in FANCOIL_ID_LIST:
				system = FancoilSystem.objects.all().filter(space_data__S_ID=self.pk)
				if system.auto_calculate_flow:
					system.update(system_flow=sum_data)

		data = [self.total_equipment_load(), self.total_lighting_load(),
		        self.total_human_load(), self.total_radiation_load(), self.additional_load()]
		sum_data = sum(data)
		__update_cooling_system()
		return sum_data

	def __str__(self):
		return self.S_ID

	class Meta:
		verbose_name = "Тепловой баланс"
		verbose_name_plural = "Тепловой баланс"
		proxy = True


class HeatAdditionalLoad(models.Model, SpaceDataRepresentation):
	space = models.ForeignKey(SpaceData, on_delete=models.CASCADE, verbose_name='Помещение')
	heat_load = models.FloatField(verbose_name='дополнительные теплопотери', null=True, blank=True)

	class Meta:
		verbose_name = "Доп. Тепловыделение"
		verbose_name_plural = "Доп. Тепловыделения"


class HeatLoadEquipment(models.Model, SpaceDataRepresentation):
	space = models.ForeignKey(SpaceData, on_delete=models.CASCADE, verbose_name='Помещение')
	heat_equipment = models.ForeignKey('HeatEquipment', on_delete=models.CASCADE, verbose_name='Наим.обор.')
	quantity = models.IntegerField(default=1, verbose_name='Кол-во')

	@admin.display(description='Тепловыд.,Вт.')
	def equipment_load_local(self) -> float:
		return self.heat_equipment.heat_load

	@admin.display(description='Сумм.Тепловыд.,Вт.')
	def summary_equipment_load(self) -> float:
		return self.equipment_load_local() * self.quantity

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=('space', 'heat_equipment'), name='unique_load')
		]
		verbose_name = "Тепловыделение Оборудование"
		verbose_name_plural = "Тепловыделение Оборудование"
		ordering = ['space']


class HeatEquipment(models.Model):
	name = models.CharField(verbose_name="Оборудование", default="Компьютер", max_length=200)
	heat_load = models.FloatField(verbose_name="Мощность,Вт", default=300, max_length=200)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = "База Оборудования"
		verbose_name_plural = "База Оборудования"
