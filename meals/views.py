from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Meal

# Create your views here.
@login_required
def meal_list(request):
    meals = Meal.objects.filter(is_available=True)
    return render(request, "meals/meal_list.html", {'meals': meals})
