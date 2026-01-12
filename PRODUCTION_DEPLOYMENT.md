# Production Deployment Guide for Mentor Connect

## Pre-Deployment Checklist

### 1. Update app.py Configuration
In `app.py`, change:
```python
PRODUCTION = True  # Change from False to True
```

### 2. Set Your Production Domain
Update the `REDIRECT_URI` in app.py:
```python
REDIRECT_URI = "https://yourdomain.com/callback"  # Your actual domain
```

### 3. Generate a Strong Secret Key
Run this command to generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Then set it as an environment variable:
```bash
export SECRET_KEY="your-generated-secret-key"
```

### 4. Update Google Cloud Console
1. Go to https://console.cloud.google.com/apis/credentials
2. Edit your OAuth 2.0 Client ID
3. Add your production domain to:
   - **Authorized JavaScript origins**: `https://yourdomain.com`
   - **Authorized redirect URIs**: `https://yourdomain.com/callback`
4. Download the updated `client_secret.json`

### 5. Database Setup (Recommended: PostgreSQL)
For production, use PostgreSQL instead of SQLite:
```bash
export DATABASE_URL="postgresql://username:password@host:5432/database_name"
```

## Deployment Options

### Option A: Deploy with Gunicorn (Linux Server)
```bash
# Install dependencies
pip install -r requirements.txt

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Option B: Deploy to AWS Elastic Beanstalk
1. Create `.ebextensions/python.config`:
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app:app
```

2. Deploy:
```bash
eb init -p python-3.11 mentor-connect
eb create mentor-connect-env
eb deploy
```

### Option C: Deploy to Heroku
1. Create `Procfile`:
```
web: gunicorn app:app
```

2. Deploy:
```bash
heroku create mentor-connect
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set DATABASE_URL="your-postgres-url"
git push heroku main
```

## Environment Variables Required
```bash
SECRET_KEY=your-strong-secret-key
DATABASE_URL=postgresql://user:pass@host:5432/dbname  # Optional, for PostgreSQL
```

## Security Checklist
- [ ] `PRODUCTION = True` in app.py
- [ ] Strong SECRET_KEY set
- [ ] HTTPS enabled (SSL certificate)
- [ ] `OAUTHLIB_INSECURE_TRANSPORT` NOT set in production
- [ ] Debug mode OFF
- [ ] Database credentials secured
- [ ] `client_secret.json` kept secure (not in public repo)

## Files to Keep Secure (Add to .gitignore)
```
client_secret.json
service_account.json
instance/
*.db
.env
```

## Running Database Migrations
```bash
flask db upgrade
```

## Testing Production Locally
```bash
# Set production mode
export PRODUCTION=True
export SECRET_KEY="test-secret-key"

# Run with gunicorn
gunicorn -w 2 -b 127.0.0.1:5000 app:app
```
