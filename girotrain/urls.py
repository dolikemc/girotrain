from django.conf import settings
from django.urls import path
from django.conf.urls import include
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views

from application.views import CreateApplication, DetailViewApplication, copy_application_to_member
from child.views import CreateAbsence, ListAbsences, CreateHoliday, delete_holiday, AssignmentPlan
from timetrack.views import TimeTracking, create_time_tracking, UpdateWorkWeek

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('admin/application/application/move/<int:app_id>/', copy_application_to_member, name='copy_application'),
    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path('timetracking/', TimeTracking.as_view(), name='list-time-tracking'),
    path('timetracking/contract/<int:id>/', create_time_tracking, name='create-time-tracking-by-contract'),
    path('timetracking/update/<int:pk>/', UpdateWorkWeek.as_view(), name='update-time-tracking'),
    path('assignment/plan/<int:year>/<int:month>/', AssignmentPlan.as_view(), name='assignment-plan'),
    path('i18n/', include('django_translation_flags.urls')),
]

urlpatterns += i18n_patterns(
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path('application/<int:pk>/', DetailViewApplication.as_view(), name='view-application'),
    path('application/create/', CreateApplication.as_view(), name='new-application'),
    path('absence/create/', CreateAbsence.as_view(), name='new-absence'),
    path('absence/', ListAbsences.as_view(), name='list-absences'),
    path('holiday/create/', CreateHoliday.as_view(), name='new-holiday'),
    path('holiday/delete/<int:year>/<int:month>/<int:day>/<int:to_year>/<int:to_month>/<int:to_day>/',
         delete_holiday, name='delete-holiday'),
    path('', include(wagtail_urls)),
    path('search/', search_views.search, name='search'),

)

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
