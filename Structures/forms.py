from django import forms
import calculation
from Structures.models.Structure import Structure


class StructureForm(forms.ModelForm):
    area = forms.DecimalField(
        widget=calculation.FormulaInput('width*length*quantity'), label='Площадь Конструкции',
        help_text='введите площадь, или расчитайте автоматически'  # <- using single math expression
    )

    class Meta:
        model = Structure
        fields = '__all__'
