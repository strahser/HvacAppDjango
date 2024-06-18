from django.db import models


class SpaceCategory(models.Model):
    name = models.CharField(max_length=200,verbose_name="Категория", default="Офис",)
    lighting = models.FloatField(verbose_name="Освещ. Вт/м2", default=20)
    human_heat = models.FloatField(verbose_name="Люди. Вт/чел", default=150)
    area_for_person = models.FloatField(verbose_name="Пл.на чел м2/чел", default=7)
    min_temp = models.FloatField(verbose_name="Мин.темп. С", default=18)
    max_temp = models.FloatField(verbose_name="Макс.темп. С", default=22)
    phi_min = models.FloatField(verbose_name="Мин.влаж. %", default=40)
    phi_max = models.FloatField(verbose_name="Макс.влаж. %", default=60)
    Sup_air_mult = models.FloatField(verbose_name="Крат.приток", default=2)
    Ex_air_mult = models.FloatField(verbose_name="Крат.вытяжка", default=2)
    sup_air_human = models.FloatField(verbose_name="Гигиен.треб. м3/чел", default=60)
    fresh_air = models.FloatField(verbose_name="процент свеж. возд.", default=0.8)

    creation_stamp = models.DateTimeField(auto_now_add=True, verbose_name="дата создания")
    update_stamp = models.DateTimeField(auto_now=True, verbose_name="дата изменения")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория Помещения"
        verbose_name_plural = "Категории Помещений"
