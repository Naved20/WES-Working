#!/usr/bin/env python
"""Test API endpoints with Flask test client"""

from app import app, db, User, MentorshipRequest, ChatConversation, ChatMessage
import json

print("=" * 70)
print("TESTING API ENDPOINTS")
print("=" * 70)

# Create test client
client = app.test_client()

with app.app_context():
    # Get test users
    mentee = User.query.filter_by(user_type="2").first()
    mentor = User.query.filter_by(user_type="1").first()
    supervisor = User.query.filter_by(user_type="0").first()
    
    print(f"\nTest Users:")
    print(f"  Mentee: {mentee.name} (ID: {mentee.id})")
    print(f"  Mentor: {mentor.name} (ID: {mentor.id})")
    print(f"  Supervisor: {supervisor.name} (ID: {supervisor.id})")
    
    # Test 1: Get current user (without session - should fail)
    print("\n1. GET /api/chat/current-user (no session)")
    print("-" * 70)
    response = client.get('/api/chat/current-user')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.get_json()}")
    
    # Test 2: Get conversations (without session - should fail)
    print("\n2. GET /api/chat/conversations (no session)")
    print("-" * 70)
    response = client.get('/api/chat/conversations')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.get_json()}")
    
    # Test 3: Get allowed contacts (without session - should fail)
    print("\n3. GET /api/chat/allowed-contacts (no session)")
    print("-" * 70)
    response = client.get('/api/chat/allowed-contacts')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.get_json()}")
    
    # Now test with session
    print("\n" + "=" * 70)
    print("TESTING WITH SESSION (Mentee)")
    print("=" * 70)
    
    with client.session_transaction() as sess:
        sess['email'] = mentee.email
        sess['user_id'] = mentee.id
        sess['user_type'] = mentee.user_type
        sess['user_name'] = mentee.name
    
    # Test 4: Get current user (with session)
    print("\n4. GET /api/chat/current-user (with session)")
    print("-" * 70)
    response = client.get('/api/chat/current-user')
    data = response.get_json()
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(data, indent=2)}")
    
    # Test 5: Get conversations (with session)
    print("\n5. GET /api/chat/conversations (with session)")
    print("-" * 70)
    response = client.get('/api/chat/conversations')
    data = response.get_json()
    print(f"Status: {response.status_code}")
    print(f"Success: {data.get('success')}")
    print(f"Conversations: {len(data.get('conversations', []))}")
    if data.get('conversations'):
        for conv in data['conversations']:
            print(f"  - {conv['other_user_name']}: {conv['last_message']}")
    
    # Test 6: Get allowed contacts (with session)
    print("\n6. GET /api/chat/allowed-contacts (with session)")
    print("-" * 70)
    response = client.get('/api/chat/allowed-contacts')
    data = response.get_json()
    print(f"Status: {response.status_code}")
    print(f"Success: {data.get('success')}")
    print(f"Contacts: {len(data.get('contacts', []))}")
    if data.get('contacts'):
        for contact in data['contacts']:
            print(f"  - {contact['name']} ({contact['role']})")
    
    # Test 7: Start conversation
    print("\n7. POST /api/chat/start/{mentor_id} (with session)")
    print("-" * 70)
    response = client.post(f'/api/chat/start/{mentor.id}')
    data = response.get_json()
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if data.get('success'):
        conv_id = data['conversation_id']
        
        # Test 8: Get messages
        print(f"\n8. GET /api/chat/messages/{conv_id} (with session)")
        print("-" * 70)
        response = client.get(f'/api/chat/messages/{conv_id}')
        data = response.get_json()
        print(f"Status: {response.status_code}")
        print(f"Success: {data.get('success')}")
        print(f"Messages: {len(data.get('messages', []))}")
        
        # Test 9: Send message
        print(f"\n9. POST /api/chat/send (with session)")
        print("-" * 70)
        response = client.post('/api/chat/send', 
                              json={
                                  'conversation_id': conv_id,
                                  'content': 'Hello from test!'
                              })
        data = response.get_json()
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")
        
        # Test 10: Get messages again
        print(f"\n10. GET /api/chat/messages/{conv_id} (after sending)")
        print("-" * 70)
        response = client.get(f'/api/chat/messages/{conv_id}')
        data = response.get_json()
        print(f"Status: {response.status_code}")
        print(f"Messages: {len(data.get('messages', []))}")
        if data.get('messages'):
            for msg in data['messages']:
                print(f"  - {msg['sender_name']}: {msg['content']}")
        
        # Test 11: Mark as read
        print(f"\n11. POST /api/chat/mark-read/{conv_id} (with session)")
        print("-" * 70)
        response = client.post(f'/api/chat/mark-read/{conv_id}')
        data = response.get_json()
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")

print("\n" + "=" * 70)
print("✅ API ENDPOINT TESTS COMPLETE")
print("=" * 70)
