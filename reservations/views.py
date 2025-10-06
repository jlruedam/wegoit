from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Tour, TourSchedule, Reservation, Agency, ReservationPayment
from django.db.models import Sum, Count
from reservations.modules.open_tours import open_tours_day
from reservations.modules.close_old_schedules import close_old_schedules
from .forms import TourScheduleForm, ReservationForm, TourForm, AgencyForm, ReservationPaymentForm
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models.functions import Coalesce
from django.db.models import Value, Q, DecimalField
from django.db.models.functions import TruncMonth
import openpyxl

# Create your views here.
@login_required
def home(request):
    if request.method == "POST":
        form = TourScheduleForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect("tours:home")
    
    close_old_schedules() # Call the function to close old schedules

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

    # Conversión a tipos nativos
    reservations_by_tour = [
        {"schedule__tour__tour_name": r["schedule__tour__tour_name"], "total": int(r["total"] or 0)}
        for r in reservations_by_tour
    ]
    payments_by_source = [
        {"source": p["source"], "total": float(p["total"] or 0)}
        for p in payments_by_source
    ]
    pax_by_tour = [
        {"schedule__tour__tour_name": t["schedule__tour__tour_name"], "total_pax": int(t["total_pax"] or 0)}
        for t in pax_by_tour
    ]

    # 👉 Programaciones activas con cálculos
    schedules_actives = []
    for schedule in TourSchedule.objects.filter(opened=True).order_by("date", "start_time"):
        reservations = schedule.reservations.all()
        total_pax = reservations.aggregate(total=Sum("pax"))["total"] or 0
        total_sales = reservations.aggregate(total=Sum("total_to_pay"))["total"] or 0
        pending_total = sum(r.pending_balance for r in reservations)

        schedules_actives.append({
            "tour": schedule.tour.tour_name,
            "programacion": f"{schedule.date} {schedule.start_time.strftime('%H:%M')}",
            "capacity": schedule.capacity,
            "sold_spots": total_pax,
            "available_spots": schedule.available_spots, 
            "total_sales": float(total_sales),
            "pending": float(pending_total),
        })

    # 👉 Nueva gráfica: Deuda por agencia
    agencias_data = (
        Reservation.objects
        .values("agency__name")
        .annotate(
            total=Coalesce(
                Sum("expected_agency_payment"),
                Value(0, output_field=DecimalField())
            ),
            pagado=Coalesce(
                Sum("payments__amount", filter=Q(payments__source="agency")),
                Value(0, output_field=DecimalField())
            )
        )
    )

    deuda_agencias = [
        {
            "agency": a["agency__name"],
            "deuda": float(a["total"]) - float(a["pagado"])
        }for a in agencias_data
    ]

    # Ventas totales por mes
    ventas_por_mes_qs = (
        Reservation.objects
        .annotate(mes=TruncMonth('schedule__date'))
        .values('mes')
        .annotate(total_ventas=Sum('total_to_pay'))
        .order_by('mes')
    )

    # Convertir a lista de diccionarios y manejar nulos
    ventas_por_mes = [
        {"mes": v["mes"].strftime("%b %Y"), "ventas": float(v["total_ventas"] or 0)}
        for v in ventas_por_mes_qs
    ]
    
    # Total de ventas global
    total_ventas = sum(s['total_sales'] for s in schedules_actives)

    # Ventas totales por tour
    ventas_por_tour_qs = (
        Reservation.objects
        .values('schedule__tour__tour_name')
        .annotate(total_ventas=Sum('total_to_pay'))
        .order_by('schedule__tour__tour_name')
    )

    ventas_por_tour = [
        {
            "tour": v["schedule__tour__tour_name"],
            "ventas": float(v["total_ventas"] or 0)
        }
        for v in ventas_por_tour_qs
    ]

    context = {
        "reservations_by_tour": reservations_by_tour,
        "payments_by_source": payments_by_source,
        "pax_by_tour": pax_by_tour,
        "schedules_actives": schedules_actives,
        "deuda_agencias": deuda_agencias, 
        "total_ventas": total_ventas,
        "ventas_por_tour": ventas_por_tour,
        "ventas_por_mes": ventas_por_mes
        
    }

    return render(request, "dashboard/dashboard.html", context)

@login_required
def export_reservations_xls(request):
    reservations = Reservation.objects.select_related(
        "schedule__tour", "agency"
    ).all()

    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Reservas"

    headers = [
        "ID Reserva",
        "Tour",
        "Fecha",
        "Hora",
        "Cliente",
        "Teléfono",
        "Pax",
        "Total a Pagar",
        "A Pagar por Agencia",
        "A Pagar por Cliente",
        "Saldo Pendiente",
        "Agencia",
        "NIT Agencia",
        "Estado",
    ]
    worksheet.append(headers)

    for r in reservations:
        worksheet.append([
            r.id,
            r.schedule.tour.tour_name,
            r.schedule.date,
            r.schedule.start_time,
            r.customer_name,
            r.customer_phone,
            r.pax,
            r.total_to_pay,
            r.expected_agency_payment,
            r.expected_customer_payment,
            r.pending_balance,
            r.agency.name if r.agency else "N/A",
            r.agency.tax_id if r.agency else "N/A",
            r.status,
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=reservas.xlsx"
    workbook.save(response)

    return response


# ---------------- EXCEL EXPORTS ----------------
@login_required
def export_schedule_reservations_xls(request, schedule_id):
    schedule = get_object_or_404(TourSchedule, id=schedule_id)
    reservations = Reservation.objects.filter(schedule=schedule).select_related(
        "schedule__tour", "agency"
    ).all()

    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = f"Reservas {schedule.tour.tour_name} - {schedule.date}"

    headers = [
        "ID Reserva",
        "Tour",
        "Fecha",
        "Hora",
        "Cliente",
        "Teléfono",
        "Pax",
        "Total a Pagar",
        "A Pagar por Agencia",
        "A Pagar por Cliente",
        "Saldo Pendiente",
        "Agencia",
        "NIT Agencia",
        "Estado",
    ]
    worksheet.append(headers)

    for r in reservations:
        worksheet.append([
            r.id,
            r.schedule.tour.tour_name,
            r.schedule.date,
            r.schedule.start_time,
            r.customer_name,
            r.customer_phone,
            r.pax,
            r.total_to_pay,
            r.expected_agency_payment,
            r.expected_customer_payment,
            r.pending_balance,
            r.agency.name if r.agency else "N/A",
            r.agency.tax_id if r.agency else "N/A",
            r.status,
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f"attachment; filename=reservas_{schedule.tour.tour_name}_{schedule.date}.xlsx"
    workbook.save(response)

    return response
