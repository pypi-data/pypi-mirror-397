"""https://stackoverflow.com/a/46928226"""

from django import template

register = template.Library()


@register.filter()
def smooth_timedelta(timedeltaobj):
    """Convert a datetime.timedelta object into Days, Hours, Minutes, Seconds."""
    secs = timedeltaobj.total_seconds()
    total_time = ""
    if secs > 86400:  # 60sec * 60min * 24hrs
        days = secs // 86400
        total_time += f"{int(days)} days"
        secs = secs - days * 86400

    if secs > 3600:
        hrs = secs // 3600
        total_time += f" {int(hrs)} hours"
        secs = secs - hrs * 3600

    if secs > 60:
        mins = secs // 60
        total_time += f" {int(mins)} minutes"
        secs = secs - mins * 60

    if secs > 0:
        total_time += f" {int(secs)} seconds"
    return total_time
