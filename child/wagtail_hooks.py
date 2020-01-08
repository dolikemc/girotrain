from wagtail.contrib.modeladmin.options import (ModelAdmin, modeladmin_register)
from child.models import Child, Absence


class ChildAdmin(ModelAdmin):
    model = Child
    menu_label = 'Giro Child'
    menu_icon = 'wagtail'
    menu_order = 300
    add_to_settings_menu = True
    exclude_from_explorer = False
    list_display = ('first_name', 'last_name', 'birth_date', 'contact_email', 'care_group')
    list_filter = ('care_group', 'birth_date')
    search_fields = ('first_name', 'last_name')


modeladmin_register(ChildAdmin)


class AbsenceAdmin(ModelAdmin):
    model = Absence
    menu_label = 'Absence Giro Child'
    menu_icon = 'date'
    menu_order = 400
    add_to_settings_menu = True
    exclude_from_explorer = False
    list_display = ('from_date', 'child_link', 'deleted', 'created_on')


modeladmin_register(AbsenceAdmin)
