"""
URL configuration for core project.

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
from django.urls import path, include, re_path
from django.shortcuts import redirect, render
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


def home_redirect(request):
    """Redirect to video room home"""
    if request.user.is_authenticated:
        return redirect('videoroom:dashboard')
    else:
        return redirect('videoroom:home')


def login_page(request):
    """Login page"""
    return render(request, 'accounts/login.html')


def register_page(request):
    """Register page"""
    return render(request, 'accounts/register.html')

# Swagger configuration
schema_view = get_schema_view(
   openapi.Info(
      title="Video Meeting App API",
      default_version='v1',
      description="A comprehensive API for video conferencing, meeting rooms and user authentication",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@meetingapp.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', home_redirect, name='home'),
    path('login/', login_page, name='login_page'),
    path('register/', register_page, name='register_page'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # This matches the original path
    path('api/accounts/', include('accounts.urls', namespace='api-accounts')),  # Alternative API path with namespace
    
    # Video Rooms - Google Meet style
    path('video/', include('videoroom.urls')),
    
    # Swagger documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
