from django.http import JsonResponse, HttpResponseRedirect
from django.views import View
from django.contrib.auth import login
from django.urls import reverse
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from allauth.socialaccount.models import SocialAccount
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import json


class GoogleOAuthTokenView(APIView):
    """
    Get JWT tokens for authenticated OAuth user
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        tags=['Authentication'],
        operation_summary="Get JWT Tokens for OAuth User",
        operation_description="Get JWT tokens after successful OAuth authentication",
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'username': openapi.Schema(type=openapi.TYPE_STRING),
                                'email': openapi.Schema(type=openapi.TYPE_STRING),
                                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                                'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        )
                    }
                )
            ),
            400: openapi.Response(description="Authentication failed")
        }
    )
    def post(self, request):
        """
        Generate JWT tokens for authenticated user
        """
        user = request.user
        
        if user.is_authenticated:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Get user profile data
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'profile': {
                    'full_name': user.profile.full_name if hasattr(user, 'profile') else user.username,
                    'is_email_verified': user.profile.is_email_verified if hasattr(user, 'profile') else True,
                }
            }
            
            # Return JSON response with tokens
            response_data = {
                'message': 'Google authentication successful',
                'access': str(access_token),
                'refresh': str(refresh),
                'user': user_data
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(
            {'error': 'Authentication required'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class GoogleOAuthInitView(APIView):
    """
    Initiate Google OAuth flow
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        tags=['Authentication'],
        operation_summary="Initiate Google OAuth",
        operation_description="Get Google OAuth authorization URL",
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'auth_url': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            )
        }
    )
    def get(self, request):
        """
        Return Google OAuth URL
        """
        from allauth.socialaccount.providers.google.urls import urlpatterns
        from django.urls import reverse
        
        # Build the Google OAuth URL
        google_login_url = request.build_absolute_uri(
            '/accounts/google/login/'
        )
        
        return Response({
            'auth_url': google_login_url,
            'message': 'Redirect to this URL to start Google OAuth flow'
        })


class SocialAccountStatusView(APIView):
    """
    Check if user has connected social accounts
    """
    
    @swagger_auto_schema(
        tags=['Authentication'],
        operation_summary="Social Account Status",
        operation_description="Check connected social accounts for authenticated user",
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'google_connected': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'social_accounts': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT)
                        ),
                    }
                )
            )
        }
    )
    def get(self, request):
        """
        Get social account status
        """
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check for connected Google account
        google_account = SocialAccount.objects.filter(
            user=request.user,
            provider='google'
        ).first()
        
        social_accounts = []
        if google_account:
            social_accounts.append({
                'provider': 'google',
                'email': google_account.extra_data.get('email'),
                'name': google_account.extra_data.get('name'),
                'connected_at': google_account.date_joined
            })
        
        return Response({
            'google_connected': bool(google_account),
            'social_accounts': social_accounts
        })