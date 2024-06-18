from django.contrib import admin
from django.views.generic import TemplateView
from django_custom_admin_pages.views.admin_base_view import AdminBaseView

from HeatBalance.Models.AirBalance.AirBalanceModel import AirBalance
from HeatBalance.Models.HeatLoadData.HeatLoadUtility import HeatLoadUtility


class HeatLoadAdminView(AdminBaseView, TemplateView):
    view_name = "Тепловой баланс"
    template_name = "Spaces/HeatBalance.html"

    # app_label = "admin"
    def get_context_data(self, *args, **kwargs):
        context: dict = super().get_context_data(*args, **kwargs)
        df = HeatLoadUtility.calculate_total_heat_load()
        HeatLoadUtility.create_filter_fancoil_system(df)
        # messages.success(self.request, f"система {system.first()} обнавлен расход {row['total_heat_load']}")
        context["df"] = df.to_html(index=False, classes="table table-striped")
        context["title"] = self.view_name
        # context["query"] = df_filter
        return context


class AirBalanceAdminView(AdminBaseView, TemplateView):
    view_name = "Воздушный баланс"
    template_name = "Spaces/HeatBalance.html"

    # app_label = "admin"
    def get_context_data(self, *args, **kwargs):
        context: dict = super().get_context_data(*args, **kwargs)
        df = AirBalance.calculate_air_balance_query()
        context["df"] = df.data.to_html(index=False, classes="table table-striped")
        context["title"] = self.view_name
        context["query"] = df.query
        return context

# # register the view after you create it
# admin.site.register_view(HeatLoadAdminView)
# admin.site.register_view(AirBalanceAdminView)
