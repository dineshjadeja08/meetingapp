#!/usr/bin/env python
"""
Google OAuth Configuration Status Check
"""
import os
import sys
import django
from urllib.parse import urlparse

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.urls import reverse, NoReverseMatch
from django.conf import settings

def check_google_oauth_config():
    """Check complete Google OAuth configuration"""
    print("🔍 Google OAuth Configuration Status")
    print("=" * 50)
    
    status = {
        'allauth_installed': False,
        'google_provider': False,
        'urls_configured': False,
        'site_configured': False,
        'oauth_app': False,
        'settings_ok': False
    }
    
    # 1. Check allauth installation
    try:
        import allauth
        print(f"✅ django-allauth: {allauth.__version__}")
        status['allauth_installed'] = True
    except ImportError:
        print("❌ django-allauth not installed")
        return status
    
    # 2. Check Google provider
    try:
        from allauth.socialaccount.providers.google import provider
        print("✅ Google provider: Available")
        status['google_provider'] = True
    except ImportError:
        print("❌ Google provider not available")
        return status
    
    # 3. Check URL configuration
    try:
        login_url = reverse('google_oauth2_login')
        callback_url = reverse('google_oauth2_callback')
        print(f"✅ URLs configured:")
        print(f"   Login: {login_url}")
        print(f"   Callback: {callback_url}")
        status['urls_configured'] = True
    except NoReverseMatch as e:
        print(f"⚠️  URL configuration: {e}")
        # Check if our custom URLs work
        try:
            custom_init = reverse('google_oauth_init')
            custom_token = reverse('google_oauth_token')
            print(f"✅ Custom OAuth URLs:")
            print(f"   Init: {custom_init}")
            print(f"   Token: {custom_token}")
        except:
            pass
    
    # 4. Check Site configuration
    try:
        site = Site.objects.get(pk=1)
        print(f"✅ Site configured: {site.domain} ({site.name})")
        status['site_configured'] = True
    except Site.DoesNotExist:
        print("❌ Default site not found")
    
    # 5. Check Social Application
    google_apps = SocialApp.objects.filter(provider='google')
    if google_apps.exists():
        app = google_apps.first()
        print(f"✅ Google OAuth App: {app.name}")
        print(f"   Client ID: {app.client_id[:20]}...")
        print(f"   Secret: {'*' * min(len(app.secret), 20)}")
        
        # Check sites association
        app_sites = app.sites.all()
        if app_sites:
            print(f"   Sites: {', '.join([s.domain for s in app_sites])}")
        else:
            print("   ⚠️  No sites associated")
        
        if app.client_id and app.secret and app_sites:
            status['oauth_app'] = True
        else:
            print("   ❌ Incomplete configuration")
    else:
        print("❌ No Google OAuth app configured")
    
    # 6. Check Django settings
    print(f"\n📋 Django Settings:")
    print(f"   LOGIN_REDIRECT_URL: {getattr(settings, 'LOGIN_REDIRECT_URL', 'Not set')}")
    print(f"   SITE_ID: {getattr(settings, 'SITE_ID', 'Not set')}")
    
    # Check SOCIALACCOUNT_PROVIDERS
    providers = getattr(settings, 'SOCIALACCOUNT_PROVIDERS', {})
    google_config = providers.get('google', {})
    if google_config:
        print("✅ SOCIALACCOUNT_PROVIDERS configured")
        scopes = google_config.get('SCOPE', [])
        print(f"   Scopes: {', '.join(scopes)}")
        status['settings_ok'] = True
    else:
        print("❌ SOCIALACCOUNT_PROVIDERS not configured")
    
    return status

def print_test_urls():
    """Print test URLs"""
    print(f"\n🧪 Test URLs:")
    print("=" * 50)
    print("http://localhost:8000/login/                    - Login page with Google OAuth")
    print("http://localhost:8000/register/                 - Registration with Google OAuth")
    print("http://localhost:8000/accounts/google/login/    - Direct Google OAuth")
    print("http://localhost:8000/admin/                    - Django admin")
    print("http://localhost:8000/api/accounts/auth/google/init/ - Custom OAuth init")

def print_next_steps(status):
    """Print next steps based on configuration status"""
    print(f"\n📋 Next Steps:")
    print("=" * 50)
    
    if not status['oauth_app']:
        print("1. 🔧 Configure Google OAuth App:")
        print("   python manage.py setup_google_oauth --client-id 'your-id' --client-secret 'your-secret'")
    
    if status['oauth_app']:
        print("1. ✅ Google OAuth is configured!")
        print("2. 🧪 Test the integration:")
        print("   - Visit: http://localhost:8000/login/")
        print("   - Click 'Continue with Google'")
        print("   - Complete OAuth flow")
    
    print("\n3. 📝 Google Console Requirements:")
    print("   Redirect URI: http://localhost:8000/accounts/google/login/callback/")

if __name__ == '__main__':
    status = check_google_oauth_config()
    print_test_urls()
    print_next_steps(status)
    
    # Overall status
    working_components = sum(status.values())
    total_components = len(status)
    
    print(f"\n🎯 Overall Status: {working_components}/{total_components} components working")
    
    if working_components == total_components:
        print("🎉 Google OAuth is fully configured and ready!")
    elif working_components >= 4:
        print("⚠️  Google OAuth is mostly configured, minor issues to fix")
    else:
        print("❌ Google OAuth needs configuration")