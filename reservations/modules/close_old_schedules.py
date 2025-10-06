from datetime import date
from ..models import TourSchedule

def close_old_schedules():
    today = date.today()
    # Find schedules that are open and have a date in the past
    old_schedules = TourSchedule.objects.filter(date__lt=today, opened=True)
    # Update these schedules to be closed
    updated_count = old_schedules.update(opened=False)
    return updated_count
