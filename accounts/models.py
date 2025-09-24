from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    """
    Extended user profile model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_email_verified = models.BooleanField(default=False, help_text='Email verification status')
    phone_number = models.CharField(max_length=15, blank=True, help_text='Phone number')
    bio = models.TextField(max_length=500, blank=True, help_text='Bio')
    location = models.CharField(max_length=100, blank=True, help_text='Location')
    birth_date = models.DateField(null=True, blank=True, help_text='Birth date')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def full_name(self):
        """Returns the user's full name"""
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
