from typing import Any, List
from django import forms
from AdminUtils import get_standard_display_list
from Systems.models import SupplySystem, SystemData
from Terminals.models import EquipmentBase


class SystemForm(forms.ModelForm):
    class Meta:
        model = SupplySystem
        fields = get_standard_display_list(SystemData, excluding_list=['space'])

    try:
        family_device_name = forms.ChoiceField(
            choices=[
                (choice, choice) for choice in EquipmentBase.objects.values_list(
                    'family_device_name', flat=True
                ).distinct()
            ],
            required=False,
        )
    except:
        pass
