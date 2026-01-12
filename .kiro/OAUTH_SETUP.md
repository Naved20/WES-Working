# Google OAuth Setup Guide

## Overview
The Mentor Connect app now supports Google OAuth login with automatic user type selection after signup.

## Features Implemented

### 1. Google OAuth Login
- Users can sign in with their Google account
- Automatic account creation for new users
- Profile picture from Google account stored

### 2. User Type Selection
- After OAuth signup, users select their role:
  - **Mentor** (1): Share expertise and guide mentees
  - **Mentee** (2): Learn from experienced mentors
  - **Supervisor** (0): Oversee mentorship programs
  - **Institution** (3): Represent school/organization

### 3. Database Updates
New fields added to `signup_details` table:
- `google_id` - Unique Google ID
- `oauth_provider` - OAuth provider name ('google')
- `profile_picture_url` - URL to Google profile picture
- `oauth_created_at` - Timestamp of OAuth account creation

Modified fields:
- `password` - Now nullable (for OAuth users)
- `user_type` - Now nullable (selected after OAuth signup)

## Routes Added

### `/google_login`
Redirects user to Google OAuth consent screen

### `/callback`
Handles Google OAuth callback:
- Creates new user if doesn't exist
- Logs in existing user
- Redirects to user type selection for new users

### `/select_user_type` (GET/POST)
- GET: Shows user type selection form
- POST: Saves selected user type and redirects to profile completion

## User Flow

### New User (OAuth)
1. Click "Sign in with Google" on signin page
2. Authenticate with Google
3. Redirected to user type selection page
4. Select role (Mentor/Mentee/Supervisor/Institution)
5. Redirected to profile completion form
6. Complete profile and access dashboard

### Existing User (OAuth)
1. Click "Sign in with Google"
2. Authenticated and logged in
3. Redirected to appropriate dashboard

### Traditional Signup
1. Fill signup form with email/password
2. Select user type during signup
3. Redirected to profile completion
4. Complete profile and access dashboard

## Configuration

### Google OAuth Credentials
Located in `client_secret.json`:
- Client ID: 451370715109-6gjomd7m6mhvk3i4a245vsmbbsthclsg.apps.googleusercontent.com
- Redirect URI: http://127.0.0.1:5000/callback (dev) or https://mentorship.weslux.lu/callback (prod)

### Environment Variables
No additional environment variables needed. All config is in `client_secret.json`

## Database Schema

### User Model Changes
```python
class User(db.Model):
    # ... existing fields ...
    password = db.Column(db.String(200), nullable=True)  # Now nullable
    user_type = db.Column(db.String(10), nullable=True)  # Now nullable
    
    # New OAuth fields
    google_id = db.Column(db.String(200), unique=True, nullable=True)
    oauth_provider = db.Column(db.String(50), nullable=True)
    profile_picture_url = db.Column(db.String(500), nullable=True)
    oauth_created_at = db.Column(db.DateTime, nullable=True)
```

## Testing

### Test OAuth Login
1. Start app: `python app.py`
2. Go to http://127.0.0.1:5000/signin
3. Click "Sign in with Google"
4. Use test Google account
5. Select user type
6. Complete profile

### Test Traditional Login
1. Use existing email/password
2. Should login directly to dashboard

## Security Notes

- Google credentials stored in `client_secret.json` (keep secure)
- OAuth tokens handled by Flask-Login
- Password hashing for traditional users
- Session management for both OAuth and traditional users

## Troubleshooting

### "Redirect URI mismatch" error
- Ensure redirect URI in Google Console matches app URL
- Dev: http://127.0.0.1:5000/callback
- Prod: https://mentorship.weslux.lu/callback

### User not redirected to type selection
- Check if user already has user_type set
- Clear session and try again

### Profile picture not showing
- Check `profile_picture_url` is stored in database
- Verify Google profile picture URL is accessible

## Future Enhancements

- Add Facebook OAuth
- Add GitHub OAuth
- Allow users to link multiple OAuth providers
- OAuth profile picture auto-upload to server
