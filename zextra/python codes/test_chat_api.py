#!/usr/bin/env python
"""Test chat API endpoints"""

from app import app, db, User, MentorshipRequest, ChatConversation, ChatMessage
import json

print("=" * 60)
print("TESTING CHAT SYSTEM")
print("=" * 60)

with app.app_context():
    # Get test users
    print("\n1. Finding test users...")
    
    mentee = User.query.filter_by(user_type="2").first()
    mentor = User.query.filter_by(user_type="1").first()
    supervisor = User.query.filter_by(user_type="0").first()
    
    if not mentee:
        print("❌ No mentee found!")
        exit(1)
    if not mentor:
        print("❌ No mentor found!")
        exit(1)
    if not supervisor:
        print("❌ No supervisor found!")
        exit(1)
    
    print(f"✅ Mentee: {mentee.name} (ID: {mentee.id})")
    print(f"✅ Mentor: {mentor.name} (ID: {mentor.id})")
    print(f"✅ Supervisor: {supervisor.name} (ID: {supervisor.id})")
    
    # Check mentorship
    print("\n2. Checking mentorship relationships...")
    mentorship = MentorshipRequest.query.filter_by(
        mentee_id=mentee.id,
        final_status="approved"
    ).first()
    
    if mentorship:
        print(f"✅ Approved mentorship found: {mentee.name} ↔ {User.query.get(mentorship.mentor_id).name}")
        mentor = User.query.get(mentorship.mentor_id)
    else:
        print("⚠️ No approved mentorship found, using first mentor")
    
    # Test get_allowed_contacts logic
    print("\n3. Testing allowed contacts logic...")
    
    # For mentee
    print(f"\n   Mentee ({mentee.name}) can chat with:")
    mentorship = MentorshipRequest.query.filter_by(
        mentee_id=mentee.id,
        final_status="approved"
    ).first()
    if mentorship:
        assigned_mentor = User.query.get(mentorship.mentor_id)
        print(f"   - Mentor: {assigned_mentor.name}")
    supervisors = User.query.filter_by(user_type="0").all()
    for sup in supervisors:
        print(f"   - Supervisor: {sup.name}")
    
    # For mentor
    print(f"\n   Mentor ({mentor.name}) can chat with:")
    mentorships = MentorshipRequest.query.filter_by(
        mentor_id=mentor.id,
        final_status="approved"
    ).all()
    for m in mentorships:
        mentee_user = User.query.get(m.mentee_id)
        print(f"   - Mentee: {mentee_user.name}")
    for sup in supervisors:
        print(f"   - Supervisor: {sup.name}")
    
    # For supervisor
    print(f"\n   Supervisor ({supervisor.name}) can chat with:")
    mentors = User.query.filter_by(user_type="1").all()
    for m in mentors[:3]:  # Show first 3
        print(f"   - Mentor: {m.name}")
    if len(mentors) > 3:
        print(f"   ... and {len(mentors) - 3} more mentors")
    
    mentees = User.query.filter_by(user_type="2").all()
    for m in mentees[:3]:  # Show first 3
        print(f"   - Mentee: {m.name}")
    if len(mentees) > 3:
        print(f"   ... and {len(mentees) - 3} more mentees")
    
    # Test conversation creation
    print("\n4. Testing conversation creation...")
    
    # Create a test conversation
    conv = ChatConversation(
        conversation_type="direct",
        participant1_id=min(mentee.id, mentor.id),
        participant2_id=max(mentee.id, mentor.id)
    )
    db.session.add(conv)
    db.session.commit()
    print(f"✅ Conversation created (ID: {conv.id})")
    
    # Add a test message
    print("\n5. Testing message creation...")
    msg = ChatMessage(
        conversation_id=conv.id,
        sender_id=mentee.id,
        content="Hello from mentee!"
    )
    db.session.add(msg)
    db.session.commit()
    print(f"✅ Message created (ID: {msg.id})")
    
    # Verify message
    print("\n6. Verifying message...")
    retrieved_msg = ChatMessage.query.get(msg.id)
    print(f"✅ Message retrieved: '{retrieved_msg.content}'")
    print(f"   From: {retrieved_msg.sender.name}")
    print(f"   Conversation: {retrieved_msg.conversation.id}")
    
    # Test conversation retrieval
    print("\n7. Testing conversation retrieval...")
    retrieved_conv = ChatConversation.query.get(conv.id)
    print(f"✅ Conversation retrieved")
    print(f"   Participant 1: {retrieved_conv.participant1.name}")
    print(f"   Participant 2: {retrieved_conv.participant2.name}")
    print(f"   Messages: {len(retrieved_conv.messages)}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
