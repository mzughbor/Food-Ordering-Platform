from django.contrib import admin
from .models import Restaurant

# Register your models here.
@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'location', 'created_at')
    list_filter = ('created_at', 'owner')
    search_fields = ('name', 'location', 'owner__username')
    ordering = ('name',)
