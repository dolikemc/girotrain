from datetime import date, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import Form, DateField, CharField, Textarea, ModelChoiceField
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView
from django.http import HttpResponseRedirect, HttpRequest
from timetrack.models import WorkWeek, Contract


class UpdateWorkWeek(LoginRequiredMixin, UpdateView):
    model = WorkWeek
    fields = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'booked']
    login_url = '/admin/login/'
    success_url = reverse_lazy('list-time-tracking')

    def form_valid(self, form):
        form.instance.booked = True
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class TimeTracking(LoginRequiredMixin, ListView):
    model = WorkWeek
    paginate_by = 20
    fields = ['user_link', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'week']
    login_url = '/admin/login/'

    def get_queryset(self):
        return WorkWeek.objects.filter(week__gte=date.today() - timedelta(weeks=1),
                                       week__lte=date.today() + timedelta(weeks=15)).order_by('week', 'user_link', )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        return context


def create_time_tracking(request: HttpRequest, id: int):
    contract = Contract.objects.get(pk=id)
    if contract is None:
        raise ValueError('contract in the list does not exist')
    for to_delete in WorkWeek.objects.filter(week__gte=contract.to_date, user_link=contract.user_link):
        pass
    time_frame = contract.to_date - contract.from_date
    if time_frame.days < 0:
        raise ValueError('from date has to be before to date')
    for week in range(0, time_frame.days, 7):
        WorkWeek.objects.create(week=contract.from_date + timedelta(days=week),
                                user_link=contract.user_link,
                                updated_by=request.user,
                                monday=contract.hours_monday,
                                tuesday=contract.hours_tuesday,
                                wednesday=contract.hours_wednesday,
                                thursday=contract.hours_thursday,
                                friday=contract.hours_friday)
    return HttpResponseRedirect('/admin/')
