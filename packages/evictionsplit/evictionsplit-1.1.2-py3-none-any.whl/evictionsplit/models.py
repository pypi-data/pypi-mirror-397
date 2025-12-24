"""Models."""

import datetime
from typing import List

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from allianceauth.authentication.models import User, UserProfile


class General(models.Model):
    """Meta model for evictionsplit permissions"""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ("basic_access", "Can access this app"),
            ("manager", "Can create and manage evictions"),
        )


def format_delta_for_export(delta: datetime.timedelta) -> str:
    """
    Returns a timedelta formatted as follows: HOUR:MINUTES:SECONDS
    Will not display the number of days and will add 24 hours instead
    """

    remaining_value = delta.seconds
    seconds = remaining_value % 60
    remaining_value = remaining_value // 60
    minutes = remaining_value % 60
    hours = (remaining_value // 60) + delta.days * 24

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class Eviction(models.Model):
    """Model for an eviction people can subscribe to"""

    name = models.CharField(max_length=120)
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="evictions_created",
        related_query_name="eviction_created",
    )
    participants = models.ManyToManyField(
        User,
        related_name="evictions_participating",
        related_query_name="eviction_participating",
        blank=True,
    )
    applicants = models.ManyToManyField(
        User, related_name="evictions_applied", related_query_name="eviction_applied"
    )
    active = models.BooleanField(default=True)
    auto_join = models.BooleanField(
        default=False,
        help_text=_("Applying members will automatically be added to the eviction"),
    )

    class EvictionInactive(Exception):
        """Signals that the eviction is now inactive"""

    @classmethod
    def create(cls, name: str, creator: User) -> "Eviction":
        """Creates and eviction in the databaser and returns it"""
        e = Eviction.objects.create(name=name, creator=creator)
        e.participants.add(creator)
        e.save()
        return e

    def __str__(self):
        return self.name

    def __repr__(self):
        profile: UserProfile = self.creator.profile  # pylint: disable=no-member
        return f"{self.name} by {profile.main_character.character_name}"

    def is_user_participating(self, user: User) -> bool:
        """True if the user is an eviction participant"""
        return self.participants.filter(id=user.id).exists()

    def user_apply(self, user: User):
        """Adds a user to the list of applicants if they are not already part of the eviction"""
        if not (
            self.participants.filter(id=user.id).exists()
            or self.applicants.filter(id=user.id).exists()
        ):
            self.applicants.add(user)

    def validate_apply(self, user: User):
        """Remove a user from the applicants and add them as a participant"""
        self.applicants.remove(user)
        self.participants.add(user)

    def has_applicants(self) -> bool:
        """True if the eviction has users with applications waiting"""
        return self.applicants.all().exists()

    def get_applicants(self) -> List[User]:
        """List of users with applications waiting"""
        return list(self.applicants.all())

    def is_user_on_standby(self, user: User) -> bool:
        """True if the user is currently on standby for ping"""
        return self.__is_user_clocked(user, Clocking.STANDBY_FOR_PINGS)

    def is_user_on_doorstop(self, user: User) -> bool:
        """True if the user is currently on doorstop"""
        return self.__is_user_clocked(user, Clocking.DOORSTOP)

    def user_start_standby_for_ping(self, user: User):
        """Puts the user on standby for pings"""
        self.__user_start_clocking(user, Clocking.STANDBY_FOR_PINGS)

    def user_start_doorstop(self, user: User):
        """Puts the user on doorstop"""
        self.__user_start_clocking(user, Clocking.DOORSTOP)

    def user_stop_standby_for_ping(self, user: User):
        """Removes the user from standby for pings"""
        self.__user_stop_clocking(user, Clocking.STANDBY_FOR_PINGS)

    def user_stop_doorstop(self, user: User):
        """Removes the user from doorstop"""
        self.__user_stop_clocking(user, Clocking.DOORSTOP)

    def __is_user_clocked(self, user: User, clocking_type) -> bool:
        """Abstract method to know if a user is in a specific clocking"""
        return Clocking.objects.filter(
            eviction=self, user=user, type=clocking_type, end__isnull=True
        ).exists()

    def __user_start_clocking(self, user: User, clocking_type):
        """Abstract method to start a user's clocking"""
        if not self.active:
            raise self.EvictionInactive
        if not Clocking.objects.filter(
            eviction=self, user=user, type=clocking_type, end__isnull=True
        ).exists():
            Clocking.objects.create(user=user, eviction=self, type=clocking_type)

    def __user_stop_clocking(self, user: User, clocking_type):
        """Abstract method to stop a user's clocking"""
        if clocking := Clocking.objects.get(
            eviction=self, user=user, type=clocking_type, end__isnull=True
        ):
            clocking.stop()

    def user_standby_time(self, user: User):
        """Returns for how long the user was on standby"""
        return self.__user_clocking_time(user, Clocking.STANDBY_FOR_PINGS)

    def user_doorstop_time(self, user: User):
        """Returns for how long the user was on doorstop"""
        return self.__user_clocking_time(user, Clocking.DOORSTOP)

    def __user_clocking_time(self, user: User, clocking_type):
        """Abstract method to know how long a user was on a specific duty"""
        clockings = Clocking.objects.filter(
            eviction=self, user=user, type=clocking_type
        )
        return sum(map(lambda x: x.duration, clockings), timezone.timedelta())

    def stop(self):
        """Marks eviction as inactive and stops all active clocking"""
        self.active = False
        self.auto_join = False
        self.save()

        active_clocking = Clocking.objects.filter(eviction=self, end__isnull=True)
        for clocking in active_clocking:
            clocking.stop()

    def spreadsheet_export(self):
        """
        Returns the time spent on standby for ping and doorstop made by each participant.
        The format is adapted to spreadsheets.

        ex:
        PILOT   STANDBY     DOORSTOP
        pilot1  02:04:00    01:30:00
        pilot2  08:25:00    03:00:00
        """

        out_str = "PILOT\tSTANDBY\tDOORSTOP\n"

        for participant in self.participants.all():
            name = (
                participant.profile.main_character.character_name
                if participant.profile.main_character
                else f"{participant.username}"
            )
            standby = format_delta_for_export(self.user_standby_time(participant))
            doorstop = format_delta_for_export(self.user_doorstop_time(participant))

            out_str += f"{name}\t{standby}\t{doorstop}\n"

        return out_str


class Clocking(models.Model):
    """Representing a user spending time on standby for ping or doorstop"""

    DOORSTOP = "DS"
    STANDBY_FOR_PINGS = "SP"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    eviction = models.ForeignKey(Eviction, on_delete=models.CASCADE)
    beginning = models.DateTimeField(default=timezone.now)
    end = models.DateTimeField(null=True, blank=True)
    type = models.CharField(
        max_length=2,
        choices=[
            (DOORSTOP, "Doorstopping"),
            (STANDBY_FOR_PINGS, "Standby for ping"),
        ],
    )

    def __repr__(self):
        return f"{self.user} - {self.type} - {self.beginning}"

    def __str__(self):
        clocking_type = "Doorstop" if self.type == self.DOORSTOP else "Standby for ping"
        profile: UserProfile = self.user.profile  # pylint: disable=no-member
        character_name = (
            profile.main_character.character_name
            if profile.main_character
            else self.user.username
        )
        return f"{clocking_type} by {character_name} started at {self.beginning}"

    @property
    def duration(self):
        """Duration of this clocking"""
        if self.end is not None:
            return self.end - self.beginning

        return timezone.now() - self.beginning

    def stop(self):
        """Stops the clocking"""
        if self.end:
            return
        self.end = timezone.now()
        self.save()
