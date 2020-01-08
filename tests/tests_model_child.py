from datetime import date, timedelta

from django.test import TestCase
from wagtail.admin.models import Page
from ls.joyous.models import SimpleEventPage, EventCategory, CalendarPage
from child.models import Child, Absence, User, GirotondoMonth


# Create your tests here.

class TestModelChild(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='un1', email='un1@test.de', password='un1')
        self.user2 = User.objects.create_user(username='un2', email='un2@test.de', password='un2')
        self.child = Child.objects.create(first_name='a', last_name='b',
                                          father=self.user, mother=self.user2, care_group='P')
        self.closed = EventCategory.objects.create(code='CL', name='closed')

    def tearDown(self) -> None:
        Child.objects.all().delete()
        User.objects.all().delete()

    def test_child(self) -> None:
        self.assertEquals('a', self.child.first_name)

    def test_child_by_parents_basic(self):
        self.assertEqual(1, len(Child.get_children_by_user(self.user)))
        for query_result in Child.get_children_by_user(self.user):
            self.assertEqual(self.child, query_result)

    def test_child_by_parent(self):
        user3 = User.objects.create_user(username='un3', email='un3@test.de', password='un3')
        Child.objects.create(first_name='a', last_name='b', father=user3)
        self.assertEqual(1, len(Child.get_children_by_user(self.user)))
        for query_result in Child.get_children_by_user(self.user):
            self.assertEqual(self.child, query_result)

    def test_absence(self):
        absence = Absence.objects.create(child_link=self.child, from_date=date.today() + timedelta(days=10),
                                         created_by=self.user)
        self.assertEqual(absence.child_link, self.child)

    def test_absence_basic(self):
        Absence.objects.create(child_link=self.child, from_date=date.today() + timedelta(days=10),
                               created_by=self.user)
        self.assertEqual(1, len(Absence.get_absence_queryset_by_user(self.user)))
        for absence in Absence.get_absence_queryset_by_user(self.user):
            self.assertEqual(absence.child_link, self.child)
        self.assertEqual(1, len(Absence.get_open_absence_queryset_by_user(self.user)))

    def test_absence_by_parent(self):
        Absence.objects.create(child_link=self.child, from_date=date.today() + timedelta(days=10),
                               created_by=self.user)
        self.assertEqual(1, len(Absence.get_absence_queryset_by_user(self.user2)))
        for absence in Absence.get_absence_queryset_by_user(self.user2):
            self.assertEqual(absence.child_link, self.child)
        self.assertEqual(1, len(Absence.get_open_absence_queryset_by_user(self.user2)))

    def test_absence_only_open(self):
        Absence.objects.create(child_link=self.child, from_date=date.today() - timedelta(days=10),
                               created_by=self.user)
        self.assertEqual(1, len(Absence.get_absence_queryset_by_user(self.user)))
        self.assertEqual(0, len(Absence.get_open_absence_queryset_by_user(self.user)))
        Absence.objects.create(child_link=self.child, from_date=date.today() + timedelta(days=10),
                               created_by=self.user, deleted=True)
        self.assertEqual(0, len(Absence.get_open_absence_queryset_by_user(self.user)))
        self.assertEqual(1, len(Absence.get_absence_queryset_by_user(self.user)))

    def test_absence_ordering(self):
        Absence.objects.create(child_link=self.child, from_date=date.today() + timedelta(days=10),
                               created_by=self.user)
        Absence.objects.create(child_link=self.child, from_date=date.today(),
                               created_by=self.user)
        index = 0
        for absence in Absence.get_open_absence_queryset_by_user(self.user):
            index += 1
            if index == 1:
                self.assertEqual(absence.from_date, date.today())
            if index == 2:
                self.assertNotEqual(absence.from_date, date.today())
            if index > 2:
                self.assertFalse(1 == 1, 'more than expected absences in')

    def test_get_holiday(self):
        Absence.objects.create(child_link=self.child, from_date=date.today() + timedelta(days=2),
                               created_by=self.user)
        Absence.objects.create(child_link=self.child, from_date=date.today() + timedelta(days=3),
                               created_by=self.user)
        Absence.objects.create(child_link=self.child, from_date=date.today() + timedelta(days=1),
                               created_by=self.user)
        Absence.objects.create(child_link=self.child, from_date=date.today(),
                               created_by=self.user)
        Absence.objects.create(child_link=self.child, from_date=date.today() + timedelta(days=4),
                               created_by=self.user)
        Absence.objects.create(child_link=self.child, from_date=date.today() + timedelta(days=5),
                               created_by=self.user)

        holidays = Absence.get_holidays(self.user)
        self.assertEqual(1, len(holidays))
        self.assertEqual(holidays[0]['from_date'], date.today())
        self.assertEqual(holidays[0]['to_date'], date.today() + timedelta(days=5))

    def test_assigments(self):
        Child.objects.create(first_name='a', last_name='b', father=self.user, care_group='M')
        Absence.objects.create(child_link=self.child, from_date=date(2019, 12, 17), created_by=self.user)
        Absence.objects.create(child_link=self.child, from_date=date(2019, 12, 18), created_by=self.user)

        assignments = Child.get_assignments_by_month(12, 2019)
        self.assertDictEqual(assignments[17 - 1], {'day': 17, 'M': [], 'G': [], 'P': [self.child]})
        self.assertDictEqual(assignments[18 - 1], {'day': 18, 'M': [], 'G': [], 'P': [self.child]})
        self.assertDictEqual(assignments[19 - 1], {'day': 19, 'M': [], 'G': [], 'P': []})

        groups = Child.get_children_per_care_group()
        self.assertEqual(1, len(groups['P']))
        self.assertEqual(1, len(groups['M']))
        self.assertEqual(0, len(groups['G']))

    def test_girotondo_month(self):
        child2 = Child.objects.create(first_name='ab', last_name='bc',
                                      father=self.user, care_group='P')
        Absence.objects.create(child_link=self.child, from_date=date(2019, 12, 17), created_by=self.user)
        Absence.objects.create(child_link=self.child, from_date=date(2019, 12, 18), created_by=self.user)
        self.home = self.home = Page.objects.get(slug='home')

        self.calendar = CalendarPage(owner=self.user,
                                     slug="events",
                                     title="Events")
        self.home.add_child(instance=self.calendar)
        self.calendar.save_revision().publish()
        self.event = SimpleEventPage(owner=self.user,
                                     slug="pet-show",
                                     title="Pet Show",
                                     category=self.closed,
                                     date=date(2019, 12, 23))
        self.calendar.add_child(instance=self.event)
        self.event.save_revision().publish()

        giro_month = GirotondoMonth(2019, 12)
        giro_month.holidays.add(date(2019, 12, 24), 'Xmas')
        self.assertFalse(giro_month.is_girotondo_day(23))
        self.assertFalse(giro_month.is_girotondo_day(24))
        self.assertFalse(giro_month.is_girotondo_day(22))
        self.assertFalse(giro_month.is_girotondo_day(21))
        self.assertTrue(giro_month.is_girotondo_day(20))

        self.assertEqual(giro_month.get_children_out(17, 'P'), [self.child.first_name + ' ' + self.child.last_name])
        self.assertEqual(giro_month.get_children_in(17, 'P'), [child2.first_name + ' ' + child2.last_name])
        self.assertEqual(giro_month.get_children_out(12, 'P'), [])
