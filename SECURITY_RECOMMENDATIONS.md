# 🔒 Security Recommendations - Meeting App

**Last Updated:** October 2025  
**Priority Levels:** 🔴 Critical | 🟡 High | 🟢 Medium | 🔵 Low

---

## 🚨 Critical Security Issues (Fix Immediately)

### 1. 🔴 Exposed Secret Key in Code

**Current Issue:**
```python
# core/settings.py
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY', 
    'django-insecure-np_we$y*p&mt8f-umqu4lpy$t&s)u%vxm90)tdengygsl@50%('  # ❌ EXPOSED
)
```

**Risk:** Anyone with access to the code can compromise session security, CSRF protection, and JWT token signing.

**Fix:**
```python
# core/settings.py
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY environment variable must be set")
```

**Action Items:**
1. Generate a new secret key: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
2. Store in environment variables only
3. Update `.env.example` with placeholder
4. Rotate the key in all environments
5. Document in deployment guides

---

### 2. 🔴 DEBUG Mode Incorrect Default

**Current Issue:**
```python
# core/settings.py
DEBUG = str(os.environ.get('DEBUG', 'False')).lower() in ('1', 'true', 'yes')
```

**Risk:** This defaults to `False` which is good for production BUT makes development difficult and the docker-compose.yml has `DEBUG=0` which should be `DEBUG=1` for local development.

**Fix:**
```python
# For development, set a better default
DEBUG = str(os.environ.get('DEBUG', 'True')).lower() in ('1', 'true', 'yes')

# Add explicit production check
if os.environ.get('ENVIRONMENT') == 'production':
    if DEBUG:
        raise ValueError("DEBUG cannot be True in production")
```

**Update docker-compose.yml:**
```yaml
environment:
  - DEBUG=1  # For local development
```

---

### 3. 🔴 No Rate Limiting on Authentication Endpoints

**Risk:** Brute force attacks on login, password reset, and registration endpoints.

**Fix - Install django-ratelimit:**
```bash
pip install django-ratelimit
```

**Add to views:**
```python
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

class CustomTokenObtainPairView(TokenObtainPairView):
    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST'))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
```

**Apply to:**
- Login endpoint: 5 attempts per minute per IP
- Registration: 3 attempts per hour per IP
- Password reset: 3 attempts per hour per email

---

## 🟡 High Priority Security Improvements

### 4. 🟡 Missing Security Headers

**Add Django Security Middleware Configuration:**
```python
# core/settings.py

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HTTPS Settings (enable in production)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
```

### 5. 🟡 CORS Configuration Too Permissive

**Current:**
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
```

**Improve:**
```python
# Development
if DEBUG:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
else:
    # Production - use environment variable
    CORS_ALLOWED_ORIGINS = os.environ.get(
        'CORS_ALLOWED_ORIGINS', 
        ''
    ).split(',')

# Additional CORS settings
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]
```

### 6. 🟡 JWT Token Lifetime Too Long

**Current:**
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # Too long
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}
```

**Recommended:**
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),  # Shorter for security
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),     # Reasonable for UX
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,  # Track login times
}
```

### 7. 🟡 Password Reset URL Hardcoded

**Current:**
```python
reset_url = f"http://localhost:3000/password-reset-confirm?uid={uid}&token={token}"
```

**Fix:**
```python
# core/settings.py
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

# accounts/views.py
reset_url = f"{settings.FRONTEND_URL}/password-reset-confirm?uid={uid}&token={token}"
```

### 8. 🟡 Email Security

**Issues:**
- File-based email backend in production
- No email validation beyond format
- No SPF/DKIM configuration documented

**Recommendations:**
```python
# Production email settings
if not DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    
    # Validate email settings
    if not all([EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD]):
        raise ValueError("Email settings must be configured in production")
```

---

## 🟢 Medium Priority Security Enhancements

### 9. 🟢 Add Django Security Checks

**Install django-security:**
```bash
pip install django-security
```

**Run checks:**
```bash
python manage.py check --deploy
```

### 10. 🟢 Input Validation & Sanitization

**Recommendations:**
- Add `bleach` library for HTML sanitization in chat messages
- Validate file uploads (if adding profile pictures)
- Sanitize room names and descriptions
- Add length limits to all text fields

```python
# For chat messages
import bleach

class ChatMessage(models.Model):
    message = models.TextField(max_length=1000)
    
    def save(self, *args, **kwargs):
        # Sanitize HTML
        self.message = bleach.clean(
            self.message,
            tags=[],  # No HTML allowed
            strip=True
        )
        super().save(*args, **kwargs)
```

### 11. 🟢 API Authentication Improvements

**Add API key support for external integrations:**
```python
# accounts/authentication.py
from rest_framework.authentication import BaseAuthentication

class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        if api_key:
            # Validate API key
            pass
```

### 12. 🟢 Add Content Security Policy

```python
# Install django-csp
# pip install django-csp

MIDDLEWARE = [
    # ... other middleware
    'csp.middleware.CSPMiddleware',
]

# CSP Settings
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://fonts.googleapis.com")
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_CONNECT_SRC = ("'self'",)
```

---

## 🔵 Low Priority / Future Enhancements

### 13. 🔵 Two-Factor Authentication (2FA)

**Consider adding:**
- TOTP (Time-based One-Time Password)
- SMS verification
- Email verification codes
- Backup codes

**Library:** django-otp

### 14. 🔵 Account Security Features

- Login history tracking
- Suspicious activity alerts
- IP-based login restrictions
- Device management
- Session management

### 15. 🔵 API Request Logging

**Log all API requests for security auditing:**
```python
# Create middleware for request logging
class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Log request details
        logger.info(f"API Request: {request.method} {request.path}")
        return self.get_response(request)
```

### 16. 🔵 Automated Security Scanning

**Add to CI/CD:**
- Bandit (Python security linter)
- Safety (dependency vulnerability scanner)
- OWASP Dependency-Check

```yaml
# .github/workflows/security.yml
name: Security Scan
on: [push, pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r . -f json -o bandit-report.json
      - name: Run Safety
        run: |
          pip install safety
          safety check
```

---

## 🛡️ OAuth Security Checklist

### Current OAuth Setup: ✅ Good

**Already Implemented:**
- ✅ PKCE enabled
- ✅ State parameter for CSRF protection
- ✅ Token storage in backend
- ✅ Proper redirect URI validation

**Additional Recommendations:**
- Store OAuth tokens encrypted at rest
- Add OAuth token refresh logic
- Implement OAuth scope management
- Add OAuth account unlinking

---

## 📝 Security Best Practices Checklist

### Code Security
- [ ] No hardcoded credentials
- [ ] No sensitive data in version control
- [ ] All secrets in environment variables
- [ ] Dependency versions pinned
- [ ] Regular dependency updates
- [ ] Security linting in CI/CD

### Authentication & Authorization
- [ ] Rate limiting on auth endpoints
- [ ] Strong password policies
- [ ] Account lockout after failed attempts
- [ ] Secure password reset flow
- [ ] JWT token rotation
- [ ] Session timeout configured

### Data Protection
- [ ] HTTPS enforced in production
- [ ] Secure cookies (Secure, HttpOnly, SameSite)
- [ ] Database connection encryption
- [ ] Backup encryption
- [ ] PII data protection

### Infrastructure
- [ ] Security headers configured
- [ ] CORS properly configured
- [ ] CSP implemented
- [ ] DDoS protection
- [ ] Regular security audits
- [ ] Incident response plan

---

## 🚀 Implementation Priority

**Week 1: Critical Fixes**
1. Fix SECRET_KEY issue
2. Fix DEBUG mode
3. Add rate limiting
4. Add security headers

**Week 2: High Priority**
1. Improve CORS configuration
2. Adjust JWT token lifetime
3. Fix email configuration
4. Add HTTPS enforcement

**Week 3: Medium Priority**
1. Add input validation
2. Implement CSP
3. Add API security features
4. Run security scans

**Month 2+: Continuous Improvement**
- Implement 2FA
- Add advanced monitoring
- Regular security audits
- Penetration testing

---

## 📚 Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [DRF Security Best Practices](https://www.django-rest-framework.org/topics/security/)
- [JWT Security Best Practices](https://tools.ietf.org/html/rfc8725)

---

**Remember:** Security is an ongoing process, not a one-time task. Regular audits, updates, and monitoring are essential for maintaining a secure application.
