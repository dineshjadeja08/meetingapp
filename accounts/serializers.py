from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration (signup)
    """
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        style={'input_type': 'password'},
        help_text="Password must be at least 8 characters long"
    )
    password2 = serializers.CharField(
        write_only=True, 
        required=True,
        style={'input_type': 'password'},
        help_text="Confirm password"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password2')
        extra_kwargs = {
            'email': {'required': True, 'help_text': 'Valid email address'},
            'username': {'help_text': 'Unique username'},
            'first_name': {'required': False, 'help_text': 'First name'},
            'last_name': {'required': False, 'help_text': 'Last name'},
        }

    def validate_email(self, value):
        """
        Validate email format and uniqueness
        """
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Enter a valid email address.")
            
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        """
        Validate username uniqueness
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate(self, attrs):
        """
        Validate that password fields match
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        """
        Create a new user with hashed password
        """
        # Remove password2 from validated_data
        validated_data.pop('password2', None)
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer with enhanced response
    """
    username_field = 'username'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Allow login with either username or email
        self.fields['username'].help_text = 'Username or email address'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['user_id'] = user.id
        token['full_name'] = f"{user.first_name} {user.last_name}".strip()
        return token

    def validate(self, attrs):
        """
        Allow authentication with username or email
        """
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            # Try to find user by username or email
            user = None
            if '@' in username:
                try:
                    user = User.objects.get(email=username)
                    username = user.username
                except User.DoesNotExist:
                    pass
            
            if user or User.objects.filter(username=username).exists():
                attrs['username'] = username
                # Let parent handle the authentication
                data = super().validate(attrs)
                
                # Add user info to response
                refresh = self.get_token(self.user)
                data['user'] = {
                    'id': self.user.id,
                    'username': self.user.username,
                    'email': self.user.email,
                    'first_name': self.user.first_name,
                    'last_name': self.user.last_name,
                }
                
                return data
            else:
                raise serializers.ValidationError('No active account found with the given credentials')
        else:
            raise serializers.ValidationError('Must include username and password')


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for password reset request
    """
    email = serializers.EmailField(
        required=True,
        help_text="Email address of the account to reset password for"
    )

    def validate_email(self, value):
        """
        Validate email format
        """
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Enter a valid email address.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation
    """
    uid = serializers.CharField(
        required=True,
        help_text="User ID from reset link"
    )
    token = serializers.CharField(
        required=True,
        help_text="Token from reset link"
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        help_text="New password"
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Confirm new password"
    )

    def validate(self, attrs):
        """
        Validate that password fields match
        """
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile with extended fields
    """
    # Profile fields
    is_email_verified = serializers.BooleanField(source='profile.is_email_verified', read_only=True)
    phone_number = serializers.CharField(source='profile.phone_number', max_length=15, required=False, allow_blank=True)
    bio = serializers.CharField(source='profile.bio', max_length=500, required=False, allow_blank=True)
    location = serializers.CharField(source='profile.location', max_length=100, required=False, allow_blank=True)
    birth_date = serializers.DateField(source='profile.birth_date', required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login',
            'is_email_verified', 'phone_number', 'bio', 'location', 'birth_date'
        )
        read_only_fields = ('id', 'username', 'date_joined', 'last_login', 'is_email_verified')
        extra_kwargs = {
            'email': {'help_text': 'Email address'},
            'first_name': {'help_text': 'First name'},
            'last_name': {'help_text': 'Last name'},
            'phone_number': {'help_text': 'Phone number'},
            'bio': {'help_text': 'Biography'},
            'location': {'help_text': 'Location'},
            'birth_date': {'help_text': 'Birth date (YYYY-MM-DD)'},
        }

    def validate_email(self, value):
        """
        Validate email uniqueness (excluding current user)
        """
        if User.objects.filter(email=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def update(self, instance, validated_data):
        """
        Update user and profile data
        """
        # Extract profile data
        profile_data = validated_data.pop('profile', {})
        
        # Update user instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update profile instance
        if profile_data and hasattr(instance, 'profile'):
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        return instance
