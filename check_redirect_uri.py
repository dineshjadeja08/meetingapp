#!/usr/bin/env python
"""
Check OAuth Redirect URI Configuration
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import RequestFactory
from allauth.socialaccount.providers.google.views import GoogleOAuth2LoginView

def check_redirect_uri():
    print("=== OAUTH REDIRECT URI DEBUG ===")
    
    # Create a test request
    factory = RequestFactory()
    request = factory.get('/accounts/google/login/')
    request.META['HTTP_HOST'] = '127.0.0.1:8000'
    
    # Get the Google OAuth view
    view = GoogleOAuth2LoginView()
    view.request = request
    
    try:
        # Get the adapter and provider
        adapter = view.get_adapter()
        provider = adapter.get_provider()
        
        # Get the authorization URL that would be generated
        print(f"Provider ID: {provider.id}")
        print(f"Provider Name: {provider.name}")
        
        # Check what redirect URI Django would use
        from allauth.socialaccount.providers.oauth2.client import OAuth2Client
        
        # Get the callback URL that Django generates
        callback_url = adapter.get_callback_url(request, None)
        print(f"Django Generated Callback URL: {callback_url}")
        
        print("\n=== REQUIRED REDIRECT URIS FOR GOOGLE CONSOLE ===")
        print("You need to add these redirect URIs in Google Cloud Console:")
        print("1. http://127.0.0.1:8000/accounts/google/login/callback/")
        print("2. http://localhost:8000/accounts/google/login/callback/")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_redirect_uri()