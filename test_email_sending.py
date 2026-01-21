"""
Test script to verify SMTP email configuration
Run this before testing the forgot password feature
"""

from app import app, send_otp_email

def test_email():
    print("\n" + "="*60)
    print("📧 TESTING EMAIL CONFIGURATION")
    print("="*60 + "\n")
    
    # Get test email from user
    test_email = input("Enter your email address to receive test OTP: ").strip()
    
    if not test_email:
        print("❌ No email provided. Exiting.")
        return
    
    print(f"\n📤 Sending test OTP to: {test_email}")
    print("⏳ Please wait...\n")
    
    with app.app_context():
        # Send test OTP
        test_otp = "123456"
        result = send_otp_email(test_email, test_otp)
        
        if result:
            print("✅ SUCCESS! Email sent successfully!")
            print(f"📬 Check your inbox at: {test_email}")
            print(f"🔢 Test OTP: {test_otp}")
            print("\n✨ Your SMTP configuration is working correctly!")
            print("✨ You can now use the forgot password feature.")
        else:
            print("❌ FAILED! Email could not be sent.")
            print("\n🔍 Troubleshooting steps:")
            print("1. Check SMTP_EMAIL and SMTP_PASSWORD in app.py")
            print("2. Verify you're using Gmail App Password (not regular password)")
            print("3. Ensure 2FA is enabled on your Gmail account")
            print("4. Check console above for specific error messages")
            print("5. See SMTP_CONFIGURATION_GUIDE.md for detailed setup")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    test_email()
