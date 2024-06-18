from Spaces.models import SpaceData
from django.db.models import F, Value, OuterRef
import pandas as pd
from django.utils.safestring import mark_safe
from collections import namedtuple

from Systems.models import FancoilSystem, SupplySystem
from django.contrib import admin


class AirBalance(SpaceData):
    BalanceData = namedtuple("BalanceData", ["data", "query"])

    @admin.display(description='Приток Кратность,м3/ч.')
    def supply_air_mult(self):
        return self.space_category.Sup_air_mult * self.S_Volume

    @admin.display(description='Вытяжка Кратность,м3/ч.')
    def exhaust_air_mult(self):
        return self.space_category.Ex_air_mult * self.S_Volume

    @staticmethod
    def calculate_air_balance_query() -> str:
        supply_air_mult = F("space_category__Sup_air_mult") * F("S_Volume")
        exhaust_air_mult = F("space_category__Ex_air_mult") * F("S_Volume")
        qs = SpaceData.objects \
            .values("S_ID", "S_Number") \
            .annotate(
            supply_air_mult=supply_air_mult,
            exhaust_air_mult=exhaust_air_mult,
            max_supply_air=supply_air_mult,
            max_exhaust_air=exhaust_air_mult,
        )
        supply_air_systems = SupplySystem.objects.all().values_list("space_data__S_ID", flat=True)
        filter_qs = qs.filter(S_ID__in=supply_air_systems)

        # return AirBalance.BalanceData(pd.DataFrame(qs), filter_qs)
        return mark_safe(pd.DataFrame(qs).to_html(escape=True))

    class Meta:
        verbose_name = "Воздушный баланс"
        verbose_name_plural = "Воздушный баланс"
        proxy = True
