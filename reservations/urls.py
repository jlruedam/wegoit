from django.urls import path
from . import views

app_name = "tours"

urlpatterns = [

    path('', views.home, name='home'),
    path("tours/", views.tour_list, name="tour_list"),
    path("tours/<int:tour_id>/schedules/", views.schedule_list, name="schedule_list"),
    path("schedules/<int:schedule_id>/reservations/", views.reservation_list, name="reservation_list"),

]