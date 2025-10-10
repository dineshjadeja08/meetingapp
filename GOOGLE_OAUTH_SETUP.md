# Google OAuth Configuration Guide

## 1. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API" and enable it
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Select "Web application"
   - Add authorized redirect URIs:
     - `http://localhost:8000/accounts/google/login/callback/`
     - `http://127.0.0.1:8000/accounts/google/login/callback/`

## 2. Django Admin Configuration

1. Start your Django server: `python manage.py runserver`
2. Go to Django Admin: `http://localhost:8000/admin/`
3. Login with your superuser credentials
4. Navigate to "Social Applications" under "SOCIAL ACCOUNT"
5. Click "Add Social Application"
6. Fill in:
   - **Provider**: Google
   - **Name**: Google OAuth
   - **Client id**: Your Google Client ID
   - **Secret key**: Your Google Client Secret
   - **Sites**: Select "example.com" (or add your domain)

## 3. Environment Variables (Recommended)

Create a `.env` file in your project root:

```
GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH2_SECRET=your-google-client-secret
```

Then update `settings.py` to use environment variables:

```python
import os
from decouple import config

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': config('GOOGLE_OAUTH2_CLIENT_ID', default=''),
            'secret': config('GOOGLE_OAUTH2_SECRET', default=''),
            'key': ''
        }
    }
}
```

## 4. Testing the Integration

### API Endpoints:

1. **Initialize OAuth**: `GET /api/accounts/auth/google/init/`
2. **OAuth Callback**: `GET /api/accounts/auth/google/callback/`
3. **Social Account Status**: `GET /api/accounts/auth/social/status/`

### Frontend Integration:

```javascript
// Initialize Google OAuth
async function loginWithGoogle() {
    const response = await fetch('/api/accounts/auth/google/init/');
    const data = await response.json();
    window.location.href = data.auth_url;
}

// Check OAuth status
async function checkSocialStatus() {
    const response = await fetch('/api/accounts/auth/social/status/', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    });
    return await response.json();
}
```

### HTML Integration:

```html
<!-- Google OAuth Button -->
<button onclick="googleOAuth.initGoogleAuth()" class="btn btn-danger">
    <i class="fab fa-google"></i> Continue with Google
</button>
```

## 5. Security Notes

1. **Never commit client secrets** to version control
2. Use environment variables for production
3. Configure proper redirect URIs for your domain
4. Enable HTTPS in production
5. Regularly rotate your OAuth credentials

## 6. Troubleshooting

### Common Issues:

1. **Invalid redirect URI**: Check your Google Console redirect URIs match exactly
2. **Client ID not found**: Verify your credentials in Django admin
3. **CORS errors**: Ensure your frontend domain is in `CORS_ALLOWED_ORIGINS`
4. **Token errors**: Check JWT configuration in settings

### Debug Mode:

Enable debug logging in `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'allauth': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```