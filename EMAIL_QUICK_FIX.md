# 🚀 Quick Fix: Email Not Sending

## Problem
Welcome emails are not being sent. Error: `Username and Password not accepted`

## ⚡ 5-Minute Fix

### Step 1: Generate New Gmail App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Sign in with: `mentorship@wazireducationsociety.com`
3. If asked to enable 2FA, do it first
4. Click "Select app" → Choose "Mail"
5. Click "Select device" → Choose "Other"
6. Type: "Mentor Connect"
7. Click "Generate"
8. **Copy the 16-character password** (example: abcd efgh ijkl mnop)

### Step 2: Update app.py
Open `app.py` and find line ~146:

```python
# REPLACE THIS LINE:
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "zxgp ivqd obwf csnj")

# WITH YOUR NEW PASSWORD (remove spaces):
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "abcdefghijklmnop")
```

### Step 3: Test It
Run the test script:
```bash
python test_email_smtp.py
```

If you see "✅ SUCCESS!", check your email inbox. You should receive a test email.

### Step 4: Test Signup
1. Go to your application signup page
2. Create a new account
3. Check the email inbox - you should receive the welcome email

## ✅ Done!

Your welcome email feature is now working!

---

## 🔒 Better Security (Optional)

Instead of hardcoding the password, use environment variables:

### 1. Create .env file
Create a file named `.env` in your project root:

```env
SMTP_EMAIL=mentorship@wazireducationsociety.com
SMTP_PASSWORD=your-new-app-password-here
```

### 2. Add to .gitignore
```bash
echo .env >> .gitignore
```

### 3. Install python-dotenv
```bash
pip install python-dotenv
```

### 4. Update app.py
Add at the top (after imports):

```python
from dotenv import load_dotenv
load_dotenv()
```

The existing code already uses `os.environ.get()`, so it will automatically work!

---

## 🎯 Production Recommendation

For production, consider using **SendGrid** instead of Gmail:
- More reliable
- Better deliverability (emails won't go to spam)
- Free tier: 100 emails/day
- Professional email service

See `EMAIL_SMTP_FIX_GUIDE.md` for SendGrid setup instructions.

---

## 📞 Still Having Issues?

Run the diagnostic test:
```bash
python test_email_smtp.py
```

This will tell you exactly what's wrong and how to fix it.

---

## 📚 Documentation

- **Complete Guide:** `EMAIL_SMTP_FIX_GUIDE.md`
- **Feature Docs:** `WELCOME_EMAIL_FEATURE.md`
- **Test Script:** `test_email_smtp.py`

