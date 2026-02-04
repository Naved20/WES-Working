"""
Script to remove all dummy users and their related data
Removes users with emails containing 'example.com' and 'xexample.com'
"""

from app import app, db, User, MenteeProfile, MentorProfile, SupervisorProfile, Institution
from sqlalchemy import or_

def cleanup_dummy_users():
    with app.app_context():
        print("🗑️  Starting cleanup of dummy users...")
        
        # Find all users with example.com or xexample.com emails
        dummy_users = User.query.filter(
            or_(
                User.email.like('%@example.com'),
                User.email.like('%@xexample.com')
            )
        ).all()
        
        print(f"\n📊 Found {len(dummy_users)} dummy users to remove")
        
        if len(dummy_users) == 0:
            print("✅ No dummy users found. Database is clean!")
            return
        
        # Count by user type
        mentees = [u for u in dummy_users if u.user_type == "2"]
        mentors = [u for u in dummy_users if u.user_type == "1"]
        supervisors = [u for u in dummy_users if u.user_type == "0"]
        institutions = [u for u in dummy_users if u.user_type == "3"]
        
        print(f"  - Mentees: {len(mentees)}")
        print(f"  - Mentors: {len(mentors)}")
        print(f"  - Supervisors: {len(supervisors)}")
        print(f"  - Institution Admins: {len(institutions)}")
        
        # Delete related data for each user
        deleted_count = {
            'users': 0,
            'mentee_profiles': 0,
            'mentor_profiles': 0,
            'supervisor_profiles': 0
        }
        
        for user in dummy_users:
            user_id = user.id
            email = user.email
            
            # Delete MenteeProfile
            mentee_profile = MenteeProfile.query.filter_by(user_id=user_id).first()
            if mentee_profile:
                db.session.delete(mentee_profile)
                deleted_count['mentee_profiles'] += 1
            
            # Delete MentorProfile
            mentor_profile = MentorProfile.query.filter_by(user_id=user_id).first()
            if mentor_profile:
                db.session.delete(mentor_profile)
                deleted_count['mentor_profiles'] += 1
            
            # Delete SupervisorProfile
            supervisor_profile = SupervisorProfile.query.filter_by(user_id=user_id).first()
            if supervisor_profile:
                db.session.delete(supervisor_profile)
                deleted_count['supervisor_profiles'] += 1
            
            # Delete User
            db.session.delete(user)
            deleted_count['users'] += 1
            
            print(f"  ✓ Deleted user: {email}")
        
        # Commit all deletions
        db.session.commit()
        
        print(f"\n✅ Cleanup completed successfully!")
        print(f"\n📈 Deletion Summary:")
        print(f"  - Users deleted: {deleted_count['users']}")
        print(f"  - Mentee profiles deleted: {deleted_count['mentee_profiles']}")
        print(f"  - Mentor profiles deleted: {deleted_count['mentor_profiles']}")
        print(f"  - Supervisor profiles deleted: {deleted_count['supervisor_profiles']}")
        
        # Show remaining user count
        remaining_users = User.query.count()
        print(f"\n📊 Remaining users in database: {remaining_users}")

if __name__ == "__main__":
    cleanup_dummy_users()
