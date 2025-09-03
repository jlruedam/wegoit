from django.db import models
from django.contrib.auth.models import User



class Agency(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class Tour(models.Model):
    tour_name = models.CharField(max_length=255)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    default_capacity = models.IntegerField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.tour_name


class TourSchedule(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="schedules")
    date = models.DateField()
    start_time = models.TimeField()
    capacity = models.IntegerField()
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.tour.tour_name} - {self.date} {self.start_time}"


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
    status = models.CharField(max_length=50)
    debt = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_received_on_tour = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    agency = models.ForeignKey(Agency, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Reserva {self.id} - {self.customer_name}"
