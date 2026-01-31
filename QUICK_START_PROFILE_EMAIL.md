# Quick Start Guide - Profile Completion Email Feature

## 🚀 Get Started in 3 Steps

### Step 1: Apply Database Migration
```bash
flask db upgrade
```

This adds the `profile_completion_email_sent` column to your User table.

### Step 2: Verify SMTP Settings
Check `app.py` has valid SMTP configuration:
```python
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"
```

### Step 3: Test It!
1. Create a new user account (any type: Mentor/Mentee/Supervisor/Institution)
2. Complete the profile (fill ALL fields + upload profile picture)
3. Submit the form
4. Check email inbox for congratulations message ✉️

---

## ✅ What This Feature Does

- Sends automatic email when user completes profile for the first time
- Email is personalized with user's name and role
- Includes role-specific next steps
- **Never sent again** on future profile edits
- Works for all 4 user types

---

## 🧪 Testing Tools

### Option 1: Manual Test
Just complete a profile and check email!

### Option 2: Test Script
```bash
python test_profile_completion_email.py
```

Interactive menu to:
- Check profile completion status
- See who received emails
- Find incomplete profiles
- Reset flags for testing
- Send test emails

---

## 🔍 How to Check It's Working

### Console Logs
When profile is completed, you'll see:
```
✅ Profile completion email sent to user@example.com
```

### Database Check
```sql
SELECT name, email, profile_completion_email_sent 
FROM user 
WHERE profile_completion_email_sent = 1;
```

---

## 📧 Email Preview

Users receive a professional HTML email with:
- 🎉 Congratulations message
- Personalized greeting
- Role-specific action items
- "Go to Dashboard" button
- Support contact info

---

## ⚠️ Important Notes

1. **Profile Picture Required**: Must upload picture for profile to be complete
2. **All Fields Required**: Every mandatory field must be filled
3. **One-Time Only**: Email sent once, never again
4. **Backend Only**: No UI changes needed

---

## 🆘 Troubleshooting

### Email Not Received?
- Check SMTP settings in app.py
- Check spam folder
- Look for error in console logs
- Verify profile is actually complete (all fields + picture)

### Want to Test Again?
Use test script to reset the email flag:
```bash
python test_profile_completion_email.py
# Choose option 4, enter user email
```

---

## 📚 Full Documentation

For complete details, see:
- `PROFILE_COMPLETION_EMAIL_FEATURE.md` - Technical documentation
- `PROFILE_COMPLETION_EMAIL_SUMMARY.md` - Implementation summary

---

## ✨ That's It!

The feature is ready to use. Just apply the migration and start testing!

**Questions?** Check the full documentation or console logs for details.
