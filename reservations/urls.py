from django.urls import path
from . import views

app_name = "tours"

urlpatterns = [

    path('', views.schedule_dashboard, name='home'),
    path("dashboard/schedules/", views.schedule_dashboard, name="schedule_dashboard"),
    path("tours/", views.tour_list, name="tour_list"),
    path("tours/<int:tour_id>/schedules/", views.schedule_list, name="schedule_list"),
    path("schedules/<int:schedule_id>/reservations/", views.reservation_list, name="reservation_list"),
    path('schedules/<int:schedule_id>/reservations/', views.reservation_list, name='reservation_list'),
    # path('schedules/<int:schedule_id>/reservations/new/', views.create_reservation, name='create_reservation')

]