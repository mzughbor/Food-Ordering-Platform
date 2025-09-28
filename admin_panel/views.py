from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import transaction
from django.core.files.storage import default_storage
import json

from users.models import User
from restaurants.models import Restaurant
from orders.models import Order
from meals.models import Meal
from .models import PlatformSettings
from .forms import PlatformSettingsForm
from .decorators import admin_required, can_edit_user, can_delete_user, can_manage_restaurant, can_manage_meal, can_view_order


@login_required
@require_http_methods(["POST"])
def toggle_user_status(request, user_id):
    """Toggle user active status"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        user = get_object_or_404(User, id=user_id)
        
        # Prevent admin from deactivating themselves
        if user.id == request.user.id:
            return JsonResponse({'success': False, 'error': 'Cannot deactivate your own account'})
        
        user.is_active = not user.is_active
        user.save()
        
        return JsonResponse({
            'success': True, 
            'is_active': user.is_active,
            'message': f'User {"activated" if user.is_active else "deactivated"} successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def delete_user(request, user_id):
    """Delete a user"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        user = get_object_or_404(User, id=user_id)
        
        # Prevent admin from deleting themselves
        if user.id == request.user.id:
            return JsonResponse({'success': False, 'error': 'Cannot delete your own account'})
        
        username = user.username
        user.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'User {username} deleted successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["GET", "POST"])
def edit_user(request, user_id):
    """Edit user information"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        user = get_object_or_404(User, id=user_id)
        
        if request.method == 'GET':
            # Return user data for editing
            return JsonResponse({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'is_active': user.is_active,
                    'date_joined': user.date_joined.isoformat()
                }
            })
        else:
            # POST request - update user
            data = json.loads(request.body)
            
            # Update user fields
            if 'username' in data:
                user.username = data['username']
            if 'email' in data:
                user.email = data['email']
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'role' in data:
                user.role = data['role']
            if 'is_active' in data:
                user.is_active = data['is_active']
            
            user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'User updated successfully'
            })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def update_order_status(request, order_id):
    """Update order status"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        order = get_object_or_404(Order, id=order_id)
        data = json.loads(request.body)
        
        new_status = data.get('status')
        valid_statuses = ['pending', 'confirmed', 'preparing', 'ready', 'delivered', 'cancelled']
        
        if new_status not in valid_statuses:
            return JsonResponse({'success': False, 'error': 'Invalid status'})
        
        order.status = new_status
        order.save()
        
        return JsonResponse({
            'success': True,
            'status': order.status,
            'message': f'Order status updated to {new_status}'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def delete_order(request, order_id):
    """Delete an order"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        order = get_object_or_404(Order, id=order_id)
        order_id = order.id
        order.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Order #{order_id} deleted successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def edit_order(request, order_id):
    """Edit order information"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        order = get_object_or_404(Order, id=order_id)
        data = json.loads(request.body)
        
        # Update order fields
        if 'total_amount' in data:
            order.total_amount = data['total_amount']
        if 'delivery_address' in data:
            order.delivery_address = data['delivery_address']
        if 'notes' in data:
            order.notes = data['notes']
        
        order.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Order updated successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["GET", "POST"])
def edit_restaurant(request, restaurant_id):
    """Edit restaurant information"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        data = json.loads(request.body)
        
        # Update restaurant fields
        if 'name' in data:
            restaurant.name = data['name']
        if 'description' in data:
            restaurant.description = data['description']
        if 'location' in data:
            restaurant.location = data['location']
        if 'is_active' in data:
            restaurant.is_active = data['is_active']
        
        restaurant.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Restaurant updated successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def delete_restaurant(request, restaurant_id):
    """Delete a restaurant"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        restaurant_name = restaurant.name
        restaurant.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Restaurant {restaurant_name} deleted successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def toggle_restaurant_status(request, restaurant_id):
    """Toggle restaurant active status"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        restaurant.is_active = not restaurant.is_active
        restaurant.save()
        
        return JsonResponse({
            'success': True,
            'is_active': restaurant.is_active,
            'message': f'Restaurant {"activated" if restaurant.is_active else "deactivated"} successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def edit_meal(request, meal_id):
    """Edit meal information"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        meal = get_object_or_404(Meal, id=meal_id)
        data = json.loads(request.body)
        
        # Update meal fields
        if 'name' in data:
            meal.name = data['name']
        if 'description' in data:
            meal.description = data['description']
        if 'price' in data:
            meal.price = data['price']
        if 'is_available' in data:
            meal.is_available = data['is_available']
        
        meal.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Meal updated successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def delete_meal(request, meal_id):
    """Delete a meal"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        meal = get_object_or_404(Meal, id=meal_id)
        meal_name = meal.name
        meal.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Meal {meal_name} deleted successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def toggle_meal_availability(request, meal_id):
    """Toggle meal availability"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        meal = get_object_or_404(Meal, id=meal_id)
        meal.is_available = not meal.is_available
        meal.save()
        
        return JsonResponse({
            'success': True,
            'is_available': meal.is_available,
            'message': f'Meal {"made available" if meal.is_available else "made unavailable"} successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def update_platform_settings(request):
    """Update platform settings"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        data = json.loads(request.body)
        
        # Update platform settings (you can add a PlatformSettings model later)
        # For now, just return success
        return JsonResponse({
            'success': True,
            'message': 'Platform settings updated successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def update_site_info(request):
    """Update site information"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        data = json.loads(request.body)
        
        # Update site information (you can add a SiteInfo model later)
        # For now, just return success
        return JsonResponse({
            'success': True,
            'message': 'Site information updated successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["GET", "POST"])
def platform_settings(request):
    """Platform settings management"""
    if request.user.role != 'admin':
        messages.error(request, 'Admin access required.')
        return redirect('users:home')
    
    # Get or create platform settings
    settings = PlatformSettings.get_settings()
    
    if request.method == 'POST':
        form = PlatformSettingsForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Platform settings updated successfully!')
            return redirect('admin:platform_settings')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PlatformSettingsForm(instance=settings)
    
    context = {
        'form': form,
        'settings': settings,
    }
    return render(request, 'admin_panel/platform_settings.html', context)


@login_required
@require_http_methods(["POST"])
def update_platform_settings_ajax(request):
    """Update platform settings via AJAX"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        settings = PlatformSettings.get_settings()
        
        # Handle form data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            # Update settings from JSON data
            for field, value in data.items():
                if hasattr(settings, field):
                    setattr(settings, field, value)
        else:
            # Handle form data
            form = PlatformSettingsForm(request.POST, request.FILES, instance=settings)
            if form.is_valid():
                form.save()
            else:
                return JsonResponse({
                    'success': False, 
                    'error': 'Invalid form data',
                    'errors': form.errors
                })
        
        settings.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Platform settings updated successfully',
            'settings': {
                'site_name': settings.site_name,
                'site_description': settings.site_description,
                'contact_email': settings.contact_email,
                'support_phone': settings.support_phone,
                'support_email': settings.support_email,
                'company_address': settings.company_address,
                'business_hours': settings.business_hours,
                'default_delivery_fee': float(settings.default_delivery_fee),
                'free_delivery_threshold': float(settings.free_delivery_threshold),
                'tax_rate': float(settings.tax_rate),
                'allow_registration': settings.allow_registration,
                'allow_restaurant_registration': settings.allow_restaurant_registration,
                'maintenance_mode': settings.maintenance_mode,
                'facebook_url': settings.facebook_url or '',
                'twitter_url': settings.twitter_url or '',
                'instagram_url': settings.instagram_url or '',
                'meta_title': settings.meta_title,
                'meta_description': settings.meta_description,
                'meta_keywords': settings.meta_keywords,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["GET"])
def get_platform_settings(request):
    """Get current platform settings"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        settings = PlatformSettings.get_settings()
        return JsonResponse({
            'success': True,
            'settings': {
                'site_name': settings.site_name,
                'site_description': settings.site_description,
                'contact_email': settings.contact_email,
                'support_phone': settings.support_phone,
                'support_email': settings.support_email,
                'company_address': settings.company_address,
                'business_hours': settings.business_hours,
                'default_delivery_fee': float(settings.default_delivery_fee),
                'free_delivery_threshold': float(settings.free_delivery_threshold),
                'tax_rate': float(settings.tax_rate),
                'allow_registration': settings.allow_registration,
                'allow_restaurant_registration': settings.allow_restaurant_registration,
                'maintenance_mode': settings.maintenance_mode,
                'facebook_url': settings.facebook_url or '',
                'twitter_url': settings.twitter_url or '',
                'instagram_url': settings.instagram_url or '',
                'meta_title': settings.meta_title,
                'meta_description': settings.meta_description,
                'meta_keywords': settings.meta_keywords,
                'site_logo_url': settings.site_logo.url if settings.site_logo else '',
                'site_favicon_url': settings.site_favicon.url if settings.site_favicon else '',
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# Restaurant Management Endpoints
@login_required
@require_http_methods(["GET"])
@admin_required
def restaurant_list(request):
    """Get list of all restaurants with details"""
    try:
        restaurants = Restaurant.objects.select_related('owner').all()
        
        restaurant_data = []
        for restaurant in restaurants:
            # Get order count for this restaurant
            orders_count = Order.objects.filter(restaurant=restaurant).count()
            
            restaurant_data.append({
                'id': restaurant.id,
                'name': restaurant.name,
                'description': restaurant.description,
                'location': restaurant.location,
                'is_active': restaurant.is_active,
                'logo': restaurant.logo.url if restaurant.logo else None,
                'owner_name': f"{restaurant.owner.first_name} {restaurant.owner.last_name}".strip() if restaurant.owner else 'N/A',
                'owner_email': restaurant.owner.email if restaurant.owner else None,
                'orders_count': orders_count,
                'created_at': restaurant.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'restaurants': restaurant_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
@admin_required
def create_restaurant(request):
    """Create a new restaurant"""
    try:
        data = json.loads(request.body)
        
        # Check if owner email exists
        owner_email = data.get('owner_email')
        try:
            owner = User.objects.get(email=owner_email)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Owner with this email does not exist'
            })
        
        # Create restaurant
        restaurant = Restaurant.objects.create(
            name=data.get('name'),
            description=data.get('description', ''),
            location=data.get('location'),
            phone_number=data.get('phone', ''),
            delivery_time=data.get('delivery_time', ''),
            opening_hours=data.get('opening_hours', ''),
            is_active=data.get('is_active', True),
            owner=owner
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Restaurant created successfully',
            'restaurant_id': restaurant.id
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["GET"])
@admin_required
def restaurant_analytics(request):
    """Get restaurant analytics data"""
    try:
        from django.db.models import Count, Avg, Sum
        from orders.models import OrderItem
        
        # Basic counts
        total_restaurants = Restaurant.objects.count()
        active_restaurants = Restaurant.objects.filter(is_active=True).count()
        
        # Order statistics
        total_orders = Order.objects.count()
        
        # Calculate average order value
        order_items = OrderItem.objects.all()
        if order_items.exists():
            total_revenue = sum(item.price * item.quantity for item in order_items)
            avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        else:
            avg_order_value = 0
        
        # Top performing restaurants
        top_restaurants = Restaurant.objects.annotate(
            orders_count=Count('order'),
            total_revenue=Sum('order__total')
        ).order_by('-orders_count')[:5]
        
        top_restaurants_data = []
        for restaurant in top_restaurants:
            top_restaurants_data.append({
                'name': restaurant.name,
                'location': restaurant.location,
                'orders_count': restaurant.orders_count or 0,
                'revenue': float(restaurant.total_revenue or 0),
                'rating': 4.5  # Placeholder - you can add rating system later
            })
        
        return JsonResponse({
            'success': True,
            'analytics': {
                'total_restaurants': total_restaurants,
                'active_restaurants': active_restaurants,
                'total_orders': total_orders,
                'avg_order_value': round(avg_order_value, 2),
                'top_restaurants': top_restaurants_data
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
@admin_required
def bulk_toggle_restaurant_status(request):
    """Bulk toggle restaurant status"""
    try:
        data = json.loads(request.body)
        restaurant_ids = data.get('restaurant_ids', [])
        
        restaurants = Restaurant.objects.filter(id__in=restaurant_ids)
        updated_count = 0
        
        for restaurant in restaurants:
            restaurant.is_active = not restaurant.is_active
            restaurant.save()
            updated_count += 1
        
        return JsonResponse({
            'success': True,
            'message': f'Status toggled for {updated_count} restaurants'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
@admin_required
def bulk_delete_restaurants(request):
    """Bulk delete restaurants"""
    try:
        data = json.loads(request.body)
        restaurant_ids = data.get('restaurant_ids', [])
        
        restaurants = Restaurant.objects.filter(id__in=restaurant_ids)
        deleted_count = restaurants.count()
        restaurants.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{deleted_count} restaurants deleted successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
