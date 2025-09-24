# Meeting App API Documentation

This document provides comprehensive information about the Meeting App authentication system with JWT tokens and Swagger documentation.

## Features Implemented

### 1. User Authentication System
- **Sign Up (Registration)**: Create new user accounts with email validation
- **Sign In (Login)**: Authenticate users and receive JWT tokens  
- **Logout**: Blacklist JWT tokens for secure logout
- **Password Reset**: Request and confirm password reset via email

### 2. User Profile Management
- **View Profile**: Get current user's profile information
- **Update Profile**: Update user profile details including extended fields

### 3. JWT Token Management
- **Access Tokens**: Short-lived tokens for API authentication
- **Refresh Tokens**: Long-lived tokens for obtaining new access tokens
- **Token Blacklisting**: Secure logout by blacklisting tokens

### 4. API Documentation
- **Swagger UI**: Interactive API documentation
- **ReDoc**: Alternative API documentation interface

## API Endpoints

### Authentication Endpoints

#### 1. User Registration (Sign Up)
```
POST /api/accounts/auth/register/
Content-Type: application/json

{
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "secure_password123",
    "password2": "secure_password123"
}
```

**Response (201 Created):**
```json
{
    "message": "User registered successfully! Please login to get your access tokens.",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com"
    }
}
```

**Note:** Registration no longer provides JWT tokens. Users must login separately to receive tokens.

#### 2. User Login (Sign In)
```
POST /api/accounts/auth/login/
Content-Type: application/json

{
    "username": "john_doe",  // Can use username or email
    "password": "secure_password123"
}
```

**Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe"
    }
}
```

#### 3. Token Refresh
```
POST /api/accounts/auth/token/refresh/
Content-Type: application/json

{    
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 4. Logout
```
POST /api/accounts/auth/logout/
Content-Type: application/json
Authorization: Bearer <access_token>

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 5. Password Reset Request
```
POST /api/accounts/auth/password-reset/
Content-Type: application/json

{
    "email": "john@example.com"
}
```

**Response (200 OK):**
```json
{
    "message": "If an account with that email exists, a password reset link has been sent."
}
```

#### 6. Password Reset Confirm
```
POST /api/accounts/auth/password-reset/confirm/
Content-Type: application/json

{
    "uid": "encoded_user_id",
    "token": "reset_token",
    "new_password": "new_secure_password123",
    "confirm_password": "new_secure_password123"
}
```

### Profile Endpoints

#### 1. Get User Profile
```
GET /api/accounts/profile/
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2025-09-24T11:30:00Z",
    "last_login": "2025-09-24T11:35:00Z",
    "is_email_verified": false,
    "phone_number": "",
    "bio": "",
    "location": "",
    "birth_date": null
}
```

#### 2. Update User Profile
```
PATCH /api/accounts/profile/
Content-Type: application/json
Authorization: Bearer <access_token>

{
    "first_name": "John",
    "last_name": "Smith",
    "phone_number": "+1234567890",
    "bio": "Software Developer",
    "location": "New York, NY"
}
```

## Authentication

All protected endpoints require JWT authentication:

```
Authorization: Bearer <access_token>
```

### Token Lifecycle
- **Access Token**: Valid for 60 minutes
- **Refresh Token**: Valid for 1 day
- **Token Rotation**: Enabled (new refresh token issued on refresh)
- **Blacklisting**: Enabled (tokens blacklisted on logout)

## API Documentation URLs

### Swagger UI (Interactive)
```
http://localhost:8000/swagger/
```

### ReDoc (Alternative)
```
http://localhost:8000/redoc/
```

### JSON Schema
```
http://localhost:8000/swagger.json
```

## Error Handling

All endpoints return standardized error responses:

### Validation Errors (400 Bad Request)
```json
{
    "field_name": ["Error message"]
}
```

### Authentication Errors (401 Unauthorized)
```json
{
    "error": "Authentication failed"
}
```

### Server Errors (500 Internal Server Error)
```json
{
    "error": "Error description"
}
```

## Security Features

1. **Password Validation**: Django's built-in password validators
2. **Email Uniqueness**: Ensures unique email addresses
3. **Token Blacklisting**: Secure logout functionality
4. **CORS**: Configured for frontend integration
5. **Email Templates**: HTML email for password reset

## Development Setup

### 1. Start the Development Server
```bash
cd "c:\Users\RDJ\Desktop\meetapp\meetingapp"
C:/Users/RDJ/Desktop/meetapp/meetingapp/venv/Scripts/python.exe manage.py runserver
```

### 2. Access API Documentation
- Swagger UI: http://localhost:8000/swagger/
- Admin Panel: http://localhost:8000/admin/
  - Username: admin
  - Password: admin123

### 3. Test with Frontend
Configure your frontend to use these endpoints with the base URL:
```
http://localhost:8000/api/accounts/
```

## Email Configuration

Currently configured for development (console backend). For production:

1. Update `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

2. Update password reset URL in views to match your frontend:
```python
reset_url = f"http://your-frontend.com/password-reset-confirm?uid={uid}&token={token}"
```

## Database Models

### User (Django's built-in)
- username (unique)
- email (unique)
- first_name
- last_name
- password
- is_active
- is_staff
- date_joined
- last_login

### UserProfile (Extended)
- user (OneToOne with User)
- is_email_verified
- phone_number
- bio
- location
- birth_date
- created_at
- updated_at

## Testing Examples

### Using curl:

#### Register a new user:
```bash
curl -X POST http://localhost:8000/api/accounts/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password2": "testpass123"
  }'
```

#### Login:
```bash
curl -X POST http://localhost:8000/api/accounts/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

#### Get profile (replace ACCESS_TOKEN):
```bash
curl -X GET http://localhost:8000/api/accounts/profile/ \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

## Next Steps

1. **Email Verification**: Add email verification flow
2. **Social Authentication**: Add Google/Facebook login
3. **Rate Limiting**: Add API rate limiting
4. **User Roles**: Add role-based permissions
5. **2FA**: Add two-factor authentication
6. **Password Policies**: Enhanced password requirements

This implementation provides a robust foundation for user authentication in your Meeting App with comprehensive API documentation and security features.