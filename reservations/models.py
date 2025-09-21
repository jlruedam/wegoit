from django.db import models
from django.contrib.auth.models import User
from django.conf import settings



class AuditModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)   # fecha creación
    updated_at = models.DateTimeField(auto_now=True)       # fecha última actualización
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(class)s_created",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(class)s_updated",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        abstract = True

class Agency(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class Tour(models.Model):
    tour_name = models.CharField("Nombre del tour", max_length=255, unique=True)
    base_price = models.DecimalField("Precio base", max_digits=10, decimal_places=2)
    default_capacity = models.PositiveIntegerField("Capacidad por defecto")
    description = models.TextField("Descripción", blank=True, null=True)
    default_start_time = models.TimeField("Hora de inicio por defecto", null=True, blank=True)
    active = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Tour"
        verbose_name_plural = "Tours"
        ordering = ["tour_name"]

    def __str__(self):
        return self.tour_name


class TourSchedule(models.Model):
    tour = models.ForeignKey(
        "Tour",
        on_delete=models.CASCADE,
        related_name="schedules",
        verbose_name="Tour"
    )
    date = models.DateField("Fecha")
    start_time = models.TimeField("Hora de inicio")
    capacity = models.PositiveIntegerField("Capacidad")
    opened = models.BooleanField("Abierto", default=True)

    class Meta:
        verbose_name = "Horario de tour"
        verbose_name_plural = "Horarios de tours"
        ordering = ["-date", "start_time"]
        unique_together = ("tour", "date", "start_time")

    def __str__(self):
        return f"{self.tour.tour_name} - {self.date} {self.start_time}"

    @property
    def reserved_spots(self):
        # suma de pax en todas las reservaciones de este schedule
        return self.reservations.aggregate(total=models.Sum("pax"))["total"] or 0

    @property
    def available_spots(self):
        # capacidad total del horario menos los cupos ya reservados
        return self.capacity - self.reserved_spots

class Reservation(AuditModel):
    
    schedule = models.ForeignKey(TourSchedule, on_delete=models.CASCADE, related_name="reservations")
    type_document = models.CharField(max_length=50, null=True, blank=True)
    costumer_document = models.IntegerField()
    customer_name = models.CharField(max_length=255)
    pax = models.IntegerField()
    total_to_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Valores esperados (compromisos)
    expected_agency_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    expected_customer_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    agency = models.ForeignKey(Agency, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50, default="Reservado")
    
    def __str__(self):
        return f"Reserva {self.id} - {self.customer_name}"
    
    @property
    def total_paid_via_agency(self): # Total a pagar por la agencia
        return sum(p.amount for p in self.payments.filter(source="agency"))
    @property
    def total_paid_direct(self):# Total a pagar por el cliente
        return sum(p.amount for p in self.payments.filter(source="customer"))
    @property
    def total_paid(self): # Total a pagar por la agencia y por el cliente
        return self.total_paid_via_agency + self.total_paid_direct
    @property 
    def pending_agency_balance(self): 
        """Saldo que la agencia aún debe transferir"""
        return max(self.expected_agency_payment - self.total_paid_via_agency, 0)
    @property
    def pending_customer_balance(self):
        """Saldo que el cliente aún debe pagar directamente"""
        return max(self.expected_customer_payment - self.total_paid_direct, 0)
    @property
    def pending_balance(self):
        """Saldo total pendiente"""
        return self.pending_agency_balance + self.pending_customer_balance
    @property
    def is_fully_paid(self):
        return self.pending_balance() == 0

    

class ReservationPayment(models.Model):
    PAYMENT_SOURCE_CHOICES = [
        ("agency", "Pagado a la Agencia"),
        ("customer", "Pagado directamente al Operador"),
    ]

    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    source = models.CharField(max_length=20, choices=PAYMENT_SOURCE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Pago {self.amount} ({self.get_source_display()}) - Reserva {self.reservation.id}"
