"""Views."""

from typing import Optional

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from allianceauth.authentication.models import User
from allianceauth.notifications.models import Notification
from allianceauth.services.hooks import get_extension_logger

from .models import Clocking, Eviction

logger = get_extension_logger(__name__)


def add_common_context(request, context: Optional[dict] = None) -> dict:
    """adds the common context used by all view"""
    context = context or {}
    new_context = {
        **{
            "user_has_manager_permission": request.user.has_perm(
                "evictionsplit.manager"
            ),
        },
        **context,
    }
    return new_context


@login_required
@permission_required("evictionsplit.basic_access")
def index(request):
    """Module index"""
    user = request.user
    logger.info("Displaying index for user %s", user)
    user_active_evictions = user.evictions_participating.filter(active=True)
    for eviction in user_active_evictions:
        eviction.is_standby = eviction.is_user_on_standby(user)
        eviction.is_doorstop = eviction.is_user_on_doorstop(user)
        eviction.time_standby = eviction.user_standby_time(user)
        eviction.time_doorstop = eviction.user_doorstop_time(user)

    return render(
        request,
        "evictionsplit/index.html",
        add_common_context(
            request,
            {
                "user_active_evictions": user_active_evictions,
            },
        ),
    )


@login_required
@permission_required("evictionsplit.basic_access")
def list_evictions(request):
    """Lists all active evictions that can be applied to join"""
    logger.info("Displaying evictions for user %s", request.user)

    active_evictions = Eviction.objects.filter(active=True)
    user_active_evictions = request.user.evictions_participating.filter(active=True)

    return render(
        request,
        "evictionsplit/list.html",
        add_common_context(
            request,
            {
                "active_evictions": active_evictions,
                "user_active_evictions": user_active_evictions,
            },
        ),
    )


@login_required
@permission_required("evictionsplit.manager")
@require_POST
def new_eviction(request):
    """Creates a new eviction from the GUI"""
    eviction_name = request.POST.get("name")
    logger.debug("Creating eviction called %s", eviction_name)
    eviction = Eviction.create(eviction_name, request.user)
    eviction.save()

    logger.info("Successfully created eviction %s", eviction.name)

    return redirect("evictionsplit:list")


def notify_managers_of_applicant(applicant: User, eviction: Eviction):
    """Sends a notification to every manager that a new application needs to be processed"""
    logger.info("Sending notification to all managers of applicant id %s", applicant.id)
    manager_permission = Permission.objects.get(
        name="Can create and manage evictions", codename="manager"
    )
    manager_users = manager_permission.user_set.all()

    for manager in manager_users:
        logger.debug("Sendint notification to manager id %s", manager.id)
        Notification.objects.notify_user(
            manager,
            title=_("New application to eviction "),
            message=_(
                "%(applicant)s applied to eviction %(eviction)s and needs to be processed"
            )
            % {
                "applicant": applicant.profile.main_character.character_name,
                "eviction": eviction.name,
            },
            level=Notification.Level.INFO,
        )


@login_required
@permission_required("evictionsplit.basic_access")
def apply(request, eviction_id):
    """Allows a user to apply to the eviction"""
    user = request.user
    logger.info("User id %s applying to eviction id %s", user.id, eviction_id)
    eviction = get_object_or_404(Eviction, id=eviction_id)
    eviction.user_apply(user)

    messages.success(request, _("Successfully applied to eviction %s") % eviction.name)

    # TODO move this logic in models
    if user.has_perm("evictionsplit.manager"):
        logger.info(
            "Accepting the application automatically since user id %s is a manager",
            user.id,
        )
        eviction.validate_apply(user)
        messages.success(request, _("Automatically validated the application."))

    elif eviction.auto_join:
        logger.info("Eviction is on auto_join mode, accepting the application")
        eviction.validate_apply(user)
        messages.success(request, _("Automatically accepted in the eviction"))

    else:
        notify_managers_of_applicant(user, eviction)

    return redirect("evictionsplit:list")


@login_required
@permission_required("evictionsplit.manager")
def accept_application(request, eviction_id, user_id):
    """Validates a user application"""
    logger.info(
        "User id %s accepting the application of user id %s to eviction id %s",
        request.user.id,
        user_id,
        eviction_id,
    )
    eviction = get_object_or_404(Eviction, id=eviction_id)
    user = get_object_or_404(User, id=user_id)
    eviction.validate_apply(user)

    Notification.objects.notify_user(
        user=user,
        title=_("Eviction application accepted"),
        message=_("Your application to %s was accepted") % eviction.name,
        level=Notification.Level.INFO,
    )

    messages.success(
        request,
        _("Successfully added %(user)s to %(eviction)s.")
        % {"eviction": eviction, "user": user.profile.main_character.character_name},
    )

    return redirect("evictionsplit:eviction", eviction_id)


@login_required
@permission_required("evictionsplit.basic_access")
def eviction_view(request, eviction_id):
    """Displays information on an eviction"""
    logger.info("Displaying eviction id %s", eviction_id)
    eviction = get_object_or_404(Eviction, id=eviction_id)
    if not (eviction.active or request.user.has_perm("evictionsplit.manage")):
        logger.warning(
            "User id %s tried to view finished eviction id %s",
            request.user.id,
            eviction_id,
        )
        messages.warning(request, _("This eviction is now finished"))
        return redirect("evictionsplit:index")
    is_standby = eviction.is_user_on_standby(request.user)
    is_doorstop = eviction.is_user_on_doorstop(request.user)
    unknown_change = request.GET.get("unknown")

    participants = []
    for participant in eviction.participants.all():
        participants.append(
            {
                "name": (
                    participant.profile.main_character.character_name
                    if participant.profile.main_character
                    else f"User id ({participant.id})"
                ),
                "portrait_url": (
                    participant.profile.main_character.portrait_url
                    if participant.profile.main_character
                    else ""
                ),
                "is_standby": eviction.is_user_on_standby(participant),
                "is_doorstop": eviction.is_user_on_doorstop(participant),
            }
        )

    applicants = []
    if eviction.has_applicants() and request.user.has_perm("evictionsplit.manager"):
        for applicant in eviction.get_applicants():
            applicants.append(
                {
                    "name": applicant.profile.main_character.character_name,
                    "id": applicant.id,
                    "portrait_url": applicant.profile.main_character.portrait_url,
                }
            )

    return render(
        request,
        "evictionsplit/eviction.html",
        add_common_context(
            request,
            {
                "eviction": eviction,
                "is_standby": is_standby,
                "is_doorstop": is_doorstop,
                "time_standby": eviction.user_standby_time(request.user),
                "time_doorstop": eviction.user_doorstop_time(request.user),
                "participants": participants,
                "applicants": applicants,
                "unknown_change": unknown_change,
            },
        ),
    )


# pylint: disable=too-many-branches
@login_required
@permission_required("evictionsplit.basic_access")
@require_POST
def change_clocking(request, eviction_id):
    """Edit the clocking status of a user"""
    logger.info(
        "Changing clocking for user id %s on eviction id %s",
        request.user.id,
        eviction_id,
    )
    eviction = Eviction.objects.get(id=eviction_id)
    user = request.user

    if change := request.POST.get("change"):
        logger.debug("Change value: %s", change)
        if change == "start":
            start = True
        elif change == "stop":
            start = False
        else:
            logger.error("Change parameter value not recognized: %s", change)
            messages.error(request, _("Something went wrong"))
            return redirect("evictionsplit:index")
    else:
        logger.error("No change parameter in the request")
        messages.error(request, _("Something went wrong"))
        return redirect("evictionsplit:index")

    clocking_type = request.POST.get("clocking_type")
    if clocking_type == Clocking.DOORSTOP:
        logger.debug("Clocking_type is doorstop")
        if start:
            eviction.user_start_doorstop(user)
            messages.success(request, _("Started doorstop"))
        else:
            eviction.user_stop_doorstop(user)
            messages.success(request, _("Stopped doorstop"))
    elif clocking_type == Clocking.STANDBY_FOR_PINGS:
        logger.debug("Clocking_type is standby")
        if start:
            eviction.user_start_standby_for_ping(user)
            messages.success(request, _("Started standby for pings"))
        else:
            eviction.user_stop_standby_for_ping(user)
            messages.success(request, _("Stopped standby for pings"))
    else:
        logger.debug("Clocking_type value not recognized: %s", clocking_type)
        messages.error(request, _("Something went wrong"))
        return redirect("evictionsplit:index")

    if request.POST.get("origin") == "eviction":
        logger.debug("Returning to the eviction")
        return redirect("evictionsplit:eviction", eviction_id)

    logger.debug("Returning to index")
    return redirect("evictionsplit:index")


@login_required
@permission_required("evictionsplit.manager")
def management(request):
    """Manage evictions"""
    logger.info("Displaying management window")
    active_evictions = Eviction.objects.filter(active=True)
    inactive_evictions = Eviction.objects.filter(active=False)

    return render(
        request,
        "evictionsplit/management.html",
        add_common_context(
            request,
            {
                "active_evictions": active_evictions,
                "inactive_evictions": inactive_evictions,
            },
        ),
    )


@login_required
@permission_required("evictionsplit.manager")
def stop_eviction(request, eviction_id):
    """Stops an eviction"""
    logger.info("Stopping eviction id %s", eviction_id)
    eviction = Eviction.objects.get(id=eviction_id)
    eviction.stop()

    messages.success(request, _("Successfully stopped the eviction %s") % eviction)

    return redirect("evictionsplit:manage")
