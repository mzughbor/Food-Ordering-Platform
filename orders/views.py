from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Order, OrderItem
from meals.models import Meal
import json

# Create your views here.
@login_required
def delivery_dashboard(request):
    # Allow admin to see all orders, delivery to see only confirmed orders
    if request.user.role == 'admin':
        orders = Order.objects.all()
    elif request.user.role == 'delivery':
        orders = Order.objects.filter(status='confirmed')
    else:
        return render(request, 'orders/access_denied.html')
    
    return render(request, 'orders/delivery_dashboard.html', {'orders': orders})


@login_required
def cart_view(request):
    """Display shopping cart"""
    # Get cart items for the current user
    cart_items = OrderItem.objects.filter(order__user=request.user, order__status='pending')
    
    # Calculate cart total properly
    cart_total = 0
    for item in cart_items:
        cart_total += float(item.total_price)
    
    context = {
        'cart_items': cart_items,
        'cart_total': f"{cart_total:.2f}",
    }
    return render(request, 'orders/cart.html', context)


@login_required
def checkout_view(request):
    """Display checkout form"""
    # Get cart items for the current user
    cart_items = OrderItem.objects.filter(order__user=request.user, order__status='pending')
    cart_total = sum(item.total_price for item in cart_items)
    
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty. Add some items before checkout.')
        return redirect('meals:meal_list')
    
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def process_checkout(request):
    """Process checkout and create order"""
    if request.method == 'POST':
        # Get cart items
        cart_items = OrderItem.objects.filter(order__user=request.user, order__status='pending')
        
        if not cart_items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('orders:cart')
        
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        zip_code = request.POST.get('zip_code')
        state = request.POST.get('state')
        country = request.POST.get('country')
        payment_method = request.POST.get('payment_method')
        order_notes = request.POST.get('order_notes', '')
        
        # Calculate total
        total_amount = sum(item.total_price for item in cart_items)
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            restaurant=cart_items.first().meal.restaurant,
            status='confirmed',
            total_amount=total_amount
        )
        
        # Update cart items to belong to this order
        cart_items.update(order=order)
        
        # Store delivery information (you might want to create a separate model for this)
        # For now, we'll just redirect to success page
        
        messages.success(request, 'Order placed successfully!')
        return redirect('orders:checkout_success', order_id=order.id)
    
    return redirect('orders:checkout')


@login_required
def checkout_success(request, order_id):
    """Display checkout success page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.all()
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'orders/checkout_success.html', context)


@login_required
@require_http_methods(["POST"])
def update_cart_item(request, item_id):
    """Update cart item quantity via AJAX"""
    try:
        item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
        
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
        
        if 1 <= quantity <= 10:
            item.quantity = quantity
            item.save()
            
            # Calculate subtotal manually since total_price is a property
            subtotal = sum(float(order_item.price * order_item.quantity) for order_item in OrderItem.objects.filter(order=item.order))
            
            return JsonResponse({
                'success': True,
                'total_price': float(item.total_price),
                'subtotal': subtotal
            })
        else:
            return JsonResponse({'success': False, 'error': 'Invalid quantity'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def remove_cart_item(request, item_id):
    """Remove item from cart via AJAX"""
    try:
        item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__status='pending')
        order = item.order
        item.delete()
        
        # Update order total
        order.total_amount = sum(item.total_price for item in order.items.all())
        order.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Item removed from cart'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def cart_count(request):
    """Get cart item count for navigation"""
    count = OrderItem.objects.filter(order__user=request.user, order__status='pending').count()
    return JsonResponse({'count': count})


@login_required
def order_tracking(request, order_id):
    """Track order status"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'orders/order_tracking.html', context)
