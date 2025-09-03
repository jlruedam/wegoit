from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Tour, TourSchedule, Reservation, Agency
from django.db.models import Sum


# Create your views here.
@login_required
def home(request):
    ctx = {}
    return render(request, 'home/index.html', ctx)


def schedule_dashboard(request):
    schedules = TourSchedule.objects.all()
    
    # Añadir la cantidad de cupos disponibles a cada schedule
    for schedule in schedules:
        reserved_pax = schedule.reservations.aggregate(total=Sum('pax'))['total'] or 0
        schedule.available_spots = schedule.capacity - reserved_pax
    
    return render(request, "home/schedule_dashboard.html", {"schedules": schedules})

# ---------------- TOUR ----------------
@login_required
def tour_list(request):
    tours = Tour.objects.all()
    return render(request, "tours/tour_list.html", {"tours": tours})

# ---------------- SCHEDULE ----------------
@login_required
def schedule_list(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    schedules = tour.schedules.all()
    return render(request, "schedules/schedule_list.html", {"tour": tour, "schedules": schedules})

# ---------------- RESERVATION ----------------
@login_required
def reservation_list(request, schedule_id):
    schedule = get_object_or_404(TourSchedule, id=schedule_id)
    reservations = schedule.reservations.all()
    return render(request, "reservations/reservation_list.html", {"schedule": schedule, "reservations": reservations})
