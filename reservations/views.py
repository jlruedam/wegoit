from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Tour, TourSchedule, Reservation, Agency, ReservationPayment
from django.db.models import Sum, Count
from reservations.modules.open_tours import open_tours_day
from .forms import TourScheduleForm, ReservationForm, TourForm, AgencyForm, ReservationPaymentForm
from django.contrib import messages
from django.views.decorators.http import require_POST


# Create your views here.
@login_required
def home(request):
    if request.method == "POST":
        form = TourScheduleForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect("tours:home")
    
    tours = Tour.objects.all()
    schedules = TourSchedule.objects.filter(opened = True)
    form = TourScheduleForm()

    ctx = {
        "tours":tours,
        "schedules": schedules,
        "form":form
    }
    
    return render(request, "home/index.html", ctx)

# ---------------- TOUR ----------------
@login_required
def tour_list(request):
    tours = Tour.objects.all()
    if request.method == "POST":
        form = TourForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("tours:tour_list")  # redirige a la lista de tours
    else:
        form = TourForm()

    ctx = {
        "form": form,
        "tours": tours
    }

    return render(request, "tours/tour_list.html",ctx)

# ---------------- SCHEDULE ----------------
@login_required
def schedule_list(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    schedules = tour.schedules.all()
    return render(request, "schedules/schedule_list.html", {"tour": tour, "schedules": schedules})

# ---------------- RESERVATION ----------------
@login_required
def create_reservation(request, schedule_id):
    schedule = get_object_or_404(TourSchedule, id=schedule_id)
    
    if request.method == "POST":
        form = ReservationForm(request.POST, schedule=schedule)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.schedule = schedule  # asegurar el horario
            reservation.status = "Reservado"  # asegurar estado
            reservation.created_by = request.user
            reservation.save()
            return redirect("tours:home")
    else:
        form = ReservationForm(schedule=schedule)

    return render(request, "reservations/reservation_form.html", {
        "form": form,
        "schedule": schedule,
    })

@login_required
def reservation_list(request, schedule_id):
    schedule = get_object_or_404(TourSchedule, id=schedule_id)
    reservations = schedule.reservations.all()
    return render(request, "reservations/reservation_list.html", {"schedule": schedule, "reservations": reservations})

@login_required
def reservation_list_general(request):
    """
    Vista que lista todas las reservas
    """
    reservations = Reservation.objects.select_related(
        "schedule__tour", "agency", "created_by"
    ).all().order_by("-id")  # las más recientes primero

    return render(request, "reservations/reservation_list.html", {
        "reservations": reservations, "general":True
    })

# ---------------- PAYMENTS ----------------
@login_required
@require_POST
def add_payment(request):
    reservation_id = request.POST.get("reservation_id")
    reservation = get_object_or_404(Reservation, id=reservation_id)

    form = ReservationPaymentForm(request.POST)
    if form.is_valid():
        payment = form.save(commit=False)
        payment.reservation = reservation

        # Validaciones
        if payment.source == "agency" and payment.amount > reservation.pending_agency_balance:
            return JsonResponse({
                "success": False,
                "message": f"El monto ({payment.amount}) supera el saldo pendiente de la agencia ({reservation.pending_agency_balance})."
            })

        if payment.source == "customer" and payment.amount > reservation.pending_customer_balance:
            return JsonResponse({
                "success": False,
                "message": f"El monto ({payment.amount}) supera el saldo pendiente del cliente ({reservation.pending_customer_balance})."
            })

        payment.save()
        return JsonResponse({"success": True, "message": "Pago registrado correctamente."})

    return JsonResponse({"success": False, "message": "Hubo un error al registrar el pago."})
@login_required
def reservation_payments_list(request, reservation_id):
    # Traemos la reserva o mostramos 404 si no existe
    reservation = get_object_or_404(Reservation, id=reservation_id)

    # Pagos asociados a la reserva
    payments = ReservationPayment.objects.filter(reservation=reservation).order_by("-payment_date")

    context = {
        "reservation": reservation,
        "payments": payments,
    }
    return render(request, "payments/reservation_payments_list.html", context)
# ---------------- AGENCIES ----------------
@login_required
def agency_list(request):
    agencies = Agency.objects.all()
    form = AgencyForm()
    return render(request, "agencies/agency_list.html", {"agencies": agencies, "form": form})

@login_required
def agency_create(request):
    if request.method == "POST":
        form = AgencyForm(request.POST)
        if form.is_valid():
            form.save()
    return redirect("tours:agency_list")

@login_required
def dashboard(request):
    reservations_by_tour = (
        Reservation.objects
        .values("schedule__tour__tour_name")
        .annotate(total=Count("id"))
        .order_by("schedule__tour__tour_name")
    )

    payments_by_source = (
        ReservationPayment.objects
        .values("source")
        .annotate(total=Sum("amount"))
    )

    pax_by_tour = (
        Reservation.objects
        .values("schedule__tour__tour_name")
        .annotate(total_pax=Sum("pax"))
        .order_by("-total_pax")[:5]
    )

    # 👇 Convertimos Decimals a float
    payments_by_source = [
        {"source": p["source"], "total": float(p["total"] or 0)}
        for p in payments_by_source
    ]
    pax_by_tour = [
        {"schedule__tour__tour_name": t["schedule__tour__tour_name"], "total_pax": int(t["total_pax"] or 0)}
        for t in pax_by_tour
    ]

    context = {
        "reservations_by_tour": list(reservations_by_tour),
        "payments_by_source": payments_by_source,
        "pax_by_tour": pax_by_tour,
    }
    return render(request, "dashboard/dashboard.html", context)
