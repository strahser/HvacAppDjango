from pprint import pprint

from django.db import models
from django.urls import reverse
from django.contrib import admin
from django.db.models import Count
from Spaces.models import SpaceData
from StaticDB.StaticData.OrientationData import OrientationData
from StaticDB.StaticData.SpaceDataRepresentation import SpaceDataRepresentation
from StaticDB.StaticData.StructureTypeData import StructureTypeData
from StaticDB.models.SunRadiationData import SunRadiationData
from Structures.HeatCalculation.StructureThermalResistenceCoefficient import \
	get_normative_thermal_resistence_coefficient
from Structures.models.BaseModel import BaseModel
from Structures.models.BaseStructure import BaseStructure
from dataclasses import dataclass


@dataclass
class DisplayTypeConstruction:
	name: str
	value: str

	def __str__(self):
		return self.value


class Structure(BaseModel, SpaceDataRepresentation):
	space = models.ForeignKey(SpaceData, verbose_name="Помещение", on_delete=models.CASCADE,
	                          related_name='rooms', null=True)
	name = models.CharField(max_length=250, verbose_name="крат.наим", blank=True, null=True)
	base_structures = models.ForeignKey(BaseStructure,
	                                    verbose_name="Базовая конструкция",
	                                    on_delete=models.CASCADE,
	                                    related_name='base_structure')
	orientation = models.CharField(
		max_length=50, blank=False, null=False, choices=OrientationData.choices(),
		verbose_name="ориент.", default=OrientationData.ND.name
	)
	width = models.FloatField(verbose_name='Ширина', default=1, null=True, blank=True)
	length = models.FloatField(verbose_name='Длина', default=1, null=True, blank=True)
	quantity = models.FloatField(verbose_name='Колличество конструкций', default=1, null=True, blank=True)
	area = models.FloatField(verbose_name="пл.констр.", null=True, default=1)

	def save(self, *args, **kwargs):
		if self.width > 0 and self.length > 0 and self.quantity > 0:
			self.area = self.width * self.length * self.quantity
			super().save(*args, **kwargs)
		else:
			super().save(*args, **kwargs)

	class Meta:
		verbose_name = "Ограждающая конструкция"
		verbose_name_plural = "Ограждающие конструкции"
		ordering = ['base_structures__name']

	def __str__(self):
		return f"{self.name}"

	@admin.display(description='Kф')
	def K_real(self):
		return round(1 / self.R_real(), 2)

	@admin.display(description='Тип констр.', ordering='base_structures')
	def standard_structure_type(self):
		qs = Structure.objects.get(pk=self.pk).base_structures.standard_structure_type
		type = getattr(StructureTypeData, f'{qs}')
		display_data = DisplayTypeConstruction(type.name, type.value)
		return display_data

	@admin.display(description='RNorm')
	def R_Norm(self):
		gsop = self.space.building.GSOP
		r_norm = get_normative_thermal_resistence_coefficient(gsop).get(self.standard_structure_type().name)
		return round(r_norm, 2)

	@admin.display(description='Rфакт')
	def R_real(self):
		qs = Structure.objects.get(pk=self.pk).base_structures.R_real
		return qs

	@admin.display(description='tв, С')
	def t_in(self):
		return self.space.t_min

	@admin.display(description='tн, С')
	def t_out(self):
		return self.space.t_out_max

	@admin.display(description='Коэф.ориен.')
	def k_orient(self):
		return getattr(OrientationData, self.orientation).value.k_heat

	@admin.display(description='Угл.Пом.')
	def corner_space_coefficient(self):
		try:
			k_corner_query = Structure.objects.select_related('space').values(
				'base_structures__standard_structure_type').filter(space=self.space) \
				.filter(base_structures__standard_structure_type=StructureTypeData.Wall.name) \
				.annotate(unique=Count('orientation', distinct=True)
			              )
			unique_wall_number = [val.get('unique') for val in k_corner_query][0]
			return 1 if unique_wall_number < 2 else 1.1
		except:
			return 1

	@admin.display(description='Теплопотери,Вт')
	def calculate_heat_loss(self):
		return round(self.K_real() * self.area * self.k_orient() * self.corner_space_coefficient() * (
				self.t_in() - self.t_out()), 1)


class StructureRadiation(Structure):
	class Meta:
		proxy = True
		verbose_name = "Конструкция Радиация"
		verbose_name_plural = "Конструкции Радиация"
		ordering = ['base_structures__name']

	@admin.display(description='Удельная радиация,Вт', ordering='')
	def radiation_data(self):
		radiation = (
			SunRadiationData.objects
			.filter(id=self.space.building.climate_data.sun_radiation.id)
			.filter(standard_structure_type=self.base_structures.standard_structure_type).first()
		)
		if radiation:
			try:
				return getattr(radiation, self.orientation)
			except:
				pass

	@admin.display(description='Суммарная радиация,Вт', ordering='')
	def calculate_radiation(self):
		try:
			return self.radiation_data() * self.area
		except:
			return 0
