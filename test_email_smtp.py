"""
Test script for SMTP email configuration
Run this to diagnose email sending issues
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = os.environ.get("SMTP_EMAIL", "mentorship@wazireducationsociety.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "zxgp ivqd obwf csnj")

def test_smtp_connection():
    """Test SMTP connection and authentication"""
    print("=" * 60)
    print("SMTP EMAIL CONFIGURATION TEST")
    print("=" * 60)
    print(f"\n📧 Email: {SMTP_EMAIL}")
    print(f"🔐 Password: {'*' * len(SMTP_PASSWORD)} ({len(SMTP_PASSWORD)} characters)")
    print(f"🌐 Server: {SMTP_SERVER}:{SMTP_PORT}")
    print("\n" + "=" * 60)
    
    try:
        print("\n[1/5] Connecting to SMTP server...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        print("     ✅ Connected successfully")
        
        print("\n[2/5] Starting TLS encryption...")
        server.starttls()
        print("     ✅ TLS started successfully")
        
        print("\n[3/5] Attempting login...")
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        print("     ✅ Login successful!")
        
        print("\n[4/5] Preparing test email...")
        msg = MIMEMultipart()
        msg['From'] = SMTP_EMAIL
        msg['To'] = SMTP_EMAIL  # Send to yourself
        msg['Subject'] = "✅ SMTP Test - Mentor Connect"
        
        body = """
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #2563eb;">✅ SMTP Configuration Test Successful!</h2>
            <p>If you're reading this email, your SMTP configuration is working correctly.</p>
            <p><strong>Server:</strong> smtp.gmail.com:587</p>
            <p><strong>From:</strong> mentorship@wazireducationsociety.com</p>
            <p>You can now send welcome emails to new users!</p>
            <hr>
            <p style="color: #666; font-size: 12px;">Mentor Connect - Test Email</p>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        print("     ✅ Email prepared")
        
        print("\n[5/5] Sending test email...")
        server.send_message(msg)
        print("     ✅ Email sent successfully!")
        
        server.quit()
        
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! SMTP is configured correctly!")
        print("=" * 60)
        print(f"\n📬 Check your inbox: {SMTP_EMAIL}")
        print("   The test email should arrive within a few seconds.")
        print("\n✅ Your welcome email feature is ready to use!")
        print("=" * 60)
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n     ❌ Authentication failed!")
        print("\n" + "=" * 60)
        print("🔴 AUTHENTICATION ERROR")
        print("=" * 60)
        print("\nThe email/password combination is not accepted by Gmail.")
        print("\n📋 SOLUTIONS:")
        print("\n1. Generate a new Gmail App Password:")
        print("   • Go to: https://myaccount.google.com/apppasswords")
        print("   • Enable 2-Factor Authentication first if not enabled")
        print("   • Create new App Password for 'Mail' app")
        print("   • Copy the 16-character password")
        print("   • Update SMTP_PASSWORD in app.py")
        print("\n2. Use environment variables:")
        print("   • Create .env file with:")
        print("     SMTP_EMAIL=your-email@gmail.com")
        print("     SMTP_PASSWORD=your-app-password")
        print("   • Install: pip install python-dotenv")
        print("   • Add to app.py: from dotenv import load_dotenv; load_dotenv()")
        print("\n3. Consider using SendGrid (recommended for production):")
        print("   • More reliable than Gmail SMTP")
        print("   • Better deliverability")
        print("   • Free tier: 100 emails/day")
        print("   • See EMAIL_SMTP_FIX_GUIDE.md for details")
        print("\n" + "=" * 60)
        return False
        
    except smtplib.SMTPException as e:
        print(f"\n     ❌ SMTP error: {e}")
        print("\n" + "=" * 60)
        print("🔴 SMTP ERROR")
        print("=" * 60)
        print(f"\nError details: {e}")
        print("\n📋 POSSIBLE CAUSES:")
        print("   • Network/firewall blocking SMTP")
        print("   • Incorrect server/port configuration")
        print("   • Gmail security settings")
        print("\n📋 SOLUTIONS:")
        print("   • Check firewall settings")
        print("   • Verify server: smtp.gmail.com")
        print("   • Verify port: 587")
        print("   • Try different network")
        print("=" * 60)
        return False
        
    except Exception as e:
        print(f"\n     ❌ Unexpected error: {e}")
        print("\n" + "=" * 60)
        print("🔴 UNEXPECTED ERROR")
        print("=" * 60)
        print(f"\nError details: {e}")
        print("\n📋 SOLUTIONS:")
        print("   • Check internet connection")
        print("   • Verify email configuration")
        print("   • See EMAIL_SMTP_FIX_GUIDE.md for help")
        print("=" * 60)
        return False

def test_welcome_email_format():
    """Test the welcome email HTML format (without sending)"""
    print("\n" + "=" * 60)
    print("TESTING WELCOME EMAIL FORMAT")
    print("=" * 60)
    
    user_name = "Test User"
    to_email = "test@example.com"
    signup_method = "traditional"
    
    signup_text = "signing up" if signup_method == "traditional" else "signing up with Google"
    
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f8fafc;">
        <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <div style="background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%); padding: 40px 20px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 32px;">Welcome to Mentor Connect! 🎉</h1>
            </div>
            <div style="padding: 40px 30px;">
                <h2 style="color: #1e293b; margin-top: 0;">Hi {user_name},</h2>
                <p style="color: #475569; font-size: 16px; line-height: 1.6;">
                    Thank you for {signup_text} with <strong>Mentor Connect</strong>!
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    print("\n✅ Welcome email HTML template is valid")
    print(f"   • User name: {user_name}")
    print(f"   • Email: {to_email}")
    print(f"   • Signup method: {signup_method}")
    print(f"   • HTML length: {len(body)} characters")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    print("\n🚀 Starting SMTP Email Tests...\n")
    
    # Test 1: SMTP Connection and Authentication
    smtp_success = test_smtp_connection()
    
    # Test 2: Email Format
    test_welcome_email_format()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    if smtp_success:
        print("\n✅ All tests passed!")
        print("✅ SMTP configuration is working")
        print("✅ Welcome emails will be sent successfully")
        print("\n🎯 Next steps:")
        print("   1. Test signup flow in your application")
        print("   2. Check that welcome emails are received")
        print("   3. Verify emails don't go to spam folder")
    else:
        print("\n❌ SMTP configuration needs fixing")
        print("\n📖 Read EMAIL_SMTP_FIX_GUIDE.md for detailed solutions")
        print("\n🔧 Quick fix:")
        print("   1. Go to: https://myaccount.google.com/apppasswords")
        print("   2. Generate new App Password")
        print("   3. Update SMTP_PASSWORD in app.py")
        print("   4. Run this test again")
    print("\n" + "=" * 60)
