import calendar
from datetime import date, timedelta
from typing import Dict, List
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from wagtail.admin.models import Page
from ls.joyous.models import CalendarPage, RecurringEventPage, MultidayEventPage, MultidayRecurringEventPage, \
    SimpleEventPage
from ls.joyous.holidays import Holidays

CalendarPage.is_creatable = False


class Child(models.Model):
    first_name = models.CharField(max_length=128, default='not known yet')
    last_name = models.CharField(max_length=128)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=[('M', 'male'), ('F', 'female'), ('X', 'not yet known')],
                              default='X')
    care_time = models.CharField(max_length=1, choices=[('F', 'full time'), ('M', 'morning'), ('A', 'afternoon')],
                                 default='F')
    care_group = models.CharField(max_length=1, choices=[('P', 'piccoli'), ('M', 'medi'), ('G', 'grandi'),
                                                         ('N', 'none')],
                                  default='P')
    contact_email = models.EmailField()
    street = models.CharField(max_length=128)
    zip = models.CharField(max_length=16)
    city = models.CharField(max_length=32)
    country = models.CharField(max_length=2, default='DE')
    mother = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, related_name='mother')
    father = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, related_name='father')
    remark = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.first_name + ' ' + self.last_name + ' (' + self.care_group + ')'

    @classmethod
    def get_children_by_user(cls, user: User) -> models.QuerySet:
        return cls.objects.filter(models.Q(father=user) | models.Q(mother=user)).order_by(
            'birth_date')

    @staticmethod
    def __get_default_month_and_year(month: int = None, year: int = None):
        if month is None:
            month = date.today().month
        if year is None:
            year = date.today().year
            if month == 12:
                year = year + 1
        return month, year

    @classmethod
    def get_assignments_by_month(cls, month: int = None, year: int = None) -> List[Dict]:
        month, year = cls.__get_default_month_and_year(month, year)
        assignments = []
        cal = calendar.Calendar()
        for day in cal.itermonthdates(year, month):
            if day.month == month:
                assignments.append({'day': day.day, 'G': [], 'M': [], 'P': []})
        for child in cls.objects.filter(care_group__in=('P', 'M', 'G')):
            for absence in Absence.objects.filter(child_link=child, deleted=False, from_date__month=month,
                                                  from_date__year=year):
                assignments[absence.from_date.day - 1][child.care_group].append(child)
        return assignments

    @classmethod
    def get_children_per_care_group(cls) -> Dict:
        group = {'P': [], 'M': [], 'G': []}
        for child in cls.objects.filter(care_group__in=('P', 'M', 'G')):
            group[child.care_group].append(child)
        return group


class Absence(models.Model):
    child_link = models.ForeignKey(to=Child, on_delete=models.CASCADE)
    from_date = models.DateField()
    remark = models.CharField(default='Urlaub', max_length=32)
    created_by = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='creator')
    deleted_by = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, blank=True,
                                   related_name='deletor')
    deleted = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    deleted_on = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return str(self.child_link) + ' ' + str(self.from_date)

    @classmethod
    def get_absence_queryset_by_user(cls, user: User) -> models.QuerySet:
        return cls.objects.filter(models.Q(child_link__father=user) | models.Q(child_link__mother=user),
                                  deleted=False).order_by('from_date')

    @classmethod
    def get_open_absence_queryset_by_user(cls, user: User) -> models.QuerySet:
        return cls.objects.filter(models.Q(child_link__father=user) | models.Q(child_link__mother=user), deleted=False,
                                  from_date__gte=date.today()).order_by('from_date')

    @classmethod
    def get_holidays(cls, user: User) -> List[Dict]:
        holidays = []
        holiday = {'from_date': None, 'to_date': None, 'remark': ''}
        for absence in Absence.get_open_absence_queryset_by_user(user):
            if holiday['from_date'] is None:
                holiday['from_date'] = absence.from_date
                holiday['to_date'] = absence.from_date
                holiday['remark'] = absence.remark
                holiday['child'] = absence.child_link.first_name

            if absence.from_date - holiday['to_date'] <= timedelta(days=1):
                holiday['to_date'] = absence.from_date
            else:
                holidays.append(holiday.copy())
                holiday['from_date'] = None
        if holiday['from_date'] is not None:
            holidays.append(holiday)
        return holidays


class AbsenceSendPage(Page):

    def serve(self, request, *args, **kwargs):
        return HttpResponseRedirect(redirect_to=reverse('list-absences'))


class HolidaySendPage(Page):

    def serve(self, request, *args, **kwargs):
        return HttpResponseRedirect(redirect_to=reverse('new-holiday'))


class GirotondoCalendar(LoginRequiredMixin, CalendarPage):
    class Meta:
        verbose_name = "Girotondo Calendar"

    show_in_menus_default = True

    def get_context(self, request, *args, **kwargs):
        self.holidays = Holidays()
        for absence in Absence.get_absence_queryset_by_user(request.user):
            if absence.deleted:
                continue
            self.holidays.add(absence.from_date, absence.child_link.first_name + ' ' + absence.remark)
        ctx = super().get_context(request, *args, **kwargs)
        return ctx

    subpage_types = [RecurringEventPage, MultidayRecurringEventPage, MultidayEventPage, SimpleEventPage]


RecurringEventPage.parent_page_types = [GirotondoCalendar]
MultidayEventPage.parent_page_types = [GirotondoCalendar]
MultidayRecurringEventPage.parent_page_types = [GirotondoCalendar]
SimpleEventPage.parent_page_types = [GirotondoCalendar]


class GirotondoMonth:
    def __init__(self, year: int = None, month: int = None):
        if month is None:
            month = date.today().month
        self.month = month
        if year is None:
            year = date.today().year
        self.year = year
        self.next_month = self.month + 1
        self.next_month_year = self.year
        if self.next_month > 12:
            self.next_month_year = self.year + 1
            self.next_month = 1
        self.event_queryset = SimpleEventPage.objects.filter(
            date__gte=date(self.year, self.month, 1),
            date__lt=date(self.next_month_year, self.next_month, 1))

        # .union(MultidayEventPage.objects.filter(
        #    date_to__gte=date(self.year, self.month, 1),
        #    date_from__lt=date(self.next_month_year, self.next_month, 1))).order_by('owner_id')
        self.absences = Child.get_assignments_by_month(self.month, self.year)
        self.children = Child.get_children_per_care_group()
        self.holidays = Holidays()

    def is_girotondo_day(self, day: int) -> bool:
        test_date = date(self.year, self.month, day)
        if test_date.weekday() > 4:  # 5 = saturday, 6 = sunday
            return False
        if len(self.holidays.get(test_date)) > 0:
            return False
        for event in self.event_queryset:
            if event.date != test_date:
                continue
            if event.category is not None and event.category.name in ('closed', 'Closed'):
                return False
        return True

    def get_children_in(self, day: int, group: str) -> List[str]:
        children_in = []
        if not self.is_girotondo_day(day):
            return []
        for child in self.children[group]:
            if child not in self.absences[day - 1][group]:
                children_in.append(child.first_name + ' ' + child.last_name)
        return children_in

    def get_children_out(self, day: int, group: str) -> List[str]:
        return [x.first_name + ' ' + x.last_name for x in self.absences[day - 1][group]]
