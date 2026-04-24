# Change Admin Password

## Local Database
✅ **COMPLETED** - Password changed successfully on local database

**Admin Details:**
- Email: `info@wazireducationsocity.com`
- User ID: 201
- User Type: 0 (Supervisor)
- New Password: `X7m#Q2vL9@pR4!Ks`

## Production Database

### Steps to Change Password on Production:

1. **SSH into production server:**
```bash
ssh naved20@ip-172-31-17-49.eu-north-1.compute.internal
```

2. **Navigate to project directory:**
```bash
cd /home/luxment/htdocs/mentorship.weslux.lu/WES-Working
```

3. **Pull latest code:**
```bash
git pull origin main
```

4. **Activate virtual environment (if needed):**
```bash
source venv/bin/activate
# or
source .venv/bin/activate
```

5. **Run the password change script:**
```bash
python3 change_admin_password_production.py
```

6. **Verify the output:**
You should see:
```
============================================================
PRODUCTION PASSWORD CHANGE
============================================================
✅ Found admin user: WES (info@wazireducationsocity.com)
   User ID: 201
   User Type: 0

✅ Password changed successfully on PRODUCTION!
   New password: X7m#Q2vL9@pR4!Ks
   Email: info@wazireducationsocity.com

⚠️  IMPORTANT: Save this password securely!
============================================================
```

7. **Test the new password:**
- Go to https://mentorship.weslux.lu/signin
- Login with:
  - Email: `info@wazireducationsocity.com`
  - Password: `X7m#Q2vL9@pR4!Ks`

## Security Notes

⚠️ **IMPORTANT:**
- This password is very strong with special characters
- Save it in a secure password manager
- Do not share via insecure channels
- Consider changing it again if needed through the UI

## Password Requirements Met:
✅ At least 8 characters
✅ Contains uppercase letters (X, Q, L, R, K)
✅ Contains lowercase letters (m, v, p, s)
✅ Contains numbers (7, 2, 9, 4)
✅ Contains special characters (#, @, !)

## Cleanup (Optional)
After successfully changing password on production, you can delete these files:
- `change_admin_password.py`
- `change_admin_password_production.py`
- `CHANGE_ADMIN_PASSWORD.md`
