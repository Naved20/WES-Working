# Production Error Fix - Parent Consent Fields Missing

## Problem
Mentee login me error aa raha hai kyunki production database me parent consent columns nahi hain.

## Solution - Production Server pe ye commands run karo:

### Step 1: SSH into production server
```bash
ssh your-production-server
```

### Step 2: Navigate to project directory
```bash
cd /path/to/WES-Working
```

### Step 3: Activate virtual environment (if using)
```bash
source venv/bin/activate
# OR
source .venv/bin/activate
```

### Step 4: Pull latest code from GitHub
```bash
git pull origin main
```

### Step 5: Run database migration
```bash
flask db upgrade
```

### Step 6: Restart the application
```bash
# If using systemd
sudo systemctl restart your-app-name

# OR if using supervisor
sudo supervisorctl restart your-app-name

# OR if using gunicorn directly
pkill gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

---

## Alternative: Manual Database Update (if migration fails)

If `flask db upgrade` fails, run this SQL directly on production database:

```sql
-- Add parent consent columns to mentee_profile table
ALTER TABLE mentee_profile ADD COLUMN parent_email VARCHAR(150);
ALTER TABLE mentee_profile ADD COLUMN parent_consent_status VARCHAR(20) DEFAULT 'pending';
ALTER TABLE mentee_profile ADD COLUMN parent_consent_token VARCHAR(200);
ALTER TABLE mentee_profile ADD COLUMN parent_consent_date DATETIME;

-- Update existing records to have approved status (for existing mentees)
UPDATE mentee_profile SET parent_consent_status = 'approved' WHERE parent_consent_status IS NULL;
```

### To run SQL on production:

**For SQLite:**
```bash
sqlite3 instance/mentors_connect.db < fix_db.sql
```

**For PostgreSQL:**
```bash
psql -U your_db_user -d your_db_name -f fix_db.sql
```

**For MySQL:**
```bash
mysql -u your_db_user -p your_db_name < fix_db.sql
```

---

## Verify the fix:

After running migration, check if columns exist:

**For SQLite:**
```bash
sqlite3 instance/mentors_connect.db "PRAGMA table_info(mentee_profile);"
```

Look for these columns:
- parent_email
- parent_consent_status
- parent_consent_token
- parent_consent_date

---

## Quick Check Script

Create a file `check_db.py` on production:

```python
from app import app, db, MenteeProfile

with app.app_context():
    # Check if columns exist
    try:
        profile = MenteeProfile.query.first()
        if profile:
            print(f"✅ parent_email exists: {hasattr(profile, 'parent_email')}")
            print(f"✅ parent_consent_status exists: {hasattr(profile, 'parent_consent_status')}")
            print(f"✅ parent_consent_token exists: {hasattr(profile, 'parent_consent_token')}")
            print(f"✅ parent_consent_date exists: {hasattr(profile, 'parent_consent_date')}")
            print("\n✅ All parent consent columns exist!")
        else:
            print("No mentee profiles found")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n⚠️ Parent consent columns are missing!")
```

Run it:
```bash
python check_db.py
```

---

## Common Issues:

### Issue 1: Multiple migration heads
**Error:** "Multiple head revisions are present"

**Fix:**
```bash
flask db merge heads -m "merge_all_heads"
flask db upgrade
```

### Issue 2: Permission denied
**Error:** "Permission denied" when accessing database

**Fix:**
```bash
sudo chown -R your-user:your-user instance/
chmod 664 instance/mentors_connect.db
```

### Issue 3: SMTP not configured
**Error:** Email sending fails

**Fix:** Check environment variables:
```bash
export SMTP_EMAIL="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"
```

---

## After Fix - Test:

1. Try logging in as mentee
2. Go to edit profile
3. Enter DOB that makes mentee under 18
4. Parent email field should appear
5. Save profile
6. Check if email is sent

---

## Need Help?

If still getting errors, check production logs:
```bash
# For systemd
sudo journalctl -u your-app-name -f

# For supervisor
tail -f /var/log/supervisor/your-app-name.log

# For gunicorn
tail -f /var/log/gunicorn/error.log
```

Send me the error message and I'll help fix it!
