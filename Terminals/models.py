from django.db import models

from HvacAppDjango.models import BaseModel
from StaticDB.StaticData.SystemChoices import Orientation, CenterOrientation
from StaticDB.StaticData.SystemChoices import SystemType


class EquipmentBase(BaseModel):
    system_equipment_type = models.CharField(max_length=200, choices=SystemType.choices(),
                                             default=SystemType.choices()[0])
    equipment_id = models.CharField(max_length=200, unique=True)
    family_device_name = models.CharField(max_length=200)
    family_instance_name = models.CharField(max_length=200)
    max_flow = models.FloatField()
    normal_velocity = models.FloatField(default=2, null=True, blank=True)
    geometry = models.CharField(max_length=200, null=True, blank=True, default='c')
    dimension1 = models.CharField(max_length=200, null=True, blank=True)
    manufacture = models.CharField(max_length=200, null=True, blank=True)
    system_flow_parameter_name = models.CharField(max_length=200, null=True, blank=True)
    system_name_parameter = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.family_device_name}"

    class Meta:
        verbose_name = 'Терминал'
        verbose_name_plural = 'Терминалы'


class DeviceGeometry(models.Model):
    device_orientation_option1 = models.CharField(max_length=20, choices=Orientation.choices(),
                                                  default=Orientation.choices()[0])
    device_orientation_option2 = models.CharField(max_length=20, choices=Orientation.choices(),
                                                  default=Orientation.choices()[0])
    single_device_orientation = models.CharField(max_length=20, choices=CenterOrientation.choices(),
                                                 default=CenterOrientation.choices()[0])
    wall_offset = models.FloatField(default=500)
    ceiling_offset = models.FloatField(default=500)

    class Meta:
        verbose_name = 'Терминал Геометрия'
        verbose_name_plural = 'Терминалы Геометрия'

    def __str__(self):
        try:
            res = f"{getattr(Orientation, self.device_orientation_option1).value}" \
                  f"-{getattr(Orientation, self.device_orientation_option2).value}" \
                  f"-{getattr(Orientation, self.single_device_orientation).value}"
            return res
        except Exception as e:
            res = f"{self.device_orientation_option1}" \
                  f"-{self.device_orientation_option2}"
            print(e)
            return res
