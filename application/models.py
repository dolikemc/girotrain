from datetime import date

from django.db import models
from django.shortcuts import reverse
from django.http import HttpResponseRedirect
from wagtail.core.models import Page
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, FieldRowPanel

from child.models import Child


class Application(models.Model):
    ip_address = models.GenericIPAddressField(editable=False, default='0.0.0.0')
    first_name = models.CharField(max_length=128, default='not known yet')
    last_name = models.CharField(max_length=128)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=[('M', 'male'), ('F', 'female'), ('X', 'not yet known')],
                              default='X')
    start_date = models.DateField()
    care_time = models.CharField(max_length=1, choices=[('F', 'full time'), ('M', 'morning'), ('A', 'afternoon')],
                                 default='F')
    contact_email = models.EmailField()
    street = models.CharField(max_length=128)
    zip = models.CharField(max_length=16)
    city = models.CharField(max_length=32)
    country = models.CharField(max_length=2, default='DE')
    first_name_father = models.CharField(max_length=128, blank=True, null=True)
    last_name_father = models.CharField(max_length=128, blank=True, null=True)
    profession_father = models.CharField(max_length=128, blank=True, null=True)
    email_father = models.EmailField(null=True, blank=True)
    phone_father = models.CharField(max_length=32, blank=True, null=True)
    nationality_father = models.CharField(max_length=2, default='DE')
    first_name_mother = models.CharField(max_length=128, blank=True, null=True)
    last_name_mother = models.CharField(max_length=128, blank=True, null=True)
    profession_mother = models.CharField(max_length=128, blank=True, null=True)
    email_mother = models.EmailField(null=True, blank=True)
    phone_mother = models.CharField(max_length=32, blank=True, null=True)
    nationality_mother = models.CharField(max_length=2, default='DE')
    remark = models.TextField(max_length=1024, default='.')
    urgency = models.CharField(max_length=1, choices=[
        ('A', 'Kinder aus Familien, die gemäß §27 i.V.m.§36 SGB VIII der „Hilfe zur Erziehung“ bedürfen'),
        ('B', """Kinder, deren Mutter oder Vater alleinerziehend und berufstätig oder in Ausbildung ist, sowie Kinder 
                 deren beide Elternteile berufstätig oder in Ausbildung sind, soweit Umfang und Lage der Arbeitszeit 
                 bzw. Unterrichtszeit die Betreuung erforderlich machen"""),
        ('C', 'Soziale Härtefälle')],
                               default='A')
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    expiry_extension = models.DateField(null=True, blank=True)  # type: date
    expiry_comment = models.CharField(max_length=128, default='inital 6 months')
    child_link = models.ForeignKey(to=Child, on_delete=models.DO_NOTHING, null=True, blank=True)

    panels = [
        MultiFieldPanel(heading='Child', children=[
            FieldRowPanel([FieldPanel('first_name'), FieldPanel('last_name'), FieldPanel('contact_email')]),
            FieldRowPanel([FieldPanel('birth_date'), FieldPanel('gender')]),
            FieldRowPanel([FieldPanel('start_date'), FieldPanel('care_time')]),
            FieldRowPanel([FieldPanel('street'), FieldPanel('zip'), FieldPanel('city')]), ]),
        MultiFieldPanel(heading='Mother', children=[
            FieldRowPanel([FieldPanel('first_name_mother'),
                           FieldPanel('last_name_mother'),
                           FieldPanel('nationality_mother')], ),
            FieldRowPanel(
                [FieldPanel('phone_mother'), FieldPanel('email_mother')], ),
            FieldRowPanel([FieldPanel('profession_mother')], ),
        ]),
        MultiFieldPanel(heading='Father', children=[
            FieldRowPanel([FieldPanel('first_name_father'),
                           FieldPanel('last_name_father'),
                           FieldPanel('nationality_father')], ),
            FieldRowPanel(
                [FieldPanel('phone_father'), FieldPanel('email_father')], ),
            FieldRowPanel([FieldPanel('profession_father')], ),
        ]),
        MultiFieldPanel(heading='Remarks', children=[
            FieldPanel('remark'),
            FieldPanel('urgency'),
            FieldRowPanel([FieldPanel('expiry_extension'), FieldPanel('expiry_comment'), ]),
            FieldPanel('child_link'),
        ], )
    ]

    def __str__(self) -> str:
        return self.first_name + ' ' + self.last_name + ': ' + str(self.birth_date)

    def get_absolute_url(self):
        return reverse('view-application', kwargs={'pk': self.pk})


class ApplicationSendPage(Page):
    def serve(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('new-application'))
