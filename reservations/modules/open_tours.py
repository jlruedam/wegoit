from datetime import date, time
from reservations.models import Tour, TourSchedule


def open_tours_day():
    """
    Administra los schedules del día actual:
    1. Cierra los schedules cuya fecha ya pasó.
    2. Garantiza que cada tour activo tenga un schedule abierto hoy.
    """

    today = date.today()

    # 1️⃣ Cerrar todos los schedules pasados
    TourSchedule.objects.filter(opened=True, date__lt=today).update(opened=False)

    # 2️⃣ Asegurar que todos los tours activos tengan schedule para hoy
    tours = Tour.objects.filter(active=True)
    schedules_to_create = []

    for tour in tours:
        exists = TourSchedule.objects.filter(tour=tour, date=today).exists()
        if not exists:
            start_time = tour.default_start_time or time(9, 0)
            capacity = tour.default_capacity or 0

            schedules_to_create.append(TourSchedule(
                tour=tour,
                date=today,
                start_time=start_time,
                capacity=capacity,
                opened=True,
            ))

    if schedules_to_create:
        TourSchedule.objects.bulk_create(schedules_to_create)
