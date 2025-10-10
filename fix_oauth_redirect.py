#!/usr/bin/env python
"""
Fix Google OAuth Redirect URI Issue
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def fix_redirect_uri():
    print("=== GOOGLE OAUTH REDIRECT URI FIX ===")
    
    print("\nCURRENT ISSUE:")
    print("Error 400: redirect_uri_mismatch")
    print("This happens when the redirect URI in Google Cloud Console doesn't match Django's callback URL")
    
    print("\nDJANGO'S EXPECTED CALLBACK URLS:")
    print("- http://127.0.0.1:8000/accounts/google/login/callback/")
    print("- http://localhost:8000/accounts/google/login/callback/")
    
    print("\n=== SOLUTION ===")
    print("You need to add these redirect URIs in Google Cloud Console:")
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Select your project")
    print("3. Go to APIs & Services > Credentials")
    print("4. Click on your OAuth 2.0 Client ID")
    print("5. In 'Authorized redirect URIs', add:")
    print("   - http://127.0.0.1:8000/accounts/google/login/callback/")
    print("   - http://localhost:8000/accounts/google/login/callback/")
    print("6. Save the changes")
    
    print("\n=== ALTERNATIVE QUICK FIX ===")
    print("Update ALLOWED_HOSTS in settings.py to use localhost instead of 127.0.0.1")

if __name__ == "__main__":
    fix_redirect_uri()