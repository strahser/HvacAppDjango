from django.db import models
from Spaces.models import SpaceData
from django.contrib import admin
from StaticDB.StaticData.SpaceDataRepresentation import SpaceDataRepresentation
from Structures.models.Structure import StructureRadiation
from Systems.models import FancoilSystem
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


class HeatBalance(SpaceData):

	@admin.display(description='Освещение,Вт.')
	def total_lighting_load(self) -> float:
		if self.space_category and self.space_category.lighting and self.S_area:
			return round(self.space_category.lighting * self.S_area, 1)
		else:
			return 0

	@admin.display(description='Люди,Вт.')
	def total_human_load(self) -> float:
		if self.space_category and self.space_category.human_heat and self.human_number:
			return round(self.space_category.human_heat * self.human_number, 1)
		else:
			return 0.0

	@admin.display(description='Радиация,Вт.')
	def total_radiation_load(self) -> float:
		res = StructureRadiation.objects.all().filter(space__S_ID=self.pk)
		return sum([val.radiation_data() for val in res if val.radiation_data()])

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
		sum_data = sum([self.total_equipment_load(), self.total_lighting_load(),
		                self.total_human_load(), self.total_radiation_load(), self.additional_load()])
		self._update_system(FancoilSystem, sum_data)
		return sum_data

	def __str__(self):
		return self.S_ID

	class Meta:
		verbose_name = "Тепловой баланс"
		verbose_name_plural = "Тепловой баланс"
		proxy = True


class HeatAdditionalLoad(models.Model, SpaceDataRepresentation):
	space = models.ForeignKey("Spaces.SpaceData", on_delete=models.CASCADE, verbose_name='Помещение')
	heat_load = models.FloatField(verbose_name='дополнительные теплопотери', null=True, blank=True)

	class Meta:
		verbose_name = "Доп. Тепловыделение"
		verbose_name_plural = "Доп. Тепловыделения"


class HeatLoadEquipment(models.Model, SpaceDataRepresentation):
	space = models.ForeignKey("Spaces.SpaceData", on_delete=models.CASCADE, verbose_name='Помещение')
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


@receiver(pre_save, sender=FancoilSystem)
def update_fancoil_system_flow_on_save(sender: FancoilSystem, instance: FancoilSystem, **kwargs):
	if instance.auto_calculate_flow:
		try:
			heat_balance = HeatBalance.objects.get(S_ID=instance.space.S_ID)
			instance.system_flow = heat_balance.total_heat_load()
			instance.calculate_terminal_data()
		except HeatBalance.DoesNotExist:
			pass
