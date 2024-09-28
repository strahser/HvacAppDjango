from django.contrib import admin
from django.utils.safestring import mark_safe
from AdminUtils import get_standard_display_list
from Systems.Forms import SystemForm
from Systems.models import SystemName, FancoilSystem, SupplySystem, ExhaustSystem, HeatSystem, SystemData
from loguru import logger

admin.site.index_title = "Системы"


@admin.register(SystemName)
class DeviceTypeAdmin(admin.ModelAdmin):
    list_display = get_standard_display_list(SystemName)
    list_filter = get_standard_display_list(SystemName)


class BaseSystem(admin.ModelAdmin):
    suffix_list = ['Space_ID', 'Space_name', 'Space_number']
    excluding_list = ['space', 'auto_calculate_flow', 'calculation_result']
    additional_filter_list = ['space__S_ID', 'space__S_level', 'space__space_category']
    list_display = suffix_list + get_standard_display_list(SupplySystem,
                                                           excluding_list=excluding_list,
                                                           additional_list=[])
    list_filter = get_standard_display_list(SupplySystem, excluding_list=excluding_list,
                                            additional_list=additional_filter_list)
    form = SystemForm
    fieldsets = (
        ('Общая информация', {
            'fields': ('space', 'system_type', 'system_name', 'system_flow', 'auto_calculate_flow',)
        }),
        ('Оборудование Параметры', {
            'fields': ('family_device_name', 'geometry_options_model',)
        }),
        ('Расчетные Параметры', {
            'fields': (
                'calculation_options', 'device_area', 'directive_terminals', 'directive_length',)
        }),
        ('Результаты расчета', {
            'fields': (
                'calculation_result',)
        }),

    )
    change_form_template = 'jazzmin/admin/change_form.html'

    @property
    def system_type(self):
        return SystemData

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        _filter = self.system_type.objects.filter(space_id=object_id).first()
        try:
            extra_context['polygons'] = _filter.draw_terminals_and_polygons()
            extra_context['terminal_data'] = mark_safe(_filter.represented_terminal_data().to_html(
                escape=True, index=False, classes="table table-striped"))
            return super().change_view(request, object_id, form_url, extra_context=extra_context)
        except Exception as e:
            extra_context['terminal_data'] = "Не возможно создать графическую модель. Проверьте геометрию"
            logger.error(f"Ошибка отрисовки полигона: {e}")

        return super().change_view(request, object_id, form_url, extra_context=extra_context)


@admin.register(SupplySystem)
class SupplySystemAdmin(BaseSystem):

    @property
    def system_type(self):
        return SupplySystem


@admin.register(ExhaustSystem)
class ExhaustSystemAdmin(BaseSystem):
    @property
    def system_type(self):
        return ExhaustSystem


@admin.register(FancoilSystem)
class FancoilSystemAdmin(BaseSystem):
    @property
    def system_type(self):
        return FancoilSystem


@admin.register(HeatSystem)
class HeatSystemAdmin(BaseSystem):
    @property
    def system_type(self):
        return HeatSystem
