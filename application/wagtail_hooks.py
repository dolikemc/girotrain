from django.utils.translation import ugettext as _
from django.contrib.admin.utils import (reverse)
from wagtail.contrib.modeladmin.views import IndexView
from wagtail.contrib.modeladmin.options import (ModelAdmin, modeladmin_register)
from application.models import Application


class MyApplicationListView(IndexView):
    def get_buttons_for_obj(self, obj):
        buttons = super().get_buttons_for_obj(obj)
        pk = getattr(obj, self.opts.pk.attname)
        buttons.append({
            'url': reverse('copy_application', kwargs={'app_id': pk}),
            'label': _('Move'),
            'classname': 'Edit',
            'title': _('Move this %s to user and child') % self.verbose_name, })
        return buttons


class ApplicationAdmin(ModelAdmin):
    model = Application
    menu_label = 'Applications'
    menu_icon = 'mail'
    menu_order = 300
    add_to_settings_menu = True
    exclude_from_explorer = False
    list_display = ('created_on', 'start_date', 'first_name', 'last_name', 'birth_date', 'contact_email')
    list_filter = ('created_on', 'start_date', 'child_link')
    search_fields = ('first_name', 'last_name', 'child_link')
    index_view_class = MyApplicationListView


modeladmin_register(ApplicationAdmin)
