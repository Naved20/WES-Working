# Email SMTP Authentication Fix Guide

## Current Issue
**Error:** `(535, b'5.7.8 Username and Password not accepted')`

The welcome email feature is fully implemented but Gmail SMTP authentication is failing. This is preventing emails from being sent.

## Root Cause
Gmail has strict security requirements for SMTP access:
- Requires 2-factor authentication (2FA) enabled
- Requires App-specific password (not regular password)
- App passwords can expire or be revoked
- "Less secure app access" is deprecated by Google

## Solution Options

### Option 1: Fix Gmail App Password (Recommended for Quick Fix)

#### Step 1: Verify 2-Factor Authentication
1. Go to https://myaccount.google.com/security
2. Sign in with `mentorship@wazireducationsociety.com`
3. Check if "2-Step Verification" is ON
4. If OFF, enable it first

#### Step 2: Generate New App Password
1. Go to https://myaccount.google.com/apppasswords
2. Sign in if prompted
3. Click "Select app" → Choose "Mail"
4. Click "Select device" → Choose "Other (Custom name)"
5. Enter name: "Mentor Connect App"
6. Click "Generate"
7. Copy the 16-character password (format: xxxx xxxx xxxx xxxx)

#### Step 3: Update app.py
Replace the current password in `app.py`:

```python
# OLD (line ~146)
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "zxgp ivqd obwf csnj")

# NEW - Use your newly generated password
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "your-new-app-password-here")
```

#### Step 4: Test
```bash
python test_profile_completion_email.py
```

---

### Option 2: Use Environment Variables (Best Practice)

Instead of hardcoding credentials, use environment variables:

#### Step 1: Create .env file
Create a file named `.env` in your project root:

```env
SMTP_EMAIL=mentorship@wazireducationsociety.com
SMTP_PASSWORD=your-new-app-password-here
```

#### Step 2: Add .env to .gitignore
```bash
echo .env >> .gitignore
```

#### Step 3: Install python-dotenv
```bash
pip install python-dotenv
pip freeze > requirements.txt
```

#### Step 4: Update app.py
Add at the top of `app.py` (after imports):

```python
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
```

The existing code already uses `os.environ.get()`, so it will automatically pick up the values from .env file.

---

### Option 3: Use SendGrid (Recommended for Production)

SendGrid is more reliable and has better deliverability than Gmail SMTP.

#### Step 1: Create SendGrid Account
1. Go to https://sendgrid.com/
2. Sign up for free account (100 emails/day free)
3. Verify your email
4. Create API key: Settings → API Keys → Create API Key

#### Step 2: Install SendGrid
```bash
pip install sendgrid
pip freeze > requirements.txt
```

#### Step 3: Update app.py Email Functions
Replace the email functions with SendGrid implementation:

```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Configuration
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY", "your-api-key-here")
FROM_EMAIL = "mentorship@wazireducationsociety.com"

def send_otp_email(to_email, otp):
    """Send OTP using SendGrid"""
    try:
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=to_email,
            subject="Password Reset OTP - Mentor Connect",
            html_content=f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #2563eb;">Password Reset Request</h2>
                <p>You have requested to reset your password for Mentor Connect.</p>
                <p>Your OTP code is:</p>
                <h1 style="color: #2563eb; font-size: 32px; letter-spacing: 5px;">{otp}</h1>
                <p>This OTP will expire in <strong>10 minutes</strong>.</p>
                <p>If you did not request this, please ignore this email.</p>
                <hr>
                <p style="color: #666; font-size: 12px;">Mentor Connect - Wazir Education Society</p>
            </body>
            </html>
            """
        )
        
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_welcome_email(to_email, user_name, signup_method="traditional"):
    """Send welcome email using SendGrid"""
    try:
        signup_text = "signing up" if signup_method == "traditional" else "signing up with Google"
        
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=to_email,
            subject="Welcome to Mentor Connect! 🎉",
            html_content=f"""
            <!-- Your existing HTML template here -->
            """
        )
        
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"✅ Welcome email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Error sending welcome email: {e}")
        return False
```

---

### Option 4: Use Mailgun (Alternative to SendGrid)

Similar to SendGrid but with different pricing structure.

#### Step 1: Create Mailgun Account
1. Go to https://www.mailgun.com/
2. Sign up for free account (5,000 emails/month free for 3 months)
3. Verify your domain or use sandbox domain
4. Get API key from Settings → API Keys

#### Step 2: Install Mailgun
```bash
pip install mailgun
pip freeze > requirements.txt
```

#### Step 3: Update Configuration
Similar to SendGrid implementation above.

---

## Quick Test Script

Create `test_email.py` to test email sending:

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "mentorship@wazireducationsociety.com"
SMTP_PASSWORD = "your-app-password-here"  # Replace with new password

def test_email():
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_EMAIL
        msg['To'] = SMTP_EMAIL  # Send to yourself for testing
        msg['Subject'] = "Test Email - Mentor Connect"
        
        body = "<h1>Test Email</h1><p>If you receive this, SMTP is working!</p>"
        msg.attach(MIMEText(body, 'html'))
        
        print("Connecting to SMTP server...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.set_debuglevel(1)  # Show detailed logs
        
        print("Starting TLS...")
        server.starttls()
        
        print("Logging in...")
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        
        print("Sending email...")
        server.send_message(msg)
        
        print("Closing connection...")
        server.quit()
        
        print("✅ Email sent successfully!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_email()
```

Run the test:
```bash
python test_email.py
```

---

## Troubleshooting

### Error: "Username and Password not accepted"
- ✅ Verify 2FA is enabled on Gmail account
- ✅ Generate new App Password
- ✅ Use the App Password, not your regular Gmail password
- ✅ Remove spaces from App Password (xxxxxxxxxxxx not xxxx xxxx xxxx xxxx)

### Error: "SMTP AUTH extension not supported"
- ✅ Verify you're using port 587 (not 465 or 25)
- ✅ Verify STARTTLS is called before login

### Error: "Connection refused"
- ✅ Check firewall settings
- ✅ Verify internet connection
- ✅ Try different network (some networks block SMTP)

### Error: "Timeout"
- ✅ Check network connectivity
- ✅ Verify SMTP server address
- ✅ Try increasing timeout value

### Emails Going to Spam
- ✅ Set up SPF record for your domain
- ✅ Set up DKIM signing
- ✅ Use verified sender email
- ✅ Avoid spam trigger words
- ✅ Consider using SendGrid/Mailgun (better deliverability)

---

## Recommended Solution

**For Development/Testing:**
- Use Option 1 (Fix Gmail App Password) - Quick and easy

**For Production:**
- Use Option 3 (SendGrid) or Option 4 (Mailgun)
- Better deliverability
- Better analytics
- More reliable
- Professional email service
- Easier to scale

---

## Next Steps

1. **Immediate Fix (5 minutes):**
   - Generate new Gmail App Password
   - Update `app.py` with new password
   - Test with `test_email.py`

2. **Better Practice (10 minutes):**
   - Create `.env` file
   - Move credentials to environment variables
   - Update `.gitignore`

3. **Production Ready (30 minutes):**
   - Sign up for SendGrid
   - Install SendGrid library
   - Update email functions
   - Test thoroughly

---

## Security Best Practices

✅ **DO:**
- Use environment variables for credentials
- Use App Passwords (not main password)
- Add `.env` to `.gitignore`
- Use TLS/SSL encryption
- Rotate passwords regularly

❌ **DON'T:**
- Commit passwords to Git
- Share App Passwords
- Use "Less secure app access"
- Hardcode credentials in code
- Use plain text passwords

---

## Support

If you continue to have issues:
1. Check Gmail account security settings
2. Verify 2FA is enabled
3. Try generating a new App Password
4. Test with the `test_email.py` script
5. Consider switching to SendGrid for production

