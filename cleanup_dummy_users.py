"""
Script to remove all dummy users and their related data
Removes users with emails containing 'example.com' and 'xexample.com'
"""

from app import app, db, User, MenteeProfile, MentorProfile, SupervisorProfile, Institution, MentorshipRequest, MeetingRequest, PersonalTask, MenteeTask, TaskRating
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
        
        print(f"Found {len(dummy_users)} dummy users to delete")
        
        if len(dummy_users) == 0:
            print("✅ No dummy users found. Nothing to delete.")
            return
        
        user_ids = [user.id for user in dummy_users]
        user_emails = [user.email for user in dummy_users]
        
        print(f"\nUsers to be deleted:")
        for email in user_emails:
            print(f"  - {email}")
        
        # Auto-confirm for script execution
        print("\n⚠️  Proceeding with deletion...")
        
        print("\n🔄 Deleting related data...")
        
        # Delete in order of dependencies
        try:
            # 1. Delete ChatMessages (if Chat system exists)
            try:
                from app import Chat, ChatMessage
                chat_messages = ChatMessage.query.filter(
                    or_(
                        ChatMessage.sender_id.in_(user_ids),
                        ChatMessage.receiver_id.in_(user_ids)
                    )
                ).delete(synchronize_session=False)
                print(f"  ✓ Deleted {chat_messages} chat messages")
                
                # 2. Delete Chats
                chats = Chat.query.filter(
                    or_(
                        Chat.user1_id.in_(user_ids),
                        Chat.user2_id.in_(user_ids)
                    )
                ).delete(synchronize_session=False)
                print(f"  ✓ Deleted {chats} chats")
            except ImportError:
                print(f"  ⊘ Chat system not yet implemented")
            
            # 3. Delete TaskRatings
            task_ratings = TaskRating.query.filter(
                or_(
                    TaskRating.mentor_id.in_(user_ids),
                    TaskRating.mentee_id.in_(user_ids)
                )
            ).delete(synchronize_session=False)
            print(f"  ✓ Deleted {task_ratings} task ratings")
            
            # 4. Delete MeetingRequests
            meeting_requests = MeetingRequest.query.filter(
                or_(
                    MeetingRequest.requester_id.in_(user_ids),
                    MeetingRequest.requested_to_id.in_(user_ids),
                    MeetingRequest.rescheduled_by_id.in_(user_ids)
                )
            ).delete(synchronize_session=False)
            print(f"  ✓ Deleted {meeting_requests} meeting requests")
            
            # 5. Delete MentorshipRequests
            mentorships = MentorshipRequest.query.filter(
                or_(
                    MentorshipRequest.mentee_id.in_(user_ids),
                    MentorshipRequest.mentor_id.in_(user_ids)
                )
            ).delete(synchronize_session=False)
            print(f"  ✓ Deleted {mentorships} mentorship requests")
            
            # 6. Delete PersonalTasks (for mentors)
            personal_tasks = PersonalTask.query.filter(
                PersonalTask.mentor_id.in_(user_ids)
            ).delete(synchronize_session=False)
            print(f"  ✓ Deleted {personal_tasks} personal tasks")
            
            # 7. Delete MenteeTasks (for mentees)
            mentee_tasks = MenteeTask.query.filter(
                MenteeTask.mentee_id.in_(user_ids)
            ).delete(synchronize_session=False)
            print(f"  ✓ Deleted {mentee_tasks} mentee tasks")
            
            # 8. Delete MenteeProfiles
            mentee_profiles = MenteeProfile.query.filter(
                MenteeProfile.user_id.in_(user_ids)
            ).delete(synchronize_session=False)
            print(f"  ✓ Deleted {mentee_profiles} mentee profiles")
            
            # 9. Delete MentorProfiles
            mentor_profiles = MentorProfile.query.filter(
                MentorProfile.user_id.in_(user_ids)
            ).delete(synchronize_session=False)
            print(f"  ✓ Deleted {mentor_profiles} mentor profiles")
            
            # 10. Delete SupervisorProfiles
            supervisor_profiles = SupervisorProfile.query.filter(
                SupervisorProfile.user_id.in_(user_ids)
            ).delete(synchronize_session=False)
            print(f"  ✓ Deleted {supervisor_profiles} supervisor profiles")
            
            # 11. Delete Institutions created by these users
            institutions = Institution.query.filter(
                Institution.user_id.in_(user_ids)
            ).delete(synchronize_session=False)
            print(f"  ✓ Deleted {institutions} institutions")
            
            # 12. Finally, delete Users
            users_deleted = User.query.filter(
                User.id.in_(user_ids)
            ).delete(synchronize_session=False)
            print(f"  ✓ Deleted {users_deleted} users")
            
            # Commit all changes
            db.session.commit()
            
            print(f"\n✅ Successfully deleted {users_deleted} users and all their related data!")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error during deletion: {str(e)}")
            raise

if __name__ == "__main__":
    cleanup_dummy_users()
