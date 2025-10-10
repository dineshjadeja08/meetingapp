#!/usr/bin/env python
"""
Debug OAuth Configuration
Run this script to diagnose OAuth setup issues
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from allauth.socialaccount.providers.google.provider import GoogleProvider
from allauth.socialaccount import app_settings

def debug_oauth():
    print("=== OAUTH DEBUG ANALYSIS ===")
    
    # Check all social apps
    print(f"\n1. ALL SOCIAL APPS:")
    apps = SocialApp.objects.all()
    for app in apps:
        print(f"   ID: {app.id}, Provider: {app.provider}, Name: {app.name}")
        print(f"   Client ID: {app.client_id}")
        print(f"   Sites: {[s.domain for s in app.sites.all()]}")
        print()
    
    # Check Google apps specifically
    print(f"\n2. GOOGLE APPS:")
    google_apps = SocialApp.objects.filter(provider='google')
    print(f"   Count: {google_apps.count()}")
    for app in google_apps:
        print(f"   ID: {app.id}, Name: {app.name}, Sites: {len(app.sites.all())}")
    
    # Check site configuration
    print(f"\n3. SITE CONFIGURATION:")
    current_site = Site.objects.get_current()
    print(f"   Current Site ID: {current_site.id}")
    print(f"   Current Site Domain: {current_site.domain}")
    print(f"   Current Site Name: {current_site.name}")
    
    all_sites = Site.objects.all()
    print(f"   Total Sites: {all_sites.count()}")
    for site in all_sites:
        print(f"     Site {site.id}: {site.domain} ({site.name})")
    
    # Check app settings
    print(f"\n4. ALLAUTH SETTINGS:")
    print(f"   SITE_ID: {getattr(django.conf.settings, 'SITE_ID', 'Not set')}")
    print(f"   SOCIALACCOUNT_PROVIDERS: {app_settings.PROVIDERS}")
    
    # Test provider lookup
    print(f"\n5. PROVIDER LOOKUP TEST:")
    try:
        from allauth.socialaccount.providers import registry
        provider = registry.by_id('google')
        print(f"   Google Provider: {provider}")
        
        # Test app lookup for current site
        from allauth.socialaccount.adapter import get_adapter
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/test/')
        adapter = get_adapter(request)
        
        # This is where the error occurs - try to get Google app
        try:
            app = adapter.get_app(request, provider='google')
            print(f"   Successfully found app: {app}")
        except Exception as e:
            print(f"   ERROR getting app: {e}")
            print(f"   Error type: {type(e)}")
            
    except Exception as e:
        print(f"   ERROR in provider lookup: {e}")

if __name__ == "__main__":
    debug_oauth()