from django.db import models

from Config.models import Building
from django.contrib import admin

from Systems.models import ExhaustSystem, SupplySystem, FancoilSystem



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

	@admin.display(description='Вытяжная',ordering="exhaustsystem__system_name")
	def ExhaustSystemDisplay(self):
		return ExhaustSystem.objects.filter(space=self.pk).first()

	@admin.display(description='Приточная',ordering="supplysystem__system_name")
	def SupplySystemDisplay(self):
		return SupplySystem.objects.filter(space=self.pk).first()

	@admin.display(description='Кондиционирование',ordering="fancoilsystem__system_name")
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
