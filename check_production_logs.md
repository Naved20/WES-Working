# How to Find Production Error Logs

## 🔍 Step 1: Check Application Logs

### For cPanel/Shared Hosting:
```bash
# Check error logs in cPanel
# Go to: cPanel → Metrics → Errors
# Or check file manager: /home/username/logs/error_log
```

### For Cloud Panel:
```bash
# SSH into server
ssh your-server

# Check application logs
tail -f /var/log/your-app/error.log

# Or check system logs
tail -f /var/log/syslog | grep python
```

### For AWS/DigitalOcean:
```bash
# Check gunicorn logs
tail -f /var/log/gunicorn/error.log

# Or systemd logs
sudo journalctl -u your-app-name -f --lines=100
```

---

## 🔍 Step 2: Enable Flask Debug Mode (Temporarily)

**⚠️ WARNING: Only do this temporarily to see error, then disable!**

In `app.py`, find this line:
```python
PRODUCTION = True
```

Change to:
```python
PRODUCTION = False  # TEMPORARY - for debugging only
```

Then restart app. You'll see detailed error on screen.

**IMPORTANT: Change back to `True` after finding error!**

---

## 🔍 Step 3: Check Python Error Logs

### Method 1: Check Flask logs
```bash
# If using gunicorn
tail -f /var/log/gunicorn/error.log

# If using uwsgi
tail -f /var/log/uwsgi/app.log

# If using systemd
sudo journalctl -u your-app-name -n 100 --no-pager
```

### Method 2: Check Apache/Nginx logs
```bash
# Apache
tail -f /var/log/apache2/error.log

# Nginx
tail -f /var/log/nginx/error.log
```

---

## 🔍 Step 4: Add Logging to app.py

Add this at the top of `app.py` (after imports):

```python
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('app_errors.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

app.logger.setLevel(logging.DEBUG)
```

Then check `app_errors.log` file for errors.

---

## 🔍 Step 5: Test Database Connection

Create `test_db.py` on production:

```python
#!/usr/bin/env python3
from app import app, db, MenteeProfile, User

print("Testing database connection...")

with app.app_context():
    try:
        # Test basic query
        user_count = User.query.count()
        print(f"✅ Users in database: {user_count}")
        
        # Test mentee profile query
        mentee_count = MenteeProfile.query.count()
        print(f"✅ Mentee profiles: {mentee_count}")
        
        # Test parent consent columns
        profile = MenteeProfile.query.first()
        if profile:
            print(f"✅ Parent email column exists: {hasattr(profile, 'parent_email')}")
            print(f"✅ Parent consent status: {hasattr(profile, 'parent_consent_status')}")
        
        print("\n✅ Database connection successful!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
```

Run it:
```bash
python test_db.py
```

---

## 🔍 Step 6: Common Errors & Solutions

### Error 1: "no such column: parent_email"
**Solution:**
```bash
flask db upgrade
# OR
sqlite3 instance/mentors_connect.db < fix_db.sql
```

### Error 2: "Unable to build URLs without SERVER_NAME"
**Solution:** In `app.py`, check if `PRODUCTION = True` is set correctly

### Error 3: "Permission denied" on database
**Solution:**
```bash
chmod 664 instance/mentors_connect.db
chown www-data:www-data instance/mentors_connect.db
```

### Error 4: "Module not found"
**Solution:**
```bash
pip install -r requirements.txt
```

### Error 5: SMTP authentication failed
**Solution:** Check environment variables:
```bash
echo $SMTP_EMAIL
echo $SMTP_PASSWORD
```

---

## 🔍 Step 7: Quick Error Check Script

Create `quick_check.py`:

```python
#!/usr/bin/env python3
import sys
import os

print("="*60)
print("PRODUCTION ERROR CHECKER")
print("="*60)

# Check 1: Python version
print(f"\n1. Python version: {sys.version}")

# Check 2: Check if app.py exists
print(f"2. app.py exists: {os.path.exists('app.py')}")

# Check 3: Check if database exists
print(f"3. Database exists: {os.path.exists('instance/mentors_connect.db')}")

# Check 4: Check database permissions
if os.path.exists('instance/mentors_connect.db'):
    import stat
    st = os.stat('instance/mentors_connect.db')
    print(f"4. Database permissions: {oct(st.st_mode)[-3:]}")

# Check 5: Try importing app
try:
    from app import app
    print("5. ✅ App import successful")
except Exception as e:
    print(f"5. ❌ App import failed: {e}")
    sys.exit(1)

# Check 6: Try importing database
try:
    from app import db, MenteeProfile
    print("6. ✅ Database models import successful")
except Exception as e:
    print(f"6. ❌ Database import failed: {e}")
    sys.exit(1)

# Check 7: Test database connection
try:
    with app.app_context():
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"7. ✅ Database tables: {len(tables)} tables found")
        
        # Check if mentee_profile table exists
        if 'mentee_profile' in tables:
            columns = [col['name'] for col in inspector.get_columns('mentee_profile')]
            print(f"8. ✅ mentee_profile columns: {len(columns)} columns")
            
            # Check parent consent columns
            required_cols = ['parent_email', 'parent_consent_status', 'parent_consent_token', 'parent_consent_date']
            missing = [col for col in required_cols if col not in columns]
            
            if missing:
                print(f"9. ❌ MISSING COLUMNS: {missing}")
                print("\n   FIX: Run 'flask db upgrade' or 'sqlite3 instance/mentors_connect.db < fix_db.sql'")
            else:
                print(f"9. ✅ All parent consent columns exist")
        else:
            print("8. ❌ mentee_profile table not found!")
            
except Exception as e:
    print(f"7. ❌ Database connection failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Check complete!")
print("="*60)
```

Run it:
```bash
python quick_check.py
```

---

## 📞 Send Me This Info:

Run these commands and send me the output:

```bash
# 1. Check Python version
python --version

# 2. Check if database has parent consent columns
python check_production_db.py

# 3. Check recent errors
tail -20 /var/log/your-app/error.log

# 4. Test database
python test_db.py

# 5. Quick check
python quick_check.py
```

Send me the output and I'll tell you exactly what's wrong!
