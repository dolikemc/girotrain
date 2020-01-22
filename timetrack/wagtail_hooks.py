from django.utils.translation import ugettext as _
from django.contrib.admin.utils import reverse
from timetrack.models import Contract, WorkWeek
from wagtail.contrib.modeladmin.views import IndexView
from wagtail.contrib.modeladmin.options import (ModelAdmin, modeladmin_register)


class ContractListView(IndexView):
    def get_buttons_for_obj(self, obj):
        buttons = super().get_buttons_for_obj(obj)
        pk = getattr(obj, self.opts.pk.attname)
        buttons.append({
            'url': reverse('create-time-tracking-by-contract', kwargs={'id': pk}),
            'label': _('Create'),
            'classname': 'Edit',
            'title': _('Create time tracking entries for %s ') % self.verbose_name,
        }
        )
        return buttons


class ContractAdmin(ModelAdmin):
    model = Contract
    menu_label = 'Contract Admin'
    menu_icon = 'tick-inverse'
    menu_order = 400
    add_to_settings_menu = True
    exclude_from_explorer = False
    list_display = ('user_link', 'from_date', 'to_date', 'deleted')
    list_filter = ('deleted', 'user_link', 'from_date')
    search_fields = ('user_link', 'deleted', 'to_date')
    index_view_class = ContractListView


class WorkWeekAdmin(ModelAdmin):
    model = WorkWeek
    menu_label = 'Work Week Admin'
    menu_icon = 'time'
    menu_order = 700
    add_to_settings_menu = True
    exclude_from_explorer = False
    list_display = ('user_link', 'week', 'booked')
    list_filter = list_display
    search_fields = list_display


modeladmin_register(ContractAdmin)
modeladmin_register(WorkWeekAdmin)
