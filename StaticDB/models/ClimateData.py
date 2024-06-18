from django.db import models

from StaticDB.models.SunRadiationData import SunRadiationData


class ClimateData(models.Model):
    name = models.CharField(max_length=15, verbose_name="Город", default="Москва")
    t_out_max = models.FloatField(
        verbose_name="Расчетная температура наружного воздуха °С",
        help_text='Температура холодной пятидневки с обеспеченностью 0.92',
        default=-26
    )
    z_ot = models.FloatField(
        verbose_name="Продолжительность отопительного периода, сут",
        default=204,
        help_text='Продолжительность отопительного периода',
    )
    t_ot_middle = models.FloatField(
        verbose_name="Средняя температура воздуха отопительного периода",
        default=-2.2,
        help_text='Средняя температура воздуха отопительного периода °С'
    )
    air_velocity_middle = models.FloatField(verbose_name="средняя скорость наружного воздуха м/с", default=3.8, )
    air_velocity_max = models.FloatField(verbose_name="максимальная скорость наружного воздуха м/с", default=3.8)
    sun_radiation = models.ForeignKey(SunRadiationData,
                                      verbose_name="Солнечная радиация",
                                      default=1,
                                      blank=True,
                                      null=True,
                                      on_delete=models.DO_NOTHING,
                                      )
    creation_stamp = models.DateTimeField(auto_now_add=True, verbose_name="дата создания")
    update_stamp = models.DateTimeField(auto_now=True, verbose_name="дата изменения")

    class Meta:
        verbose_name = "Климатические данные"
        verbose_name_plural = "Климатические данные"

    def __str__(self):
        return f"город {self.name}"
