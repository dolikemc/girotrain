from datetime import date, datetime, timedelta
from django.db import models
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.utils.timezone import now
from wagtail.core.models import Page


# Create your models here.

class Contract(models.Model):
    user_link = models.ForeignKey(to=User, on_delete=models.CASCADE)
    from_date = models.DateField()
    to_date = models.DateField(null=TabError, blank=True)  # null means forever
    holidays_per_year = models.FloatField(default=30.0)
    hours_monday = models.FloatField(default=8.0)
    hours_tuesday = models.FloatField(default=8.0)
    hours_wednesday = models.FloatField(default=8.0)
    hours_thursday = models.FloatField(default=8.0)
    hours_friday = models.FloatField(default=8.0)
    deleted = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return self.user_link.first_name + ' ' + self.user_link.last_name + ': ' + str(self.from_date) + '-' + str(
            self.to_date)

    @classmethod
    def get_actual_contracts(cls, user: User = None) -> models.QuerySet:
        if user is None:
            return cls.objects.filter(deleted=False, to_date__gte=date.today())
        return cls.objects.filter(deleted=False, to_date__gte=date.today(), user_link=user)


WORK_DAY_VALUES = ('0', '0.5', '1', '1.5', '2', '2.5', '3', '3.5', '4', '4.5', '5', '5.5', '6', '6.5', '7', '7.5',
                   '8', '8.5', '9', '9.5', 'k', 'u', 'U')


class WorkWeek(models.Model):
    user_link = models.ForeignKey(to=User, on_delete=models.CASCADE)
    monday = models.FloatField(default=8.0)
    tuesday = models.FloatField(default=8.0)
    wednesday = models.FloatField(default=8.0)
    thursday = models.FloatField(default=8.0)
    friday = models.FloatField(default=8.0)
    week = models.DateField(default=now)
    booked = models.BooleanField(default=False)
    updated_by = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='updator')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class WorkWeekAdmin(Page):
    def serve(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('list-time-tracking'))
