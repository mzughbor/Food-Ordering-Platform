from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Meal
from orders.models import Order, OrderItem

# Create your views here.
@login_required
def meal_list(request):
    meals = Meal.objects.filter(is_available=True)
    return render(request, "meals/meal_list.html", {'meals': meals})


@login_required
def meal_detail(request, meal_id):
    """Display meal detail page"""
    meal = get_object_or_404(Meal, id=meal_id)
    
    context = {
        'meal': meal,
    }
    return render(request, 'meals/product_detail.html', context)


@login_required
def add_to_cart(request, meal_id):
    """Add meal to cart"""
    if request.method == 'POST':
        try:
            meal = get_object_or_404(Meal, id=meal_id)
            quantity = int(request.POST.get('quantity', 1))
            
            if not meal.is_available:
                return JsonResponse({'success': False, 'error': 'This meal is currently unavailable.'})
            
            # Get or create pending order for user
            order, created = Order.objects.get_or_create(
                user=request.user,
                status='pending',
                defaults={'restaurant': meal.restaurant, 'total_amount': 0}
            )
            
            # Get or create order item
            order_item, created = OrderItem.objects.get_or_create(
                order=order,
                meal=meal,
                defaults={'quantity': quantity, 'price': meal.price}
            )
            
            if not created:
                order_item.quantity += quantity
                order_item.save()
            
            # Update order total
            order.total_amount = sum(item.total_price for item in order.items.all())
            order.save()
            
            return JsonResponse({'success': True, 'message': f'{meal.name} added to cart!'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
