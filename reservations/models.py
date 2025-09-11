from django.db import models
from django.contrib.auth.models import User



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

class Reservation(models.Model):
    """
        schedule: Relación con la programación del tour
        customer_name: Nombre del Cliente
        pax: capacidad máxima del tour
        net_payment: Total Abonado
        pending_balance = saldo pendiente
        status: estado de la reserva (creada, revisada, confirmada, cancelada)
    """
    schedule = models.ForeignKey(TourSchedule, on_delete=models.CASCADE, related_name="reservations")
    customer_name = models.CharField(max_length=255)
    pax = models.IntegerField()
    net_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pending_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=50, default="Reservado")
    debt = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_received_on_tour = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    agency = models.ForeignKey(Agency, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Reserva {self.id} - {self.customer_name}"
