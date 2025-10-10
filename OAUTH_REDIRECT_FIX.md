# Google OAuth Redirect URI Mismatch - SOLUTION

## Problem
You're getting `Error 400: redirect_uri_mismatch` when trying to authenticate with Google.

## Root Cause
The redirect URI configured in Google Cloud Console doesn't match what Django is sending.

## SOLUTION 1: Update Google Cloud Console (REQUIRED)

### Step 1: Access Google Cloud Console
1. Go to: https://console.cloud.google.com/
2. Select your project (or the project associated with your OAuth app)

### Step 2: Navigate to OAuth Configuration
1. Go to **APIs & Services** > **Credentials**
2. Find your OAuth 2.0 Client ID: `1011917550414-kv7ncc1hkfbvaavknfknq8tbs3dg6n2s`
3. Click on it to edit

### Step 3: Add Redirect URIs
In the **Authorized redirect URIs** section, add BOTH of these URLs:
```
http://localhost:8000/accounts/google/login/callback/
http://127.0.0.1:8000/accounts/google/login/callback/    
```

### Step 4: Save Changes
Click **Save** and wait a few minutes for the changes to propagate.

## SOLUTION 2: Update Django Settings (COMPLETED)

✅ I've already updated your `settings.py` to include:
```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

## Test After Fix

1. **Restart Django Server**:
   ```bash
   python manage.py runserver
   ```

2. **Test Google OAuth**:
   - Visit: http://localhost:8000/login/
   - Click "Continue with Google"
   - Should now work without redirect_uri_mismatch error

## Alternative URLs to Try

If you're still having issues, try accessing your app via:
- http://localhost:8000/login/ (instead of 127.0.0.1)
- Make sure you're using the same URL format that you configured in Google Console

## Verification

Once you've updated the Google Cloud Console, the OAuth flow should work correctly. The redirect URI mismatch error should be resolved.