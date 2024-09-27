from django.db import models
class BaseModel(models.Model):
    creation_stamp = models.DateTimeField(auto_now_add=True, verbose_name="дата создания", null=True)
    update_stamp = models.DateTimeField(auto_now=True, verbose_name="дата изменения", null=True)

    class Meta:
        abstract = True
