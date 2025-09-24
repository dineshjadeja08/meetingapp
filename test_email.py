#!/usr/bin/env python3
"""
Email Configuration Tester for Meeting App
"""

import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email_config():
    """Test current email configuration"""
    print("=" * 50)
    print("EMAIL CONFIGURATION TEST")
    print("=" * 50)
    
    print(f"Backend: {settings.EMAIL_BACKEND}")
    
    if 'filebased' in settings.EMAIL_BACKEND:
        print(f"File Path: {getattr(settings, 'EMAIL_FILE_PATH', 'Not set')}")
        print("📁 Emails will be saved as files in the specified directory")
        
    elif 'smtp' in settings.EMAIL_BACKEND:
        print(f"SMTP Host: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
        print(f"SMTP Port: {getattr(settings, 'EMAIL_PORT', 'Not set')}")
        print(f"Use TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}")
        print(f"Host User: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
        print("📧 Emails will be sent via SMTP")
        
    elif 'console' in settings.EMAIL_BACKEND:
        print("📺 Emails will be printed to console")
    
    print(f"From Email: {settings.DEFAULT_FROM_EMAIL}")
    print()

def send_test_email(to_email):
    """Send a test email"""
    try:
        send_mail(
            subject='Test Email from Meeting App',
            message='This is a test email to verify your email configuration is working.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False,
        )
        
        if 'filebased' in settings.EMAIL_BACKEND:
            print("✅ Test email created successfully!")
            print(f"📁 Check the '{settings.EMAIL_FILE_PATH}' directory for the email file")
        elif 'smtp' in settings.EMAIL_BACKEND:
            print("✅ Test email sent successfully!")
            print(f"📧 Check your inbox at {to_email}")
        elif 'console' in settings.EMAIL_BACKEND:
            print("✅ Test email printed to console!")
            print("📺 Check the Django server terminal for the email content")
            
        return True
        
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False

def main():
    test_email_config()
    
    # Get email address for testing
    email = input("Enter your email address to test: ").strip()
    
    if not email:
        print("❌ No email address provided")
        return
    
    print("\n🔄 Sending test email...")
    success = send_test_email(email)
    
    if success:
        print("\n" + "=" * 50)
        print("✅ EMAIL SYSTEM IS WORKING!")
        print("=" * 50)
        print("\nYou can now use the password reset feature:")
        print("1. Go to your app's login page")
        print("2. Click 'Forgot Password'")
        print("3. Enter your email address")
        
        if 'filebased' in settings.EMAIL_BACKEND:
            print("4. Check the 'tmp/app-messages' folder for the reset email")
        elif 'smtp' in settings.EMAIL_BACKEND:
            print("4. Check your email inbox for the reset link")
        else:
            print("4. Check the Django server console for the email")
            
    else:
        print("\n" + "=" * 50)
        print("❌ EMAIL SYSTEM NEEDS CONFIGURATION")
        print("=" * 50)
        print("\nRefer to EMAIL_CONFIGURATION_GUIDE.md for setup instructions")

if __name__ == "__main__":
    main()