from app import db, app
from app import MentorshipRequest

with app.app_context():
    try:

        
        # Clear all data from mentee_tasks  
        db.session.query(MentorshipRequest).delete()
        print("✅ Cleared all mentee_tasks data")
        
        db.session.commit()
        print("🎉 Both tables data cleared successfully!")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {e}")