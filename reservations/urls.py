from django.urls import path
from . import views

app_name = "tours"

urlpatterns = [

    path('', views.home, name='home'),
    path("tours/", views.tour_list, name="tour_list"),
    path("tours/<int:tour_id>/schedules/", views.schedule_list, name="schedule_list"),
    path("schedules/<int:schedule_id>/reservations/", views.reservation_list, name="reservation_list"),
    path('schedules/reservations/', views.reservation_list_general, name='reservation_list_general'),
    path("reservations/<int:schedule_id>/create", views.create_reservation, name="create_reservation"),
    path("agencies/", views.agency_list, name="agency_list"),
    path("agencies/create/", views.agency_create, name="agency_create"),

]