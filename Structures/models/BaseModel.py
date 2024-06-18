from django.db import models


class BaseModel(models.Model):
	name = models.CharField(max_length=250, verbose_name="наименование")
	creation_stamp = models.DateTimeField(auto_now_add=True, verbose_name="дата создания")
	update_stamp = models.DateTimeField(auto_now=True, verbose_name="дата изменения")

	class Meta:
		abstract = True

	def __str__(self):
		return f"{self.name}"
