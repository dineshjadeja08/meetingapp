# Email Configuration Guide for Meeting App

## Current Issue: Not Receiving Password Reset Emails

The reason you're not receiving emails is because the email backend was set to `console` mode, which only prints emails to the Django server terminal instead of actually sending them.

## Email Backend Options

### 1. Console Backend (Current - Development Only)
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```
- **Purpose**: Development testing
- **Behavior**: Prints emails to Django server console
- **Pros**: No configuration needed
- **Cons**: No actual emails sent

### 2. File-based Backend (Testing)
```python
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = 'tmp/app-messages'
```
- **Purpose**: Testing without SMTP
- **Behavior**: Saves emails as files
- **Pros**: Can see email content without SMTP setup
- **Cons**: No actual emails sent

### 3. SMTP Backend (Production)
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```
- **Purpose**: Production use
- **Behavior**: Sends actual emails
- **Pros**: Real email delivery
- **Cons**: Requires SMTP configuration

## Quick Fix Options

### Option 1: File-based Testing (Immediate)
Update `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = 'tmp/app-messages'
```

### Option 2: Gmail SMTP Setup

#### Step 1: Enable 2-Factor Authentication on Gmail
1. Go to Google Account settings
2. Enable 2-Factor Authentication

#### Step 2: Generate App Password
1. Go to Google Account → Security → 2-Step Verification
2. Scroll down to "App passwords"
3. Generate password for "Mail"
4. Copy the 16-character password

#### Step 3: Update settings.py
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'youremail@gmail.com'  # Your Gmail address
EMAIL_HOST_PASSWORD = 'your-16-char-app-password'  # App password from step 2
DEFAULT_FROM_EMAIL = 'Meeting App <youremail@gmail.com>'
```

### Option 3: Other Email Providers

#### Outlook/Hotmail
```python
EMAIL_HOST = 'smtp.live.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

#### Yahoo Mail
```python
EMAIL_HOST = 'smtp.mail.yahoo.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

## Testing Email Configuration

### Test Script
Create a test file to verify email configuration:

```python
# test_email.py
from django.core.mail import send_mail
from django.conf import settings

def test_email():
    try:
        send_mail(
            'Test Email from Meeting App',
            'This is a test email to verify email configuration.',
            settings.DEFAULT_FROM_EMAIL,
            ['your-test-email@example.com'],
            fail_silently=False,
        )
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Email failed: {e}")

if __name__ == "__main__":
    test_email()
```

### Django Shell Test
```python
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```

## Environment Variables (Recommended)

For security, use environment variables:

### .env file
```
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### settings.py
```python
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
```

## Troubleshooting

### Common Issues

1. **Gmail "Less secure app access"** 
   - Solution: Use App Password instead

2. **Authentication failed**
   - Check email/password
   - Verify 2FA and app password

3. **Connection refused**
   - Check EMAIL_HOST and EMAIL_PORT
   - Verify firewall/antivirus settings

4. **Emails in spam folder**
   - Check recipient's spam folder
   - Consider using verified domain

### Debug Settings
```python
# Add to settings.py for debugging
EMAIL_USE_SSL = False  # Use with port 465
EMAIL_USE_TLS = True   # Use with port 587
EMAIL_TIMEOUT = 30     # Timeout in seconds

# Enable logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
    },
    'loggers': {
        'django.core.mail': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Next Steps

1. **Choose an email backend** (file-based for testing or SMTP for production)
2. **Update settings.py** with your configuration
3. **Test the configuration** using the test script
4. **Try password reset again**

## Current Status

✅ Password reset API endpoint working
✅ Email template created
❌ Email delivery not configured
🔄 Need to configure SMTP or file-based backend

Choose one of the options above to start receiving password reset emails!