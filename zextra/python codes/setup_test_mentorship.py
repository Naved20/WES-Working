#!/usr/bin/env python
"""Setup test mentorship relationship"""

from app import app, db, User, MentorshipRequest

print("=" * 60)
print("SETTING UP TEST MENTORSHIP")
print("=" * 60)

with app.app_context():
    # Get a mentee and mentor
    mentee = User.query.filter_by(user_type="2").first()
    mentor = User.query.filter_by(user_type="1").first()
    
    if not mentee or not mentor:
        print("❌ Could not find mentee or mentor!")
        exit(1)
    
    print(f"\nMentee: {mentee.name} (ID: {mentee.id})")
    print(f"Mentor: {mentor.name} (ID: {mentor.id})")
    
    # Check if mentorship already exists
    existing = MentorshipRequest.query.filter_by(
        mentee_id=mentee.id,
        mentor_id=mentor.id
    ).first()
    
    if existing:
        print(f"\n⚠️ Mentorship already exists with status: {existing.final_status}")
        if existing.final_status != "approved":
            print("Updating to approved...")
            existing.final_status = "approved"
            existing.mentor_status = "accepted"
            existing.supervisor_status = "approved"
            db.session.commit()
            print("✅ Updated to approved!")
    else:
        # Create new mentorship request
        print("\nCreating new mentorship request...")
        mr = MentorshipRequest(
            mentee_id=mentee.id,
            mentor_id=mentor.id,
            purpose="Testing chat system",
            mentor_type="anchor",
            term="long",
            duration_months=6,
            why_need_mentor="Testing",
            mentor_status="accepted",
            supervisor_status="approved",
            final_status="approved"
        )
        db.session.add(mr)
        db.session.commit()
        print(f"✅ Mentorship created (ID: {mr.id})")
    
    # Verify
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)
    
    mentorship = MentorshipRequest.query.filter_by(
        mentee_id=mentee.id,
        mentor_id=mentor.id,
        final_status="approved"
    ).first()
    
    if mentorship:
        print(f"✅ Approved mentorship confirmed!")
        print(f"   Mentee: {mentee.name}")
        print(f"   Mentor: {mentor.name}")
        print(f"   Status: {mentorship.final_status}")
    else:
        print("❌ Mentorship not approved!")
        exit(1)
    
    print("\n" + "=" * 60)
    print("✅ TEST MENTORSHIP SETUP COMPLETE")
    print("=" * 60)
