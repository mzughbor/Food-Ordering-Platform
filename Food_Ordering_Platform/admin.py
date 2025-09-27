from django.contrib import admin
from django.db.models import Count, Sum, Q
from django.utils.html import format_html
from django.urls import reverse
from django.template.response import TemplateResponse
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin import AdminSite
from django.utils.safestring import mark_safe

# Custom admin site
class FoodOrderingAdminSite(AdminSite):
    site_header = "Food Ordering Platform Administration"
    site_title = "Food Ordering Admin"
    index_title = "Welcome to Food Ordering Platform Administration"
    
    def index(self, request, extra_context=None):
        """
        Display the main admin index page with statistics
        """
        from users.models import User
        from restaurants.models import Restaurant
        from meals.models import Meal
        from orders.models import Order, OrderItem
        
        # Get statistics
        stats = {
            'total_users': User.objects.count(),
            'total_customers': User.objects.filter(role='customer').count(),
            'total_owners': User.objects.filter(role='owner').count(),
            'total_restaurants': Restaurant.objects.count(),
            'total_meals': Meal.objects.count(),
            'available_meals': Meal.objects.filter(is_available=True).count(),
            'total_orders': Order.objects.count(),
            'pending_orders': Order.objects.filter(status='pending').count(),
            'confirmed_orders': Order.objects.filter(status='confirmed').count(),
            'delivered_orders': Order.objects.filter(status='delivered').count(),
            'cancelled_orders': Order.objects.filter(status='cancelled').count(),
        }
        
        # Calculate total revenue
        total_revenue = OrderItem.objects.filter(
            order__status__in=['confirmed', 'delivered']
        ).aggregate(total=Sum('price'))['total'] or 0
        stats['total_revenue'] = total_revenue
        
        # Recent orders
        recent_orders = Order.objects.select_related('user', 'restaurant').order_by('-created_at')[:10]
        
        # Top restaurants by order count
        top_restaurants = Restaurant.objects.annotate(
            order_count=Count('orders')
        ).order_by('-order_count')[:5]
        
        # Top meals by order count
        top_meals = Meal.objects.annotate(
            order_count=Count('orderitem')
        ).order_by('-order_count')[:5]
        
        context = {
            'stats': stats,
            'recent_orders': recent_orders,
            'top_restaurants': top_restaurants,
            'top_meals': top_meals,
        }
        
        if extra_context:
            context.update(extra_context)
            
        return TemplateResponse(request, 'admin/index.html', context)

# Create custom admin site instance
admin_site = FoodOrderingAdminSite(name='food_ordering_admin')

# Register models with custom admin site
from users.models import User
from restaurants.models import Restaurant
from meals.models import Meal
from orders.models import Order, OrderItem

# Import admin classes
from users.admin import CustomUserAdmin
from restaurants.admin import RestaurantAdmin
from meals.admin import MealAdmin
from orders.admin import OrderAdmin, OrderItemAdmin

# Register with custom admin site
admin_site.register(User, CustomUserAdmin)
admin_site.register(Restaurant, RestaurantAdmin)
admin_site.register(Meal, MealAdmin)
admin_site.register(Order, OrderAdmin)
admin_site.register(OrderItem, OrderItemAdmin)
