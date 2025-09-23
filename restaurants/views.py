from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Restaurant
from .forms import RestaurantForm
from meals.models import Meal
from meals.forms import MealForm, MealSearchForm
from orders.models import Order


@login_required
def dashboard(request):
    """Basic restaurant dashboard"""
    if request.user.role == 'admin':
        restaurants = Restaurant.objects.all()
    elif request.user.role == 'owner':
        restaurants = Restaurant.objects.filter(owner=request.user)
    else:
        return render(request, 'restaurants/access_denied.html')
    
    return render(request, 'restaurants/dashboard.html', {'restaurants': restaurants})


@login_required
def restaurant_dashboard(request):
    """Detailed restaurant dashboard for owners and admins"""
    if request.user.role not in ['owner', 'admin']:
        messages.error(request, 'Access denied. Restaurant owner privileges required.')
        return redirect('users:home')
    
    # Get restaurant data
    if request.user.role == 'admin':
        restaurant = Restaurant.objects.first()
        restaurants = Restaurant.objects.all()
    else:
        restaurants = Restaurant.objects.filter(owner=request.user)
        restaurant = restaurants.first() if restaurants.exists() else None
    
    # Get meals for the restaurant
    meals = []
    recent_orders = []
    
    if restaurant:
        meals = Meal.objects.filter(restaurant=restaurant)[:10]
        recent_orders = Order.objects.filter(restaurant=restaurant).select_related('user').order_by('-created_at')[:10]
    
    context = {
        'restaurant': restaurant,
        'restaurants': restaurants,
        'meals': meals,
        'recent_orders': recent_orders,
    }
    return render(request, 'restaurants/restaurant_dashboard.html', context)


@login_required
def manage_meals(request):
    """Manage meals for restaurant"""
    if request.user.role not in ['owner', 'admin']:
        messages.error(request, 'Access denied. Restaurant owner privileges required.')
        return redirect('users:home')
    
    # Get restaurant
    if request.user.role == 'admin':
        restaurant = Restaurant.objects.first()
    else:
        restaurant = Restaurant.objects.filter(owner=request.user).first()
    
    if not restaurant:
        messages.error(request, 'No restaurant found.')
        return redirect('restaurants:restaurant_dashboard')
    
    # Handle search and filtering
    search_form = MealSearchForm(request.GET)
    meals = Meal.objects.filter(restaurant=restaurant)
    
    if search_form.is_valid():
        search = search_form.cleaned_data.get('search')
        is_available = search_form.cleaned_data.get('is_available')
        
        if search:
            meals = meals.filter(name__icontains=search)
        if is_available:
            meals = meals.filter(is_available=(is_available == 'true'))
    
    # Pagination
    paginator = Paginator(meals, 10)
    page_number = request.GET.get('page')
    meals = paginator.get_page(page_number)
    
    context = {
        'restaurant': restaurant,
        'meals': meals,
        'search_form': search_form,
    }
    return render(request, 'restaurants/manage_meals.html', context)


@login_required
def add_meal(request):
    """Add a new meal"""
    if request.user.role not in ['owner', 'admin']:
        messages.error(request, 'Access denied. Restaurant owner privileges required.')
        return redirect('users:home')
    
    # Get restaurant
    if request.user.role == 'admin':
        restaurant = Restaurant.objects.first()
    else:
        restaurant = Restaurant.objects.filter(owner=request.user).first()
    
    if not restaurant:
        messages.error(request, 'No restaurant found.')
        return redirect('restaurants:restaurant_dashboard')
    
    if request.method == 'POST':
        form = MealForm(request.POST, request.FILES, restaurant=restaurant)
        if form.is_valid():
            meal = form.save(commit=False)
            meal.restaurant = restaurant
            meal.save()
            messages.success(request, f'Meal "{meal.name}" added successfully!')
            return redirect('restaurants:manage_meals')
    else:
        form = MealForm(restaurant=restaurant)
    
    context = {
        'form': form,
        'restaurant': restaurant,
    }
    return render(request, 'restaurants/add_meal.html', context)


@login_required
def edit_meal(request, meal_id):
    """Edit an existing meal"""
    if request.user.role not in ['owner', 'admin']:
        messages.error(request, 'Access denied. Restaurant owner privileges required.')
        return redirect('users:home')
    
    # Get meal
    if request.user.role == 'admin':
        meal = get_object_or_404(Meal, id=meal_id)
    else:
        meal = get_object_or_404(Meal, id=meal_id, restaurant__owner=request.user)
    
    if request.method == 'POST':
        form = MealForm(request.POST, request.FILES, instance=meal, restaurant=meal.restaurant)
        if form.is_valid():
            form.save()
            messages.success(request, f'Meal "{meal.name}" updated successfully!')
            return redirect('restaurants:manage_meals')
    else:
        form = MealForm(instance=meal, restaurant=meal.restaurant)
    
    context = {
        'form': form,
        'meal': meal,
        'restaurant': meal.restaurant,
    }
    return render(request, 'restaurants/edit_meal.html', context)


@login_required
def delete_meal(request, meal_id):
    """Delete a meal"""
    if request.user.role not in ['owner', 'admin']:
        messages.error(request, 'Access denied. Restaurant owner privileges required.')
        return redirect('users:home')
    
    # Get meal
    if request.user.role == 'admin':
        meal = get_object_or_404(Meal, id=meal_id)
    else:
        meal = get_object_or_404(Meal, id=meal_id, restaurant__owner=request.user)
    
    if request.method == 'POST':
        meal_name = meal.name
        meal.delete()
        messages.success(request, f'Meal "{meal_name}" deleted successfully!')
        return redirect('restaurants:manage_meals')
    
    context = {
        'meal': meal,
    }
    return render(request, 'restaurants/delete_meal.html', context)


@login_required
def toggle_meal_availability(request, meal_id):
    """Toggle meal availability via AJAX"""
    if request.user.role not in ['owner', 'admin']:
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    # Get meal
    if request.user.role == 'admin':
        meal = get_object_or_404(Meal, id=meal_id)
    else:
        meal = get_object_or_404(Meal, id=meal_id, restaurant__owner=request.user)
    
    if request.method == 'POST':
        meal.is_available = not meal.is_available
        meal.save()
        return JsonResponse({
            'success': True,
            'is_available': meal.is_available,
            'message': f'Meal is now {"available" if meal.is_available else "unavailable"}'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def restaurant_settings(request):
    """Restaurant settings and profile management"""
    if request.user.role not in ['owner', 'admin']:
        messages.error(request, 'Access denied. Restaurant owner privileges required.')
        return redirect('users:home')
    
    # Get restaurant
    if request.user.role == 'admin':
        restaurant = Restaurant.objects.first()
    else:
        restaurant = Restaurant.objects.filter(owner=request.user).first()
    
    if not restaurant:
        messages.error(request, 'No restaurant found.')
        return redirect('restaurants:restaurant_dashboard')
    
    if request.method == 'POST':
        form = RestaurantForm(request.POST, instance=restaurant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Restaurant settings updated successfully!')
            return redirect('restaurants:restaurant_settings')
    else:
        form = RestaurantForm(instance=restaurant)
    
    # Get restaurant statistics
    total_meals = Meal.objects.filter(restaurant=restaurant).count()
    available_meals = Meal.objects.filter(restaurant=restaurant, is_available=True).count()
    total_orders = Order.objects.filter(restaurant=restaurant).count()
    total_revenue = Order.objects.filter(restaurant=restaurant).aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    context = {
        'form': form,
        'restaurant': restaurant,
        'total_meals': total_meals,
        'available_meals': available_meals,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
    }
    return render(request, 'restaurants/restaurant_settings.html', context)


@login_required
def restaurant_orders(request):
    """View restaurant orders"""
    if request.user.role not in ['owner', 'admin']:
        messages.error(request, 'Access denied. Restaurant owner privileges required.')
        return redirect('users:home')
    
    # Get restaurant
    if request.user.role == 'admin':
        restaurant = Restaurant.objects.first()
    else:
        restaurant = Restaurant.objects.filter(owner=request.user).first()
    
    if not restaurant:
        messages.error(request, 'No restaurant found.')
        return redirect('restaurants:restaurant_dashboard')
    
    # Get orders
    orders = Order.objects.filter(restaurant=restaurant).select_related('user').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(orders, 15)
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    
    context = {
        'restaurant': restaurant,
        'orders': orders,
    }
    return render(request, 'restaurants/restaurant_orders.html', context)