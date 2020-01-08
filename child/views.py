from datetime import date, timedelta
import calendar

from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import Form, DateField, CharField, Textarea, ModelChoiceField
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, FormView, TemplateView
from django.http import HttpResponseRedirect
from child.models import Absence, Child, GirotondoMonth
from timetrack.models import Contract


# Create your views here.
class CreateAbsence(LoginRequiredMixin, CreateView):
    model = Absence
    fields = ['child_link', 'from_date', 'remark']
    success_url = reverse_lazy('list-absences')
    login_url = '/admin/login/'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ListAbsences(LoginRequiredMixin, ListView):
    model = Absence
    paginate_by = 20
    fields = ['child_link', 'from_date', 'remark', 'created_on']
    login_url = '/admin/login/'

    def get_queryset(self):
        return Absence.get_open_absence_queryset_by_user(self.request.user)

    def get_context_data(self, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['today'] = date.today()
        context['holidays'] = Absence.get_holidays(self.request.user)
        return context


class HolidayForm(Form):
    from_date = DateField()
    to_date = DateField()
    remark = CharField(max_length=256, widget=Textarea)
    children = ModelChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['children'].queryset = Child.get_children_by_user(user=user)


class CreateHoliday(LoginRequiredMixin, FormView):
    template_name = 'holiday/holiday_form.html'
    success_url = reverse_lazy('list-absences')
    form_class = HolidayForm
    login_url = '/admin/login/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        delta = form.cleaned_data['to_date'] - form.cleaned_data['from_date']
        absences = Absence.get_open_absence_queryset_by_user(self.request.user)
        for day_delta in range(0, delta.days + 1):
            the_day = form.cleaned_data['from_date'] + timedelta(days=day_delta)
            if the_day not in [x.from_date for x in absences]:
                Absence.objects.create(from_date=the_day, created_by=self.request.user,
                                       child_link=form.cleaned_data['children'],
                                       remark=form.cleaned_data['remark'])

        return super().form_valid(form)


def delete_holiday(request, year, month, day, to_year, to_month, to_day):
    if hasattr(request, 'user') and request.user.is_authenticated:
        for absence in Absence.get_open_absence_queryset_by_user(request.user):
            if date(year, month, day) <= absence.from_date <= date(to_year, to_month, to_day):
                absence.deleted_by = request.user
                absence.deleted = True
                absence.save()
    return HttpResponseRedirect(reverse_lazy('list-absences'))


class AssignmentPlan(LoginRequiredMixin, TemplateView):
    template_name = 'assignment/assignment_plan.html'
    login_url = '/admin/login/'

    def get_context_data(self, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        giro_month = GirotondoMonth(
            year=kwargs.pop('year', date.today().year),
            month=kwargs.pop('month', date.today().month)
        )
        context['object_list'] = []
        for day in calendar.Calendar().itermonthdates(giro_month.year, giro_month.month):
            if day.month != giro_month.month:
                continue
            context['object_list'].append({'date': day, 'open': giro_month.is_girotondo_day(day.day),
                                          'Pi': str(giro_month.get_children_in(day.day, 'P')),
                                          'Po': str(giro_month.get_children_out(day.day, 'P')),
                                          'Mi': str(giro_month.get_children_in(day.day, 'M')),
                                          'Mo': str(giro_month.get_children_out(day.day, 'M')),
                                          'Gi': str(giro_month.get_children_in(day.day, 'G')),
                                          'Go': str(giro_month.get_children_out(day.day, 'G')),
                                          })

        context['contracts'] = Contract.objects.filter(from_date__lte=date(giro_month.year, giro_month.month, 1),
                                                       to_date__gt=date(giro_month.next_month_year,
                                                                        giro_month.next_month, 1))
        print(context)
        return context
