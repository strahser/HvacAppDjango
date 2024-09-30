import numpy as np
from django.db import models

from StaticDB.StaticData.StaticCoefficientStructures import StaticCoefficientStructures
from StaticDB.models.BuildingType import BuildingType, BuildingProperty
from StaticDB.models.ClimateData import ClimateData
from dataclasses import dataclass


@dataclass
class NormativeData:
    wall: float
    door: float
    window: float
    floor: float
    roof: float
    skylight: float


class Building(models.Model):
    name = models.CharField(max_length=200, verbose_name="наименование")
    category = models.ForeignKey(BuildingType, on_delete=models.DO_NOTHING, verbose_name="категория здания")
    climate_data = models.ForeignKey(ClimateData, on_delete=models.DO_NOTHING, verbose_name="климат.данные")
    building_temperature = models.FloatField(verbose_name="внутренняя температура °С", default=20)
    heated_volume = models.FloatField(verbose_name="отапливаемый объем м3", default=34229)
    level_number = models.IntegerField(verbose_name="количество этажей", default=20)
    level_height = models.FloatField(verbose_name="высота этажа,м", default=3)
    wall = models.FloatField(verbose_name="Норм.Стена", null=True, blank=True)
    door = models.FloatField(verbose_name="Норм.Дверь", null=True, blank=True)
    window = models.FloatField(verbose_name="Норм.Окно", null=True, blank=True)
    floor = models.FloatField(verbose_name="Норм.Перекрытие", null=True,
                              blank=True)  # Покрытий и перекрытий над проездами
    roof = models.FloatField(verbose_name="Норм.Кровля", null=True,
                             blank=True)  # Перекрытий чердачных, над неотапливаемыми подпольями и подвалами
    skylight = models.FloatField(verbose_name="Норм.Зенитный фонарь", null=True,
                                 blank=True)  # -Зенитных фонарей
    creation_stamp = models.DateTimeField(auto_now_add=True, verbose_name="дата создания")
    update_stamp = models.DateTimeField(auto_now=True, verbose_name="дата изменения")

    class Meta:
        verbose_name = "Здание"
        verbose_name_plural = "Здания"

    @property
    def GSOP(self):
        return (self.building_temperature - self.climate_data.t_ot_middle) * self.climate_data.z_ot

    GSOP.fget.short_description = 'ГСОП'

    def _get_coefficient(self, coefficient_name: str = 'a'):
        return (BuildingProperty.objects
                .filter(building_type=self.category)
                .filter(structure_coefficient__name=coefficient_name)
                .first()
                )

    def calculate_normative_coefficient(self)->NormativeData:
        a = self._get_coefficient('a')
        b = self._get_coefficient('b')
        wall = a.wall * self.GSOP + b.wall
        door = wall * 0.55
        if a.window and b.window:
            window = a.window * self.GSOP + b.window
        else:
            window = np.interp(self.GSOP,
                               StaticCoefficientStructures.normal_window_gsop_base,
                               StaticCoefficientStructures.normal_thermal_coefficient_window_base
                               )
        floor = a.floor * self.GSOP + b.floor
        roof = a.roof * self.GSOP + b.roof
        skylight = a.skylight * self.GSOP + b.skylight
        normative_data = NormativeData(wall=round(wall, 2), door=round(door, 2),
                                       window=round(window, 2), floor=round(floor, 2),
                                       roof=round(roof, 2), skylight=round(skylight, 2))
        return normative_data

    def save(self, *args, **kwargs)->None:
        try:
            normative_data = self.calculate_normative_coefficient()
            self.wall = normative_data.wall
            self.door = normative_data.door
            self.window = normative_data.window
            self.floor = normative_data.floor
            self.roof = normative_data.roof
            self.skylight = normative_data.skylight
            super(Building, self).save(*args, **kwargs)
        except:
            super(Building, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} город {self.climate_data.name}"
