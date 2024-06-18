def duplicate_event(modeladmin, request, queryset):
	for object in queryset:
		object.id = None
		object.save()


duplicate_event.short_description = "копировать выбранное"


def get_standard_display_list(model, excluding_list: list[str] = None, additional_list: list[str] = None):
	additional_list = additional_list if additional_list else []
	excluding_list = excluding_list if excluding_list else []
	excluding_list = ["creation_stamp", 'update_stamp'] + excluding_list
	return [f.name for f in model._meta.fields if f.name not in excluding_list] + additional_list
