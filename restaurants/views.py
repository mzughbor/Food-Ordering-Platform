from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Restaurant

# Create your views here.
@login_required
def dashboard(request):
    if request.user.role != 'owner':
        return render(request, 'restaurants/access_denied.html')
    
    restaurants = Restaurant.objects.filter(owner=request.user)
    return render(request, 'restaurants/dashboard.html', {'restaurants': restaurants})