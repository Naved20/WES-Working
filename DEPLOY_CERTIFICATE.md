# Deploy Certificate Feature to Production

## Changes Made
1. Added certificate route `/my_certificate` in app.py
2. Created beautiful certificate template with WES logo
3. Added "My Certificate" button to mentor and mentee dashboards
4. Certificate includes: user name, registration date, user type, certificate ID
5. Features: Download as PNG and Print

## Deployment Steps

### 1. Pull Latest Code on Production
```bash
cd /home/luxment/htdocs/mentorship.weslux.lu/WES-Working
git pull origin main
```

### 2. Restart Application
Go to CloudPanel dashboard:
- Sites → mentorship.weslux.lu
- Click 'Restart' button

OR manually restart:
```bash
# Find and kill existing processes
ps aux | grep gunicorn | grep luxment

# Start new process (CloudPanel handles this automatically)
```

### 3. Test the Feature
1. Login as mentor or mentee
2. Click "My Certificate" button on dashboard
3. Verify certificate displays correctly
4. Test download and print features

## Certificate Details
- Route: `/my_certificate`
- Template: `templates/certificate.html`
- Registration Date: Uses `oauth_created_at` for OAuth users, shows "Member since account creation" for others
- Certificate ID Format: WES-{user_type}-{user_id}
- User Types: 1=Mentor, 2=Mentee, 0=Supervisor, 3=Institution

## Troubleshooting
If certificate doesn't load:
1. Check app.py line 5623 - should use `oauth_created_at` not `created_at`
2. Verify logo path: `static/img/logo.jpg`
3. Check html2canvas CDN is accessible
4. Verify user is logged in (session check)

## Files Changed
- `app.py` (lines 5592-5650)
- `templates/certificate.html` (new file)
- `templates/mentee/menteedashboard.html`
- `templates/mentor/mentordashboard.html`
