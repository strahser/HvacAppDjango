from django.db import models

from StaticDB.StaticData.StructureTypeData import StructureTypeData


class SunRadiationData(models.Model):
    name = models.CharField(verbose_name="Наименование", default="Москва",max_length=200)
    N = models.FloatField(verbose_name="С", default=100)
    S = models.FloatField(verbose_name="Ю", default=360)
    E = models.FloatField(verbose_name="В", default=350)
    W = models.FloatField(verbose_name="З", default=350)
    NW = models.FloatField(verbose_name="СЗ", default=350)
    NE = models.FloatField(verbose_name="СВ", default=350)
    SE = models.FloatField(verbose_name="ЮВ", default=350)
    SW = models.FloatField(verbose_name="ЮЗ", default=350)
    horizontal = models.FloatField(verbose_name="горизонтальная", default=350)
    creation_stamp = models.DateTimeField(auto_now_add=True, verbose_name="дата создания")
    update_stamp = models.DateTimeField(auto_now=True, verbose_name="дата изменения")

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Солнечная радиация"
        verbose_name_plural = "Солнечная радиация"
