from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.delivery_dashboard, name='delivery_dashboard'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('process-checkout/', views.process_checkout, name='process_checkout'),
    path('checkout-success/<int:order_id>/', views.checkout_success, name='checkout_success'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove-cart-item/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('cart-count/', views.cart_count, name='cart_count'),
    path('order-tracking/<int:order_id>/', views.order_tracking, name='order_tracking'),
]