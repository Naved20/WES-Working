# 📧 Gmail App Password Setup - Step by Step

## Why Do You Need This?

Gmail requires an "App Password" for applications to send emails. Your regular Gmail password won't work for security reasons.

---

## Prerequisites

✅ You must have **2-Factor Authentication (2FA)** enabled on your Gmail account  
✅ You must be the owner of the Gmail account  
✅ You need access to the Gmail account: `mentorship@wazireducationsociety.com`

---

## Step-by-Step Instructions

### Step 1: Enable 2-Factor Authentication (If Not Already Enabled)

1. Go to: https://myaccount.google.com/security
2. Sign in with `mentorship@wazireducationsociety.com`
3. Look for "2-Step Verification" section
4. If it says "OFF", click on it and follow the setup wizard
5. You'll need to:
   - Add a phone number
   - Verify with a code sent to your phone
   - Complete the setup

**Note:** If 2FA is already enabled, skip to Step 2.

---

### Step 2: Generate App Password

1. **Go to App Passwords page:**
   - Direct link: https://myaccount.google.com/apppasswords
   - Or: Google Account → Security → 2-Step Verification → App passwords

2. **Sign in if prompted**

3. **Select app:**
   - Click the dropdown that says "Select app"
   - Choose "Mail"

4. **Select device:**
   - Click the dropdown that says "Select device"
   - Choose "Other (Custom name)"
   - Type: "Mentor Connect App"

5. **Generate:**
   - Click the "Generate" button
   - A popup will appear with a 16-character password
   - Example format: `abcd efgh ijkl mnop`

6. **Copy the password:**
   - Click the copy button or manually copy it
   - **IMPORTANT:** Save it somewhere safe - you won't be able to see it again!

---

### Step 3: Update Your Application

1. **Open app.py in your code editor**

2. **Find line ~146** (search for "SMTP_PASSWORD"):
   ```python
   SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "zxgp ivqd obwf csnj")
   ```

3. **Replace with your new password** (remove spaces):
   ```python
   # If your password is: abcd efgh ijkl mnop
   # Remove spaces and use: abcdefghijklmnop
   
   SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "abcdefghijklmnop")
   ```

4. **Save the file**

---

### Step 4: Test the Configuration

Run the test script:
```bash
python test_email_smtp.py
```

**Expected output if successful:**
```
✅ Connected successfully
✅ TLS started successfully
✅ Login successful!
✅ Email prepared
✅ Email sent successfully!
🎉 SUCCESS! SMTP is configured correctly!
```

**Check your email:**
- Go to `mentorship@wazireducationsociety.com` inbox
- You should see a test email with subject "✅ SMTP Test - Mentor Connect"
- If you received it, everything is working!

---

### Step 5: Test Welcome Email in Your App

1. **Go to your application signup page**
2. **Create a test account:**
   - Name: Test User
   - Email: your-test-email@gmail.com
   - Password: Test123!
3. **Complete signup**
4. **Check the email inbox** (your-test-email@gmail.com)
5. **You should receive the welcome email** with subject "Welcome to Mentor Connect! 🎉"

---

## Troubleshooting

### Problem: "App passwords" option not available

**Solution:**
- Make sure 2-Factor Authentication is enabled
- Wait a few minutes after enabling 2FA
- Try signing out and signing back in
- Some Google Workspace accounts may have this disabled by admin

---

### Problem: Still getting authentication error after updating password

**Solutions:**
1. **Verify you removed spaces from the password:**
   - ❌ Wrong: `"abcd efgh ijkl mnop"`
   - ✅ Correct: `"abcdefghijklmnop"`

2. **Generate a new App Password:**
   - The old one might have been revoked
   - Delete the old App Password from Google Account
   - Generate a fresh one

3. **Check for typos:**
   - Make sure you copied the entire password
   - No extra characters or spaces

4. **Restart your application:**
   - Stop the Flask app if running
   - Start it again to load new configuration

---

### Problem: Email sent but not received

**Solutions:**
1. **Check spam/junk folder**
2. **Wait a few minutes** (sometimes delayed)
3. **Check Gmail "Sent" folder** to confirm it was sent
4. **Try sending to a different email address**

---

### Problem: Emails going to spam

**Solutions:**
1. **For testing:** Mark as "Not Spam" in your email client
2. **For production:** Consider using SendGrid or Mailgun
   - Professional email services have better deliverability
   - Less likely to be marked as spam
   - See `EMAIL_SMTP_FIX_GUIDE.md` for setup

---

## Security Best Practices

### ✅ DO:
- Keep your App Password secret
- Use environment variables (see below)
- Revoke old App Passwords you're not using
- Generate new password if compromised

### ❌ DON'T:
- Share your App Password
- Commit passwords to Git
- Use your regular Gmail password
- Reuse App Passwords across multiple apps

---

## Better Security: Use Environment Variables

Instead of hardcoding the password in `app.py`, use environment variables:

### 1. Create .env file
Create a file named `.env` in your project root:

```env
SMTP_EMAIL=mentorship@wazireducationsociety.com
SMTP_PASSWORD=abcdefghijklmnop
```

### 2. Add .env to .gitignore
```bash
echo .env >> .gitignore
```

### 3. Install python-dotenv
```bash
pip install python-dotenv
pip freeze > requirements.txt
```

### 4. Update app.py
Add at the very top of `app.py` (after imports):

```python
from dotenv import load_dotenv
load_dotenv()  # This loads variables from .env file
```

### 5. Keep the existing code
The existing code already uses `os.environ.get()`, so it will automatically pick up values from `.env`:

```python
SMTP_EMAIL = os.environ.get("SMTP_EMAIL", "mentorship@wazireducationsociety.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "zxgp ivqd obwf csnj")
```

Now your password is not in the code!

---

## Alternative: Use SendGrid (Recommended for Production)

Gmail SMTP is fine for testing, but for production, use a professional email service:

### Why SendGrid?
- ✅ More reliable than Gmail
- ✅ Better deliverability (won't go to spam)
- ✅ Email analytics (open rates, click rates)
- ✅ Free tier: 100 emails/day
- ✅ Easy to scale
- ✅ Professional support

### Quick Setup:
1. Sign up at https://sendgrid.com/
2. Verify your email
3. Create API key
4. Install: `pip install sendgrid`
5. Update email functions (see `EMAIL_SMTP_FIX_GUIDE.md`)

---

## Summary Checklist

- [ ] 2-Factor Authentication enabled on Gmail
- [ ] App Password generated
- [ ] Password copied (without spaces)
- [ ] `app.py` updated with new password
- [ ] Test script run successfully (`python test_email_smtp.py`)
- [ ] Test email received in inbox
- [ ] Signup tested with welcome email
- [ ] Welcome email received
- [ ] (Optional) Environment variables configured
- [ ] (Optional) `.env` added to `.gitignore`

---

## Need Help?

1. **Run the diagnostic test:**
   ```bash
   python test_email_smtp.py
   ```

2. **Read the detailed guide:**
   - `EMAIL_SMTP_FIX_GUIDE.md` - Complete solutions
   - `EMAIL_QUICK_FIX.md` - Quick reference
   - `WELCOME_EMAIL_FEATURE.md` - Feature documentation

3. **Check Google Account:**
   - https://myaccount.google.com/security
   - https://myaccount.google.com/apppasswords

---

## Quick Reference

| What | Where |
|------|-------|
| Enable 2FA | https://myaccount.google.com/security |
| Generate App Password | https://myaccount.google.com/apppasswords |
| Update password | `app.py` line ~146 |
| Test SMTP | `python test_email_smtp.py` |
| Test signup | Your app's `/signup` page |

---

**Good luck! 🚀**

Once you complete these steps, your welcome email feature will work perfectly!

