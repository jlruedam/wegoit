from django.contrib import admin
from .models import Tour, TourSchedule, Agency, Reservation

# Register your models here.
admin.site.register(Tour)
admin.site.register(TourSchedule)
admin.site.register(Agency)
admin.site.register(Reservation)
