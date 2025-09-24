from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    UserRegistrationSerializer, 
    CustomTokenObtainPairSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    UserProfileSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token obtain view with enhanced response
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        tags=['Authentication'],
        operation_summary="User Sign In",
        operation_description="Sign in with username/email and password to get JWT tokens",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username or email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            },
            required=['username', 'password']
        ),
        responses={
            200: openapi.Response(
                description="Successfully signed in",
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
                            }
                        )
                    }
                )
            ),
            401: "Invalid credentials"
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            if response.status_code == 200:
                logger.info(f"User signed in successfully: {request.data.get('username')}")
            return response
        except Exception as e:
            logger.error(f"Sign in error: {str(e)}")
            return Response(
                {'error': 'Authentication failed'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )


class UserRegistrationView(APIView):
    """
    View to handle user registration (Sign Up)
    """
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        tags=['Authentication'],
        operation_summary="User Sign Up",
        operation_description="Register a new user account. After registration, use the login endpoint to get JWT tokens.",
        request_body=UserRegistrationSerializer,
        responses={
            201: openapi.Response(
                description="User registered successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Success message"
                        ),
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'username': openapi.Schema(type=openapi.TYPE_STRING),
                                'email': openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        )
                    }
                )
            ),
            400: "Validation errors"
        }
    )
    def post(self, request):
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                
                logger.info(f"New user registered: {user.username}")
                
                return Response({
                    'message': 'User registered successfully! Please login to get your access tokens.',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                    }
                }, status=status.HTTP_201_CREATED)
            
            logger.warning(f"Registration validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response(
                {'error': 'Registration failed. Please try again.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PasswordResetRequestView(APIView):
    """
    View to handle password reset requests
    """
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        tags=['Authentication'],
        operation_summary="Request Password Reset",
        operation_description="Request a password reset link via email",
        request_body=PasswordResetRequestSerializer,
        responses={
            200: openapi.Response(
                description="Password reset email sent (if account exists)",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Success message"
                        )
                    }
                )
            ),
            400: "Email is required"
        }
    )
    def post(self, request):
        try:
            serializer = PasswordResetRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                # NOTE: Change to your frontend URL
                reset_url = f"http://localhost:3000/password-reset-confirm?uid={uid}&token={token}"
                
                # Create email content
                email_context = {
                    'user': user,
                    'reset_url': reset_url,
                }
                
                # HTML email content
                html_content = render_to_string('accounts/password_reset_email.html', email_context)
                
                # Plain text fallback
                text_content = f"""
Hello {user.first_name or user.username},

You requested a password reset for your Meeting App account.

Reset your password by clicking this link: {reset_url}

This link will expire in 24 hours for security reasons.

If you didn't request this password reset, please ignore this email.

Best regards,
The Meeting App Team
                """.strip()
                
                send_mail(
                    'Password Reset Request - Meeting App',
                    text_content,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=html_content,
                    fail_silently=False,
                )
                
                logger.info(f"Password reset email sent to: {email}")
                
            except User.DoesNotExist:
                logger.warning(f"Password reset requested for non-existent email: {email}")
                # Still return success for security reasons
                pass
            
            return Response({
                "message": "If an account with that email exists, a password reset link has been sent."
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Password reset request error: {str(e)}")
            return Response(
                {'error': 'Unable to process password reset request'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PasswordResetConfirmView(APIView):
    """
    View to handle password reset confirmation
    """
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        tags=['Authentication'],
        operation_summary="Confirm Password Reset",
        operation_description="Confirm password reset with token and set new password",
        request_body=PasswordResetConfirmSerializer,
        responses={
            200: openapi.Response(
                description="Password reset successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Success message"
                        )
                    }
                )
            ),
            400: "Invalid token or missing fields"
        }
    )
    def post(self, request):
        try:
            serializer = PasswordResetConfirmSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            uidb64 = serializer.validated_data['uid']
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                logger.warning(f"Invalid UID in password reset: {uidb64}")
                return Response(
                    {"error": "The reset link is invalid or has expired."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                
                logger.info(f"Password reset successful for user: {user.username}")
                
                return Response({
                    "message": "Password has been reset successfully."
                }, status=status.HTTP_200_OK)
            else:
                logger.warning(f"Invalid token in password reset for user: {user.username}")
                return Response(
                    {"error": "The reset link is invalid or has expired."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Password reset confirmation error: {str(e)}")
            return Response(
                {'error': 'Unable to reset password'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserProfileView(APIView):
    """
    View to get and update user profile
    """
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        tags=['User Profile'],
        operation_summary="Get User Profile",
        operation_description="Get current user's profile information",
        responses={
            200: UserProfileSerializer,
            401: "Authentication required"
        }
    )
    def get(self, request):
        try:
            serializer = UserProfileSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Get profile error: {str(e)}")
            return Response(
                {'error': 'Unable to fetch profile'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        tags=['User Profile'],
        operation_summary="Update User Profile",
        operation_description="Update current user's profile information",
        request_body=UserProfileSerializer,
        responses={
            200: UserProfileSerializer,
            400: "Validation errors",
            401: "Authentication required"
        }
    )
    def patch(self, request):
        try:
            serializer = UserProfileSerializer(
                request.user, 
                data=request.data, 
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Profile updated for user: {request.user.username}")
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Update profile error: {str(e)}")
            return Response(
                {'error': 'Unable to update profile'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )