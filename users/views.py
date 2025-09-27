from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django import forms
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import re
from .models import User
from restaurants.models import Restaurant
from orders.models import Order


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.role = 'customer'  # Set default role
        if commit:
            user.save()
        return user


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    form = CustomUserCreationForm()  # Initialize form at the beginning
    
    if request.method == 'POST':
        # Check if it's a login form or registration form
        if 'username' in request.POST and 'password' in request.POST and 'login-email' not in request.POST:
            # Login form
            username_or_email = request.POST['username']
            password = request.POST['password']
            
            # Try to authenticate with username first
            user = authenticate(request, username=username_or_email, password=password)
            
            # If username authentication fails, try email authentication
            if user is None:
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None
            
            if user is not None:
                login(request, user)
                # Redirect based on role
                if user.role == 'customer':
                    return redirect('meals:meal_list')
                elif user.role == 'owner':
                    return redirect('restaurants:restaurant_dashboard')
                elif user.role == 'admin':
                    return redirect('users:simple_admin_dashboard')
                elif user.role == 'delivery':
                    return redirect('orders:delivery_dashboard')
            else:
                messages.error(request, 'Invalid username/email or password.')
        elif 'reg-email' in request.POST or 'email' in request.POST:
            # Registration form
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Registration successful! Please log in.')
                return redirect('users:login')
            else:
                messages.error(request, 'Registration failed. Please check your information.')

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('users:login')


@login_required
def profile_view(request):
    return render(request, 'users/profile.html', {'user': request.user})


def home_view(request):
    return render(request, 'users/home.html')


@login_required
def admin_dashboard_view(request):
    """Full admin dashboard with detailed management"""
    if request.user.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('users:home')
    
    # Get statistics
    total_users = User.objects.count()
    total_restaurants = Restaurant.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Get recent data
    users = User.objects.all()[:10]
    recent_orders = Order.objects.select_related('user', 'restaurant').order_by('-created_at')[:10]
    
    context = {
        'total_users': total_users,
        'total_restaurants': total_restaurants,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'users': users,
        'recent_orders': recent_orders,
    }
    return render(request, 'users/admin_dashboard.html', context)


@login_required
def simple_admin_dashboard_view(request):
    """Simple admin dashboard with basic overview"""
    if request.user.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('users:home')
    
    # Get statistics
    total_users = User.objects.count()
    total_restaurants = Restaurant.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Get recent data
    users = User.objects.all()[:10]
    recent_orders = Order.objects.select_related('user', 'restaurant').order_by('-created_at')[:5]
    
    context = {
        'total_users': total_users,
        'total_restaurants': total_restaurants,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'users': users,
        'recent_orders': recent_orders,
    }
    return render(request, 'users/simple_admin_dashboard.html', context)


def business_registration_view(request):
    """Business registration for restaurant owners"""
    if request.method == 'POST':
        # Create user account
        username = request.POST.get('email')  # Use email as username
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        full_name = request.POST.get('full_name', '')
        restaurant_name = request.POST.get('restaurant_name', '')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        location = request.POST.get('location', '')
        logo_url = request.POST.get('logo_url', '')
        cuisine_type = request.POST.get('cuisine_type', '')
        description = request.POST.get('description', '')
        opening_time = request.POST.get('opening_time', '09:00')
        closing_time = request.POST.get('closing_time', '21:00')
        
        # Validate passwords match
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'users/business_registration.html')
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'users/business_registration.html')
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                role='owner',
                first_name=full_name.split()[0] if full_name else '',
                last_name=' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else ''
            )
            
            # Create restaurant
            if restaurant_name:
                Restaurant.objects.create(
                    name=restaurant_name,
                    description=description,
                    owner=user,
                    location=address or location
                )
            
            messages.success(request, 'Business registration successful! Please log in.')
            return redirect('users:login')
            
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
    
    return render(request, 'users/business_registration.html')


@csrf_exempt
@require_http_methods(["POST"])
def validate_email(request):
    """AJAX endpoint to validate email format and availability"""
    email = request.POST.get('email', '').strip()
    
    if not email:
        return JsonResponse({
            'valid': False,
            'message': 'Email is required',
            'status': 'error'
        })
    
    # Check email format
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return JsonResponse({
            'valid': False,
            'message': 'Please enter a valid email address',
            'status': 'error'
        })
    
    # Check if email already exists
    if User.objects.filter(email=email).exists():
        return JsonResponse({
            'valid': False,
            'message': 'This email is already registered',
            'status': 'error'
        })
    
    # Email is valid and available
    return JsonResponse({
        'valid': True,
        'message': 'Email is available',
        'status': 'success'
    })


@csrf_exempt
@require_http_methods(["POST"])
def validate_restaurant_name(request):
    """AJAX endpoint to validate restaurant name availability"""
    restaurant_name = request.POST.get('restaurant_name', '').strip()
    
    if not restaurant_name:
        return JsonResponse({
            'valid': False,
            'message': 'Restaurant name is required',
            'status': 'error'
        })
    
    # Check if restaurant name already exists (case-insensitive)
    if Restaurant.objects.filter(name__iexact=restaurant_name).exists():
        return JsonResponse({
            'valid': False,
            'message': 'This restaurant name is already taken',
            'status': 'error'
        })
    
    # Restaurant name is available
    return JsonResponse({
        'valid': True,
        'message': 'Restaurant name is available',
        'status': 'success'
    })
