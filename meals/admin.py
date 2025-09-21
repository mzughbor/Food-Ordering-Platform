from django.contrib import admin
from .models import Meal

# Register your models here.
@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'price', 'is_available', 'created_at')
    list_filter = ('is_available', 'restaurant', 'created_at')
    search_fields = ('name', 'restaurant__name')
    ordering = ('name',)
