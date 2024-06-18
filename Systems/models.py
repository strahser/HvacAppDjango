from django.db import models

from StaticDB.StaticData.SpaceDataRepresentation import SpaceDataRepresentation
from StaticDB.StaticData.SystemChoices import SystemType, CalculationOptions
from Terminals.models import DeviceGeometry
from django.contrib import admin


class BaseModel(models.Model):
	creation_stamp = models.DateTimeField(auto_now_add=True, verbose_name="дата создания", null=True)
	update_stamp = models.DateTimeField(auto_now=True, verbose_name="дата изменения", null=True)

	class Meta:
		abstract = True


class SystemName(BaseModel):
	system_type = models.CharField(max_length=200, choices=SystemType.choices(), default=SystemType.choices()[0])
	system_name = models.CharField(max_length=200)

	def __str__(self):
		return self.system_name

	class Meta:
		verbose_name = 'Система Наименование'
		verbose_name_plural = 'Система Наименование'


class SystemData(BaseModel,SpaceDataRepresentation):
	_data_index = 0
	choices = SystemType.choices()
	system_type = models.CharField(max_length=20,
	                               choices=choices,
	                               default=choices[_data_index]
	                               )
	space = models.OneToOneField("Spaces.SpaceData", on_delete=models.CASCADE, primary_key=True)
	system_name = models.ForeignKey(SystemName, on_delete=models.CASCADE)
	calculation_options = models.CharField(max_length=20,
	                                       choices=CalculationOptions.choices(),
	                                       default=CalculationOptions.choices()[0])
	family_device_name = models.CharField(max_length=200)
	system_flow = models.FloatField(default=0, null=True, blank=True)
	device_area = models.FloatField(null=True, blank=True)
	directive_terminals = models.FloatField(null=True, blank=True)
	directive_length = models.FloatField(null=True, blank=True)
	geometry_options_model = models.ForeignKey(DeviceGeometry, on_delete=models.CASCADE)


	class Meta:
		abstract = True
		ordering = ['system_name']

	def __str__(self):
		return self.system_name.system_name


class SupplySystem(SystemData):
	_data_index = 0

	class Meta:
		verbose_name = f"Система {SystemType.Supply_system.value}"
		verbose_name_plural = f"Система {SystemType.Supply_system.value}"


class ExhaustSystem(SystemData):
	_data_index = 1

	class Meta:
		verbose_name = f"Система {SystemType.Exhaust_system.value}"
		verbose_name_plural = f"Система {SystemType.Exhaust_system.value}"


class FancoilSystem(SystemData):
	_data_index = 2

	class Meta:
		verbose_name = f"Система {SystemType.Fan_coil_system.value}"
		verbose_name_plural = f"Система {SystemType.Fan_coil_system.value}"


class HeatSystem(SystemData):
	_data_index = 3

	class Meta:
		verbose_name = f"Система {SystemType.Heat_system.value}"
		verbose_name_plural = f"Система {SystemType.Heat_system.value}"
