from django.db import models


class BuildingType(models.Model):
	"""Жилые, лечебно-профилактические и детские учреждения, школы, интернаты, гостиницы и общежития
		Общественные, кроме указанных выше, административные и бытовые, производственные и
		другие здания и помещения с влажным или мокрым режимами
		Производственные с сухим и нормальным режимами
	"""
	name = models.CharField(max_length=255)
	description = models.CharField(max_length=255)

	def __str__(self):
		return self.description

	class Meta:
		verbose_name = "Тип Здания"
		verbose_name_plural = "Типы Зданий"
		ordering = ['pk']


class StructureCoefficient(models.Model):
	"коэффициенты a,b для расчета нормируемых значений конструкций"
	name = models.CharField(max_length=10)

	class Meta:
		verbose_name = "Коэффициент конструкции"
		verbose_name_plural = "Коэффициенты конструкций"

	def __str__(self):
		return self.name


class BuildingProperty(models.Model):
	building_type = models.ForeignKey(BuildingType, on_delete=models.CASCADE)
	structure_coefficient = models.ForeignKey(StructureCoefficient, on_delete=models.CASCADE)
	wall = models.FloatField()
	roof = models.FloatField()
	floor = models.FloatField()
	window = models.FloatField(null=True, blank=True)
	skylight = models.FloatField()

	class Meta:
		verbose_name = "Свойства Здания"
		verbose_name_plural = "Свойства Зданий"
		ordering = ['pk']

	def __str__(self):
		return f"Properties for {self.building_type.name}"
