from Spaces.models import SpaceData
from Systems.models import SupplySystem, ExhaustSystem
from django.contrib import admin

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


class AirBalance(SpaceData):

    @admin.display(description='Приток Кратность,м3/ч.', ordering='_supply_air_mult')
    def supply_air_mult(self):
        if self.space_category and self.space_category.Sup_air_mult and self.S_Volume:
            return self.space_category.Sup_air_mult * self.S_Volume
        else: return 0

    @admin.display(description='Вытяжка Кратность,м3/ч.', ordering='_exhaust_air_mult')
    def exhaust_air_mult(self):
        if self.space_category and self.space_category.Ex_air_mult and self.S_Volume:
            return self.space_category.Ex_air_mult * self.S_Volume

        else: return 0
    @admin.display(description='Итого приточный воздух,м3/ч.', ordering='_total_supply_air_balance')
    def total_supply_air_balance(self) -> str:
        """собираем все виды расчетов потребного воздуха на ассимиляцию"""
        sum_data = sum([self.supply_air_mult()])
        self._update_system(SupplySystem, sum_data)
        return sum_data

    @admin.display(description='Итого вытяжной воздух,м3/ч.', ordering='_total_exhaust_air_balance')
    def total_exhaust_air_balance(self) -> str:
        """собираем все виды расчетов потребного воздуха на ассимиляцию"""
        sum_data = sum([self.exhaust_air_mult()])
        self._update_system(ExhaustSystem, sum_data)
        return sum_data

    class Meta:
        verbose_name = "Воздушный баланс"
        verbose_name_plural = "Воздушный баланс"
        proxy = True


def update_system_flow(sender, instance, **kwargs):
    """Обновляет поле system_flow и создает terminal_data, если auto_calculate_flow=True.
    """
    if instance.auto_calculate_flow:
        try:
            air_balance = AirBalance.objects.get(S_ID=instance.space.S_ID)
            if isinstance(instance, SupplySystem):
                instance.system_flow = air_balance.total_supply_air_balance()
            elif isinstance(instance, ExhaustSystem):
                instance.system_flow = air_balance.total_exhaust_air_balance()
            else:
                return  # Неизвестный тип объекта

            instance.calculate_terminal_data()
        except AirBalance.DoesNotExist:
            pass


@receiver(pre_save, sender=SupplySystem)
@receiver(pre_save, sender=ExhaustSystem)
def update_system_flow_on_save(sender, instance, **kwargs):
    """Обновляет поле system_flow и создает terminal_data, если auto_calculate_flow=True.
    """
    update_system_flow(sender, instance, **kwargs)