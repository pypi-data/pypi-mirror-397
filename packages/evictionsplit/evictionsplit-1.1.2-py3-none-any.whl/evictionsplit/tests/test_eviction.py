from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from ..models import Clocking, Eviction


class EvictionTest(TestCase):
    def test_create_eviction(self):
        user1 = User.objects.create_user("user1", "", "")
        Eviction.create(
            name="Test eviction",
            creator=user1,
        )

        self.assertTrue(True)

    def test_user_part_eviction(self):
        user1 = User.objects.create_user("user1", "", "")
        user2 = User.objects.create_user("user2", "", "")
        eviction = Eviction.create(
            name="Test eviction",
            creator=user1,
        )

        self.assertTrue(eviction.is_user_participating(user1))
        self.assertTrue(not eviction.is_user_participating(user2))

        eviction.participants.add(user2)

        self.assertTrue(eviction.is_user_participating(user2))

    def test_eviction_has_applicants(self):
        user1 = User.objects.create_user("user1", "", "")
        user2 = User.objects.create_user("user2", "", "")
        eviction = Eviction.create(
            name="Test eviction",
            creator=user1,
        )

        self.assertFalse(eviction.has_applicants())

        eviction.user_apply(user2)

        self.assertTrue(eviction.has_applicants())

        eviction.validate_apply(user2)

        self.assertFalse(eviction.has_applicants())

    def test_eviction_application(self):
        user1 = User.objects.create_user("user1", "", "")
        user2 = User.objects.create_user("user2", "", "")
        eviction = Eviction.create(
            name="Test eviction",
            creator=user1,
        )

        eviction.user_apply(user2)

        self.assertTrue(eviction.applicants.filter(id=user2.id).exists())
        self.assertEqual(eviction.get_applicants(), [user2])

        eviction.validate_apply(user2)

        self.assertTrue(len(eviction.applicants.all()) == 0)
        self.assertTrue(eviction.participants.filter(id=user2.id).exists())
        self.assertEqual(eviction.get_applicants(), [])

    def test_eviction_clocking_time(self):
        user1 = User.objects.create_user("user1", "", "")
        eviction = Eviction.create(
            name="Test eviction",
            creator=user1,
        )

        clock_1 = Clocking(
            user=user1,
            eviction=eviction,
            type=Clocking.DOORSTOP,
            beginning=timezone.datetime(2023, 1, 1, 12, 0, 0, 0),
            end=timezone.datetime(2023, 1, 1, 12, 10, 0, 0),
        )
        clock_1.save()

        self.assertEqual(
            timezone.timedelta(minutes=10), eviction.user_doorstop_time(user1)
        )

        clock_2 = Clocking(
            user=user1,
            eviction=eviction,
            type=Clocking.DOORSTOP,
            beginning=timezone.datetime(2023, 1, 1, 13, 0, 0, 0),
            end=timezone.datetime(2023, 1, 1, 13, 20, 0, 0),
        )
        clock_2.save()

        self.assertEqual(
            timezone.timedelta(minutes=30), eviction.user_doorstop_time(user1)
        )

        clock_3 = Clocking(
            user=user1,
            eviction=eviction,
            type=Clocking.STANDBY_FOR_PINGS,
            beginning=timezone.datetime(2023, 1, 1, 12, 0, 0, 0),
            end=timezone.datetime(2023, 1, 1, 12, 10, 0, 0),
        )
        clock_3.save()

        self.assertEqual(
            timezone.timedelta(minutes=30), eviction.user_doorstop_time(user1)
        )
        self.assertEqual(
            timezone.timedelta(minutes=10), eviction.user_standby_time(user1)
        )

    def test_eviction_stop(self):
        user1 = User.objects.create_user("user1", "", "")
        eviction = Eviction.create(
            name="Test eviction",
            creator=user1,
        )

        clock_1 = Clocking(
            user=user1,
            eviction=eviction,
            type=Clocking.DOORSTOP,
            beginning=timezone.datetime(2023, 1, 1, 12, 0, 0, 0),
        )
        clock_1.save()

        clock_2 = Clocking(
            user=user1,
            eviction=eviction,
            type=Clocking.STANDBY_FOR_PINGS,
            beginning=timezone.datetime(2023, 1, 1, 12, 0, 0, 0),
        )
        clock_2.save()

        clock_3 = Clocking(
            user=user1,
            eviction=eviction,
            type=Clocking.STANDBY_FOR_PINGS,
            beginning=timezone.datetime(2023, 1, 1, 11, 0, 0, 0),
            end=timezone.datetime(2023, 1, 1, 11, 10, 0, 0),
        )
        clock_3.save()

        self.assertTrue(eviction.active)
        self.assertIsNone(clock_1.end)
        self.assertIsNone(clock_2.end)

        eviction.stop()

        self.assertFalse(eviction.active)
        self.assertIsNotNone(Clocking.objects.get(id=clock_1.id).end)
        self.assertIsNotNone(Clocking.objects.get(id=clock_2.id).end)
        self.assertIsNotNone(Clocking.objects.get(id=clock_3.id).end)

    def test_cant_clock_inactive(self):
        user1 = User.objects.create_user("user1", "", "")
        eviction = Eviction.create(
            name="Test eviction",
            creator=user1,
        )
        eviction.stop()

        with self.assertRaises(Eviction.EvictionInactive):
            eviction.user_start_doorstop(user1)

        with self.assertRaises(Eviction.EvictionInactive):
            eviction.user_start_standby_for_ping(user1)

    def test_eviction_export_activity(self):
        user1 = User.objects.create_user("user1", "", "")
        eviction = Eviction.create(
            name="Test eviction",
            creator=user1,
        )

        clock_1 = Clocking(
            user=user1,
            eviction=eviction,
            type=Clocking.DOORSTOP,
            beginning=timezone.datetime(2023, 1, 1, 12, 0, 0, 0),
            end=timezone.datetime(2023, 1, 1, 15, 20, 30, 0),
        )
        clock_1.save()

        clock_2 = Clocking(
            user=user1,
            eviction=eviction,
            type=Clocking.STANDBY_FOR_PINGS,
            beginning=timezone.datetime(2023, 1, 1, 12, 0, 0, 0),
            end=timezone.datetime(2023, 1, 2, 13, 30, 20),
        )
        clock_2.save()

        clock_3 = Clocking(
            user=user1,
            eviction=eviction,
            type=Clocking.STANDBY_FOR_PINGS,
            beginning=timezone.datetime(2023, 1, 1, 11, 0, 0, 0),
            end=timezone.datetime(2023, 1, 1, 11, 10, 0, 0),
        )
        clock_3.save()
        eviction.stop()

        activity_export = eviction.spreadsheet_export()
        expected = """PILOT\tSTANDBY\tDOORSTOP
user1\t25:40:20\t03:20:30\n"""

        self.assertEqual(expected, activity_export)

        user2 = User.objects.create_user("user2", "", "")
        eviction.participants.add(user2)

        clock_4 = Clocking(
            user=user2,
            eviction=eviction,
            type=Clocking.STANDBY_FOR_PINGS,
            beginning=timezone.datetime(2023, 1, 1, 12, 0, 0, 0),
            end=timezone.datetime(2023, 1, 1, 13, 10, 0, 0),
        )
        clock_4.save()

        clock_5 = Clocking(
            user=user2,
            eviction=eviction,
            type=Clocking.DOORSTOP,
            beginning=timezone.datetime(2023, 1, 1, 12, 20, 0, 0),
            end=timezone.datetime(2023, 1, 1, 12, 30, 0, 0),
        )
        clock_5.save()

        activity_export = eviction.spreadsheet_export()
        expected = """PILOT\tSTANDBY\tDOORSTOP
user1\t25:40:20\t03:20:30
user2\t01:10:00\t00:10:00\n"""

        self.assertEqual(expected, activity_export)
