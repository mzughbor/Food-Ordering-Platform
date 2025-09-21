from django.contrib import admin
from .models import Order, OrderItem

# Register your models here.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'restaurant', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at', 'restaurant')
    search_fields = ('user__username', 'restaurant__name')
    ordering = ('-created_at',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'meal', 'quantity', 'price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('order__id', 'meal__name')
    ordering = ('-created_at',)
