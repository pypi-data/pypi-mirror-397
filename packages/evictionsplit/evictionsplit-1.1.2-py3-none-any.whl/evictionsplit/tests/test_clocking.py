from django.contrib.auth.models import User
from django.test import TestCase

from ..models import Clocking, Eviction


class ClockingTest(TestCase):
    def test_user_is_on_clocked(self):
        user1 = User.objects.create_user("user1", "", "")
        eviction = Eviction.create(
            name="Test eviction",
            creator=user1,
        )

        self.assertTrue(not eviction.is_user_on_standby(user1))
        self.assertTrue(not eviction.is_user_on_doorstop(user1))
        eviction.user_start_standby_for_ping(user1)
        eviction.user_start_doorstop(user1)
        self.assertTrue(eviction.is_user_on_standby(user1))
        self.assertTrue(eviction.is_user_on_doorstop(user1))

    def test_user_stop_clocked(self):
        user1 = User.objects.create_user("user1", "", "")
        eviction = Eviction.create(
            name="Test eviction",
            creator=user1,
        )

        eviction.user_start_standby_for_ping(user1)
        eviction.user_start_doorstop(user1)
        self.assertTrue(eviction.is_user_on_standby(user1))
        self.assertTrue(eviction.is_user_on_doorstop(user1))
        eviction.user_stop_standby_for_ping(user1)
        eviction.user_stop_doorstop(user1)

        self.assertTrue(not eviction.is_user_on_standby(user1))
        self.assertTrue(not eviction.is_user_on_doorstop(user1))

    def test_no_duplicate_clocking(self):
        user1 = User.objects.create_user("user1", "", "")
        eviction = Eviction.create(
            name="Test eviction",
            creator=user1,
        )

        self.assertEqual(0, Clocking.objects.count())

        eviction.user_start_doorstop(user1)
        eviction.user_start_standby_for_ping(user1)

        self.assertEqual(2, Clocking.objects.count())

        eviction.user_start_doorstop(user1)
        eviction.user_start_standby_for_ping(user1)

        self.assertEqual(2, Clocking.objects.count())

    def test_stop_clocking(self):
        user1 = User.objects.create_user("user1", "", "")
        eviction = Eviction.create(
            name="Test eviction",
            creator=user1,
        )

        clocking = Clocking(user=user1, eviction=eviction)
        clocking.save()

        self.assertEqual(None, clocking.end)

        clocking.stop()

        clocking = Clocking.objects.get(eviction=eviction)

        self.assertIsNot(None, clocking.end)
