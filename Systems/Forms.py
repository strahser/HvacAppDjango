from typing import Any, List
from django import forms
from AdminUtils import get_standard_display_list
from Systems.models import SupplySystem, SystemData, DeviceFamily


class SystemForm(forms.ModelForm):
    class Meta:
        model = SupplySystem
        fields = get_standard_display_list(SystemData, excluding_list=['space'])



