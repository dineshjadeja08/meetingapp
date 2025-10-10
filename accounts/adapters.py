from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile

User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom social account adapter to handle Google OAuth integration
    """
    
    def save_user(self, request, sociallogin, form=None):
        """
        Custom user save method for social accounts
        """
        user = super().save_user(request, sociallogin, form)
        
        # Create or update user profile
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'is_email_verified': True}  # Social accounts are pre-verified
        )
        
        if not created and not profile.is_email_verified:
            profile.is_email_verified = True
            profile.save()
        
        return user
    
    def pre_social_login(self, request, sociallogin):
        """
        Handle existing user linking
        """
        # If user exists with same email, connect the accounts
        if sociallogin.account.provider == 'google':
            try:
                existing_user = User.objects.get(
                    email=sociallogin.account.extra_data['email']
                )
                if not sociallogin.is_existing:
                    sociallogin.connect(request, existing_user)
            except User.DoesNotExist:
                pass


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom account adapter for regular account handling
    """
    
    def save_user(self, request, user, form, commit=True):
        """
        Custom user save method
        """
        user = super().save_user(request, user, form, commit)
        
        if commit:
            # Create user profile if it doesn't exist
            UserProfile.objects.get_or_create(user=user)
        
        return user