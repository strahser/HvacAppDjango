from django import forms

from AdminUtils import get_standard_display_list
from Systems.models import SupplySystem, SystemData
from Terminals.models import EquipmentBase


class DeviceGeometryForm(forms.ModelForm):
	family_device_name = forms.ChoiceField(
		required=True,
		choices=[],
		widget=forms.Select,
	)

	def __init__(self, *args, **kwargs):
		super(DeviceGeometryForm, self).__init__(*args, **kwargs)
		self.fields['family_device_name'].choices = EquipmentBase. \
			objects.values_list('family_device_name', 'family_device_name').distinct()

	class Meta:
		model = SupplySystem
		fields = '__all__'


class SystemForm(DeviceGeometryForm):
	class Meta:
		model = SupplySystem
		fields = get_standard_display_list(SystemData, excluding_list=['space'])
