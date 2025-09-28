"""
URL configuration for Food_Ordering_Platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from .admin import admin_site

def redirect_to_home(request):
    return redirect('users:home')

urlpatterns = [
    path('admin/', admin_site.urls),  # Use custom admin site
    path("admin-api/", include("admin_panel.urls", namespace="admin")),  # Admin API endpoints
    path("", redirect_to_home, name="home"),
    path("users/", include("users.urls", namespace="users")),
    path("meals/", include("meals.urls", namespace="meals")),
    path("orders/", include("orders.urls", namespace="orders")),
    path("restaurants/", include("restaurants.urls", namespace="restaurants")),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
