from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .modules.close_old_schedules import close_old_schedules

@receiver(user_logged_in)
def run_close_old_schedules_on_login(sender, request, user, **kwargs):
    close_old_schedules()
