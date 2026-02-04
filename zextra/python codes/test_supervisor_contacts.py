#!/usr/bin/env python
"""
Test supervisor contacts API
"""
import sys
sys.path.insert(0, '.')

from app import app, db, User, MentorshipRequest

# Create app context
with app.app_context():
    print("=" * 60)
    print("TESTING SUPERVISOR CONTACTS")
    print("=" * 60)
    
    # Find supervisor
    supervisor = User.query.filter_by(user_type="0").first()
    if not supervisor:
        print("❌ No supervisor found")
        sys.exit(1)
    
    print(f"\n✅ Supervisor found: {supervisor.name} (ID: {supervisor.id})")
    
    # Count mentors
    mentors = User.query.filter_by(user_type="1").all()
    print(f"✅ Mentors in system: {len(mentors)}")
    
    # Count mentees
    mentees = User.query.filter_by(user_type="2").all()
    print(f"✅ Mentees in system: {len(mentees)}")
    
    # Simulate the API logic
    print("\n" + "=" * 60)
    print("SIMULATING API RESPONSE")
    print("=" * 60)
    
    allowed_contacts = []
    
    # Get all mentors
    for mentor in mentors:
        allowed_contacts.append({
            "id": mentor.id,
            "name": mentor.name,
            "type": "1",
            "role": "Mentor"
        })
    
    # Get all mentees
    for mentee in mentees:
        allowed_contacts.append({
            "id": mentee.id,
            "name": mentee.name,
            "type": "2",
            "role": "Mentee"
        })
    
    print(f"\n✅ Total contacts for supervisor: {len(allowed_contacts)}")
    print(f"   - Mentors: {len([c for c in allowed_contacts if c['type'] == '1'])}")
    print(f"   - Mentees: {len([c for c in allowed_contacts if c['type'] == '2'])}")
    
    # Show first 5
    print("\nFirst 5 contacts:")
    for contact in allowed_contacts[:5]:
        print(f"   - {contact['name']} ({contact['role']})")
    
    if len(allowed_contacts) > 5:
        print(f"   ... and {len(allowed_contacts) - 5} more")
    
    print("\n" + "=" * 60)
