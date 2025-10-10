#!/usr/bin/env python
"""
Test script to verify Google OAuth setup
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.urls import reverse
from django.test import RequestFactory

def test_google_oauth_setup():
    """Test Google OAuth configuration"""
    print("🔍 Testing Google OAuth Setup...")
    print("=" * 50)
    
    # Check if allauth is properly installed
    try:
        import allauth
        print("✅ django-allauth is installed:", allauth.__version__)
    except ImportError:
        print("❌ django-allauth is not installed")
        return False
    
    # Check if Google provider is available
    try:
        from allauth.socialaccount.providers.google import provider
        print("✅ Google provider is available")
    except ImportError:
        print("❌ Google provider is not available")
        return False
    
    # Check URL configuration
    try:
        google_login_url = reverse('google_oauth2_login')
        print(f"✅ Google OAuth login URL: {google_login_url}")
    except:
        print("❌ Google OAuth URLs not properly configured")
    
    try:
        google_callback_url = reverse('google_oauth2_callback')  
        print(f"✅ Google OAuth callback URL: {google_callback_url}")
    except:
        print("❌ Google OAuth callback URL not found")
    
    # Check Site configuration
    try:
        site = Site.objects.get(pk=1)
        print(f"✅ Default site configured: {site.domain}")
    except Site.DoesNotExist:
        print("❌ Default site not configured")
    
    # Check for Google OAuth app
    google_apps = SocialApp.objects.filter(provider='google')
    if google_apps.exists():
        app = google_apps.first()
        print(f"✅ Google OAuth app found: {app.name}")
        print(f"   Client ID: {app.client_id[:20]}...")
        print(f"   Sites: {', '.join([s.domain for s in app.sites.all()])}")
        
        if not app.client_id or not app.secret:
            print("❌ Google OAuth app missing credentials")
            return False
    else:
        print("⚠️  No Google OAuth app configured yet")
        print("   Use Django admin or run: python manage.py setup_google_oauth --client-id 'your-id' --client-secret 'your-secret'")
        return False
    
    print("\n🎉 Google OAuth setup verification completed!")
    return True

def print_setup_instructions():
    """Print setup instructions"""
    print("\n📋 Setup Instructions:")
    print("=" * 50)
    print("1. Google Cloud Console:")
    print("   - Go to https://console.cloud.google.com/")
    print("   - Create OAuth 2.0 credentials")
    print("   - Add redirect URI: http://localhost:8000/accounts/google/login/callback/")
    print("\n2. Configure Django:")
    print("   - Visit: http://localhost:8000/admin/")
    print("   - Add Social Application (Google)")
    print("   - Or run: python manage.py setup_google_oauth --client-id 'your-id' --client-secret 'your-secret'")
    print("\n3. Test OAuth:")
    print("   - Visit: http://localhost:8000/login/")
    print("   - Click 'Continue with Google'")

if __name__ == '__main__':
    is_configured = test_google_oauth_setup()
    if not is_configured:
        print_setup_instructions()