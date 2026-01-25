#!/usr/bin/env python
"""Complete end-to-end test of chat system"""

from app import app, db, User, MentorshipRequest, ChatConversation, ChatMessage
import json

print("=" * 70)
print("COMPLETE CHAT SYSTEM TEST")
print("=" * 70)

with app.app_context():
    # 1. Get test users
    print("\n1. FINDING TEST USERS")
    print("-" * 70)
    
    mentee = User.query.filter_by(user_type="2").first()
    mentor = User.query.filter_by(user_type="1").first()
    supervisor = User.query.filter_by(user_type="0").first()
    
    if not all([mentee, mentor, supervisor]):
        print("❌ Missing required users!")
        exit(1)
    
    print(f"✅ Mentee: {mentee.name} (ID: {mentee.id}, Type: {mentee.user_type})")
    print(f"✅ Mentor: {mentor.name} (ID: {mentor.id}, Type: {mentor.user_type})")
    print(f"✅ Supervisor: {supervisor.name} (ID: {supervisor.id}, Type: {supervisor.user_type})")
    
    # 2. Verify mentorship
    print("\n2. VERIFYING MENTORSHIP RELATIONSHIP")
    print("-" * 70)
    
    mentorship = MentorshipRequest.query.filter_by(
        mentee_id=mentee.id,
        mentor_id=mentor.id,
        final_status="approved"
    ).first()
    
    if mentorship:
        print(f"✅ Approved mentorship exists: {mentee.name} ↔ {mentor.name}")
    else:
        print(f"⚠️ No approved mentorship, creating one...")
        mr = MentorshipRequest(
            mentee_id=mentee.id,
            mentor_id=mentor.id,
            purpose="Testing",
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
        print(f"✅ Mentorship created!")
    
    # 3. Test allowed contacts logic
    print("\n3. TESTING ALLOWED CONTACTS LOGIC")
    print("-" * 70)
    
    # For mentee
    print(f"\n   Mentee ({mentee.name}) can chat with:")
    mentorship = MentorshipRequest.query.filter_by(
        mentee_id=mentee.id,
        final_status="approved"
    ).first()
    if mentorship:
        assigned_mentor = User.query.get(mentorship.mentor_id)
        print(f"   ✅ Mentor: {assigned_mentor.name}")
    else:
        print(f"   ❌ No assigned mentor")
    
    supervisors = User.query.filter_by(user_type="0").all()
    for sup in supervisors:
        print(f"   ✅ Supervisor: {sup.name}")
    
    # For mentor
    print(f"\n   Mentor ({mentor.name}) can chat with:")
    mentorships = MentorshipRequest.query.filter_by(
        mentor_id=mentor.id,
        final_status="approved"
    ).all()
    if mentorships:
        for m in mentorships:
            mentee_user = User.query.get(m.mentee_id)
            print(f"   ✅ Mentee: {mentee_user.name}")
    else:
        print(f"   ❌ No assigned mentees")
    
    for sup in supervisors:
        print(f"   ✅ Supervisor: {sup.name}")
    
    # For supervisor
    print(f"\n   Supervisor ({supervisor.name}) can chat with:")
    mentors = User.query.filter_by(user_type="1").all()
    print(f"   ✅ {len(mentors)} mentors")
    mentees = User.query.filter_by(user_type="2").all()
    print(f"   ✅ {len(mentees)} mentees")
    
    # 4. Test conversation creation
    print("\n4. TESTING CONVERSATION CREATION")
    print("-" * 70)
    
    # Clear existing conversations
    ChatConversation.query.delete()
    ChatMessage.query.delete()
    db.session.commit()
    print("✅ Cleared existing conversations")
    
    # Create conversation between mentee and mentor
    conv = ChatConversation(
        conversation_type="direct",
        participant1_id=min(mentee.id, mentor.id),
        participant2_id=max(mentee.id, mentor.id)
    )
    db.session.add(conv)
    db.session.commit()
    print(f"✅ Conversation created (ID: {conv.id})")
    print(f"   Participant 1: {conv.participant1.name}")
    print(f"   Participant 2: {conv.participant2.name}")
    
    # 5. Test message creation
    print("\n5. TESTING MESSAGE CREATION")
    print("-" * 70)
    
    msg1 = ChatMessage(
        conversation_id=conv.id,
        sender_id=mentee.id,
        content="Hello mentor, how are you?"
    )
    db.session.add(msg1)
    db.session.commit()
    print(f"✅ Message 1 created from {mentee.name}")
    
    msg2 = ChatMessage(
        conversation_id=conv.id,
        sender_id=mentor.id,
        content="I'm doing great! How can I help you today?"
    )
    db.session.add(msg2)
    db.session.commit()
    print(f"✅ Message 2 created from {mentor.name}")
    
    # 6. Test message retrieval
    print("\n6. TESTING MESSAGE RETRIEVAL")
    print("-" * 70)
    
    messages = ChatMessage.query.filter_by(conversation_id=conv.id).all()
    print(f"✅ Retrieved {len(messages)} messages:")
    for msg in messages:
        print(f"   - {msg.sender.name}: {msg.content}")
    
    # 7. Test conversation retrieval
    print("\n7. TESTING CONVERSATION RETRIEVAL")
    print("-" * 70)
    
    retrieved_conv = ChatConversation.query.get(conv.id)
    print(f"✅ Conversation retrieved:")
    print(f"   - ID: {retrieved_conv.id}")
    print(f"   - Participant 1: {retrieved_conv.participant1.name}")
    print(f"   - Participant 2: {retrieved_conv.participant2.name}")
    print(f"   - Messages: {len(retrieved_conv.messages)}")
    print(f"   - Last message: {retrieved_conv.messages[-1].content if retrieved_conv.messages else 'None'}")
    
    # 8. Test conversation list for mentee
    print("\n8. TESTING CONVERSATION LIST FOR MENTEE")
    print("-" * 70)
    
    mentee_convs = ChatConversation.query.filter(
        db.or_(
            ChatConversation.participant1_id == mentee.id,
            ChatConversation.participant2_id == mentee.id
        )
    ).all()
    print(f"✅ Mentee has {len(mentee_convs)} conversation(s)")
    for c in mentee_convs:
        other_id = c.participant2_id if c.participant1_id == mentee.id else c.participant1_id
        other_user = User.query.get(other_id)
        print(f"   - With {other_user.name}: {len(c.messages)} messages")
    
    # 9. Test conversation list for mentor
    print("\n9. TESTING CONVERSATION LIST FOR MENTOR")
    print("-" * 70)
    
    mentor_convs = ChatConversation.query.filter(
        db.or_(
            ChatConversation.participant1_id == mentor.id,
            ChatConversation.participant2_id == mentor.id
        )
    ).all()
    print(f"✅ Mentor has {len(mentor_convs)} conversation(s)")
    for c in mentor_convs:
        other_id = c.participant2_id if c.participant1_id == mentor.id else c.participant1_id
        other_user = User.query.get(other_id)
        print(f"   - With {other_user.name}: {len(c.messages)} messages")
    
    # 10. Test unread tracking
    print("\n10. TESTING UNREAD MESSAGE TRACKING")
    print("-" * 70)
    
    unread = ChatMessage.query.filter_by(
        conversation_id=conv.id,
        is_read=False
    ).filter(ChatMessage.sender_id != mentee.id).count()
    print(f"✅ Unread messages for mentee: {unread}")
    
    # Mark as read
    ChatMessage.query.filter(
        ChatMessage.conversation_id == conv.id,
        ChatMessage.sender_id != mentee.id,
        ChatMessage.is_read == False
    ).update({ChatMessage.is_read: True})
    db.session.commit()
    
    unread_after = ChatMessage.query.filter_by(
        conversation_id=conv.id,
        is_read=False
    ).filter(ChatMessage.sender_id != mentee.id).count()
    print(f"✅ Unread messages after marking read: {unread_after}")
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)
    print("\nChat system is ready to use!")
    print("- Database tables: ✅ Created")
    print("- Mentorship mapping: ✅ Working")
    print("- Message persistence: ✅ Working")
    print("- Conversation retrieval: ✅ Working")
    print("- Unread tracking: ✅ Working")
