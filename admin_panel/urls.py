from django.urls import path
from . import views

app_name = 'admin'

urlpatterns = [
    # User Management
    path('users/create/', views.create_user, name='create_user'),
    path('users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    
    # Order Management
    path('orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('orders/<int:order_id>/delete/', views.delete_order, name='delete_order'),
    path('orders/<int:order_id>/edit/', views.edit_order, name='edit_order'),
    
    # Restaurant Management
    path('restaurants/<int:restaurant_id>/edit/', views.edit_restaurant, name='edit_restaurant'),
    path('restaurants/<int:restaurant_id>/delete/', views.delete_restaurant, name='delete_restaurant'),
    path('restaurants/<int:restaurant_id>/toggle-status/', views.toggle_restaurant_status, name='toggle_restaurant_status'),
    path('restaurants/list/', views.restaurant_list, name='restaurant_list'),
    path('restaurants/create/', views.create_restaurant, name='create_restaurant'),
    path('restaurants/analytics/', views.restaurant_analytics, name='restaurant_analytics'),
    path('restaurants/bulk-toggle-status/', views.bulk_toggle_restaurant_status, name='bulk_toggle_restaurant_status'),
    path('restaurants/bulk-delete/', views.bulk_delete_restaurants, name='bulk_delete_restaurants'),
    
    # Meal Management
    path('meals/<int:meal_id>/edit/', views.edit_meal, name='edit_meal'),
    path('meals/<int:meal_id>/delete/', views.delete_meal, name='delete_meal'),
    path('meals/<int:meal_id>/toggle-availability/', views.toggle_meal_availability, name='toggle_meal_availability'),
    
    # Platform Settings
    path('settings/', views.platform_settings, name='platform_settings'),
    path('settings/update/', views.update_platform_settings_ajax, name='update_platform_settings'),
    path('settings/get/', views.get_platform_settings, name='get_platform_settings'),
    path('settings/site-info/', views.update_site_info, name='update_site_info'),
]
