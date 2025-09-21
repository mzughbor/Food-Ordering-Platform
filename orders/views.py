from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Order

# Create your views here.
@login_required
def delivery_dashboard(request):
    if request.user.role != 'delivery':
        return render(request, 'orders/access_denied.html')
    
    orders = Order.objects.filter(status='confirmed')
    return render(request, 'orders/delivery_dashboard.html', {'orders': orders})
