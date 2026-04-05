# Deploy Certificate Feature to Production

## Changes Made
1. Added `created_at` field to User model to track exact registration date
2. Added certificate route `/my_certificate` in app.py
3. Created beautiful certificate template with WES logo
4. Added "My Certificate" button in top navbar (left of profile icon) for mentors and mentees
5. Certificate includes: user name, exact registration date, user type, certificate ID
6. Features: Download as PNG and Print

## Deployment Steps

### 1. Pull Latest Code on Production
```bash
cd /home/luxment/htdocs/mentorship.weslux.lu/WES-Working
git pull origin main
```

### 2. Run Database Migration
```bash
# Activate virtual environment if needed
source venv/bin/activate  # or source .venv/bin/activate

# Run migration to add created_at field
flask db upgrade
```

### 3. Restart Application
Go to CloudPanel dashboard:
- Sites → mentorship.weslux.lu
- Click 'Restart' button

OR manually restart:
```bash
# Find and kill existing processes
ps aux | grep gunicorn | grep luxment

# Start new process (CloudPanel handles this automatically)
```

### 4. Test the Feature
1. Login as mentor or mentee
2. Look for "My Certificate" button in top navbar (purple button, left of profile icon)
3. Click button to view certificate
4. Verify certificate displays with correct registration date
5. Test download and print features

## Certificate Details
- Route: `/my_certificate`
- Template: `templates/certificate.html`
- Registration Date: Uses `created_at` field (exact date when user registered)
- Certificate ID Format: WES-{user_type}-{user_id}
- User Types: 1=Mentor, 2=Mentee, 0=Supervisor, 3=Institution
- Button Location: Top navbar, left of profile dropdown (only visible for mentors and mentees)

## Database Changes
- Added `created_at` column to `signup_details` table
- Migration file: `migrations/versions/add_created_at_to_user.py`
- Existing users will have their `created_at` set to migration run time

## Troubleshooting
If certificate doesn't load:
1. Check migration ran successfully: `flask db current`
2. Verify created_at field exists: Check database schema
3. Verify logo path: `static/img/logo.jpg`
4. Check html2canvas CDN is accessible
5. Verify user is logged in (session check)

If button doesn't appear:
1. Clear browser cache
2. Check user_type is '1' or '2' (mentor or mentee)
3. Verify base2.html template updated correctly

## Files Changed
- `app.py` (User model + certificate route)
- `templates/certificate.html` (new file)
- `templates/base2.html` (added certificate button in navbar)
- `templates/mentee/menteedashboard.html` (removed duplicate button)
- `templates/mentor/mentordashboard.html` (removed duplicate button)
- `migrations/versions/add_created_at_to_user.py` (new migration)
