"""
Test script for Profile Completion Email Feature
Run this script to verify the email feature is working correctly
"""

from app import app, db, User, MentorProfile, MenteeProfile, SupervisorProfile, Institution
from app import check_profile_complete, send_profile_completion_email

def test_profile_completion_check():
    """Test the profile completion check function"""
    print("\n" + "="*60)
    print("TESTING PROFILE COMPLETION CHECK")
    print("="*60)
    
    with app.app_context():
        # Test for each user type
        user_types = {
            "0": "Supervisor",
            "1": "Mentor", 
            "2": "Mentee",
            "3": "Institution"
        }
        
        for user_type, role_name in user_types.items():
            print(f"\n{role_name} (user_type={user_type}):")
            print("-" * 40)
            
            # Find a user of this type
            user = User.query.filter_by(user_type=user_type).first()
            
            if user:
                is_complete = check_profile_complete(user.id, user_type)
                email_sent = user.profile_completion_email_sent
                
                print(f"✓ User found: {user.name} ({user.email})")
                print(f"  Profile Complete: {'✅ Yes' if is_complete else '❌ No'}")
                print(f"  Email Sent: {'✅ Yes' if email_sent else '❌ No'}")
                
                if is_complete and not email_sent:
                    print(f"  ⚠️  Profile complete but email not sent!")
                    print(f"     This user should receive email on next profile edit.")
            else:
                print(f"❌ No {role_name} user found in database")

def test_email_sent_flag():
    """Check which users have received the profile completion email"""
    print("\n" + "="*60)
    print("USERS WHO RECEIVED PROFILE COMPLETION EMAIL")
    print("="*60)
    
    with app.app_context():
        users_with_email = User.query.filter_by(profile_completion_email_sent=True).all()
        
        if users_with_email:
            print(f"\nFound {len(users_with_email)} user(s) who received email:\n")
            for user in users_with_email:
                role_names = {
                    "0": "Supervisor",
                    "1": "Mentor",
                    "2": "Mentee",
                    "3": "Institution"
                }
                role = role_names.get(user.user_type, "Unknown")
                print(f"  • {user.name} ({user.email}) - {role}")
        else:
            print("\n❌ No users have received the profile completion email yet.")

def test_incomplete_profiles():
    """Find users with incomplete profiles"""
    print("\n" + "="*60)
    print("USERS WITH INCOMPLETE PROFILES")
    print("="*60)
    
    with app.app_context():
        all_users = User.query.all()
        incomplete_users = []
        
        for user in all_users:
            is_complete = check_profile_complete(user.id, user.user_type)
            if not is_complete:
                incomplete_users.append(user)
        
        if incomplete_users:
            print(f"\nFound {len(incomplete_users)} user(s) with incomplete profiles:\n")
            
            role_names = {
                "0": "Supervisor",
                "1": "Mentor",
                "2": "Mentee",
                "3": "Institution"
            }
            
            for user in incomplete_users:
                role = role_names.get(user.user_type, "Unknown")
                print(f"  • {user.name} ({user.email}) - {role}")
                print(f"    → Complete profile to trigger email")
        else:
            print("\n✅ All users have complete profiles!")

def reset_email_flag(email):
    """Reset the email sent flag for a specific user (for testing)"""
    print("\n" + "="*60)
    print("RESET EMAIL FLAG")
    print("="*60)
    
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        
        if user:
            user.profile_completion_email_sent = False
            db.session.commit()
            print(f"\n✅ Reset email flag for: {user.name} ({user.email})")
            print(f"   User will receive email on next profile completion.")
        else:
            print(f"\n❌ User not found with email: {email}")

def send_test_email(email):
    """Send a test profile completion email"""
    print("\n" + "="*60)
    print("SEND TEST EMAIL")
    print("="*60)
    
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        
        if user:
            print(f"\nSending test email to: {user.name} ({user.email})")
            print(f"User type: {user.user_type}")
            
            success = send_profile_completion_email(user.email, user.name, user.user_type)
            
            if success:
                print("\n✅ Test email sent successfully!")
                print("   Check the inbox for the email.")
            else:
                print("\n❌ Failed to send test email.")
                print("   Check SMTP configuration in app.py")
        else:
            print(f"\n❌ User not found with email: {email}")

def main():
    """Main test menu"""
    print("\n" + "="*60)
    print("PROFILE COMPLETION EMAIL FEATURE - TEST SCRIPT")
    print("="*60)
    
    while True:
        print("\n\nSelect a test option:")
        print("1. Check profile completion status for all user types")
        print("2. List users who received profile completion email")
        print("3. Find users with incomplete profiles")
        print("4. Reset email flag for a user (for testing)")
        print("5. Send test email to a user")
        print("6. Run all tests")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-6): ").strip()
        
        if choice == "1":
            test_profile_completion_check()
        elif choice == "2":
            test_email_sent_flag()
        elif choice == "3":
            test_incomplete_profiles()
        elif choice == "4":
            email = input("Enter user email: ").strip()
            reset_email_flag(email)
        elif choice == "5":
            email = input("Enter user email: ").strip()
            send_test_email(email)
        elif choice == "6":
            test_profile_completion_check()
            test_email_sent_flag()
            test_incomplete_profiles()
        elif choice == "0":
            print("\n👋 Exiting test script. Goodbye!")
            break
        else:
            print("\n❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
