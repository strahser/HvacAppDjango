from django.contrib import admin


class SpaceDataRepresentation:
    short_names = ['id', 'Space_ID', 'Space_name', 'Space_number']
    space = None

    @admin.display(description='id пом.', ordering="space__S_ID")
    def Space_ID(self):
        return self.space.pk

    @admin.display(description='наим. пом.', ordering="space__S_Name")
    def Space_name(self):
        return self.space.S_Name

    @admin.display(description='Ном. пом.', ordering="space__S_Number")
    def Space_number(self):
        return self.space.S_Number
