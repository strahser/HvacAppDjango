from django.db import models

from StaticDB.StaticData.BuildingCategory import BuildingCategory
from StaticDB.models.ClimateData import ClimateData


class Building(models.Model):
    name = models.CharField(max_length=200, verbose_name="наименование")

    category = models.CharField(max_length=150, choices=[(val.name, val.value) for val in BuildingCategory],
                                default=BuildingCategory.living.name,
                                verbose_name="категория помещения")
    climate_data = models.ForeignKey(ClimateData, on_delete=models.DO_NOTHING, verbose_name="климат.данные")
    building_temperature = models.FloatField(verbose_name="внутренняя температура °С", default=20)
    heated_volume = models.FloatField(verbose_name="отапливаемый объем м3", default=34229)
    level_number = models.IntegerField(verbose_name="количество этажей", default=20)
    level_height = models.FloatField(verbose_name="высота этажа,м", default=3)
    creation_stamp = models.DateTimeField(auto_now_add=True, verbose_name="дата создания")
    update_stamp = models.DateTimeField(auto_now=True, verbose_name="дата изменения")

    class Meta:
        verbose_name = "Здание"
        verbose_name_plural = "Здания"

    @property
    def GSOP(self):
        return (self.building_temperature - self.climate_data.t_ot_middle) * self.climate_data.z_ot

    GSOP.fget.short_description = 'ГСОП'

    def __str__(self):
        return f"{self.name} город {self.climate_data.name}"
