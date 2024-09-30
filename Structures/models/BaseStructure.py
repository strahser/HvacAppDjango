import pandas as pd
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from typing import Iterable

from Config.models import Building
from StaticDB.StaticData.StructureTypeData import StructureTypeData
from Structures.Utils.TableRender import df_html
from Structures.models.BaseModel import BaseModelStructure


class BaseStructure(BaseModelStructure):
    """шаблон типовых конструкций, без конкретной площади. Например навесной фасад.
    Состоит из множества слоев. Опционально можем расчитать ГСОП конструкции и получить нормируемый коэффицент теплопередачи,
    если выберим здания/здание (множественный выбор)
    """

    R_real = models.FloatField(verbose_name="Факт.терм. сопр.", null=False, blank=False, default=1,
                               help_text="принимается в расчетах если не заданы слои конструкций")
    standard_structure_type = models.CharField(max_length=200,
                                               choices=StructureTypeData.choices(),
                                               default=StructureTypeData.wall,
                                               verbose_name="тип констр.",
                                               )
    structure_picture = models.ImageField(verbose_name="Изображение", blank=True, upload_to="StructureType/%Y/%m/%d/")

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "03 Базовая конструкция"
        verbose_name_plural = "03 Базовые конструкции"
        ordering = ['id']

    @property
    def calculate_heat_resistance_normative(self):
        try:
            qs1 = Building.objects.all()
            modal_body = self.render_gsop_table()[1]
            return mark_safe(f"""
			<div class="container"><details> <summary>Показать Таблицу</summary><div>{modal_body}</div></details></div>
			""")
        except:
            return ""
    calculate_heat_resistance_normative.fget.short_description = 'Терм. сопрот.расчетное'

    def render_gsop_table(self):
        building_qs =Building.objects.all()
        gsop_list = [val.GSOP for val in building_qs]
        R_norm = [getattr(val,self.standard_structure_type) for val in Building.objects.all()]
        data = {"Здание": [val.name for val in building_qs],
                "Город": [val.climate_data.name for val in building_qs],
                "ГСОП": gsop_list,
                "R_норматив": R_norm,
                "R_факт": self.R_real
                }
        df = pd.DataFrame(data)
        if not df.empty:
            return data, df_html(pd.DataFrame(df))
