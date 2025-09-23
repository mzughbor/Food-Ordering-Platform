from django.urls import path
from . import views

app_name = 'restaurants'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('restaurant-dashboard/', views.restaurant_dashboard, name='restaurant_dashboard'),
    path('manage-meals/', views.manage_meals, name='manage_meals'),
    path('add-meal/', views.add_meal, name='add_meal'),
    path('edit-meal/<int:meal_id>/', views.edit_meal, name='edit_meal'),
    path('delete-meal/<int:meal_id>/', views.delete_meal, name='delete_meal'),
    path('toggle-meal/<int:meal_id>/', views.toggle_meal_availability, name='toggle_meal'),
    path('settings/', views.restaurant_settings, name='restaurant_settings'),
    path('orders/', views.restaurant_orders, name='restaurant_orders'),
]