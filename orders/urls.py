from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.delivery_dashboard, name='delivery_dashboard'),
]