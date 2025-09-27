from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('accounts/login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]