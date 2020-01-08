from datetime import datetime, timedelta
from django.views.generic import CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpRequest, HttpResponseServerError, HttpResponseRedirect
from django.shortcuts import render_to_response
from application.models import Application


def copy_application_to_member(request: HttpRequest, app_id: int) -> HttpResponse:
    from child.models import Child
    from django.contrib.auth.models import User
    application = Application.objects.get(pk=app_id)
    if application is None:
        return HttpResponseServerError(b'id %d error, application does not exist anymore' % app_id)
    if application.child_link is not None:
        return HttpResponseServerError(
            b'id %d error, application already linked to a child. Remove child link first' % app_id)
    if application.birth_date is None:
        application.birth_date = datetime.today()  # have to be changed later
    try:
        father = None
        mother = None
        if application.first_name_father is not None and len(application.first_name_father) > 1:
            father = User.objects.create_user(
                username=application.last_name_father.lower() + application.first_name_father.lower()[0:2],
                email=application.email_father,
                password=application.birth_date.strftime('%Y%m%d'),
                first_name=application.first_name_father,
                last_name=application.last_name_father,
            )

        if application.first_name_mother is not None and len(application.first_name_mother) > 1:
            mother = User.objects.create_user(
                username=application.last_name_mother.lower() + application.first_name_mother.lower()[0:2],
                email=application.email_father,
                password=application.birth_date.strftime('%Y%m%d'),
                first_name=application.first_name_mother,
                last_name=application.last_name_mother)

        child = Child.objects.create(first_name=application.first_name, last_name=application.last_name,
                                     birth_date=application.birth_date, street=application.street,
                                     zip=application.zip, city=application.city, country=application.country,
                                     contact_email=application.contact_email, care_time=application.care_time,
                                     care_group='N', remark=application.remark, father=father, mother=mother)
        application.child_link = child
        application.save()

    except OSError as exc:
        HttpResponseServerError(b'id %d %s' % app_id % exc)

    return HttpResponseRedirect(redirect_to='/admin/')


class CreateApplication(CreateView):
    model = Application
    fields = ['contact_email', 'first_name', 'last_name', 'birth_date', 'gender', 'start_date', 'care_time',
              'street', 'zip', 'city', 'country', 'first_name_father', 'last_name_father', 'profession_father',
              'email_father', 'phone_father', 'nationality_father',
              'first_name_mother', 'last_name_mother', 'profession_mother', 'email_mother', 'phone_mother',
              'nationality_mother', 'remark', 'urgency']

    def form_valid(self, form):
        if isinstance(form.instance, Application) and isinstance(self.request, HttpRequest):
            try:
                form.instance.ip_address = self.request.META['HTTP_X_FORWARDED_FOR']
            except KeyError:
                pass
            # default validity is 6 months
            form.instance.expiry_extension = datetime.now() + timedelta(days=180)
        super().form_valid(form)
        return render_to_response(template_name='application/application_answer.html',
                                  context={'form': form.instance, 'request': self.request})


class DetailViewApplication(LoginRequiredMixin, DetailView):
    model = Application
    login_url = '/admin/login/'
