#!/usr/bin/env python
import sqlite3
import os

db_path = 'instance/mentors_connect.db'

if not os.path.exists(db_path):
    print(f"❌ Database file not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print("=" * 60)
print("DATABASE DIAGNOSTIC REPORT")
print("=" * 60)
print(f"\n📊 Total Tables: {len(tables)}\n")

chat_tables = ['chat_conversations', 'chat_messages', 'chat_participants']
found_chat_tables = []

for table in tables:
    table_name = table[0]
    print(f"✓ {table_name}")
    if table_name in chat_tables:
        found_chat_tables.append(table_name)

print("\n" + "=" * 60)
print("CHAT SYSTEM STATUS")
print("=" * 60)

for chat_table in chat_tables:
    if chat_table in found_chat_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {chat_table}")
        count = cursor.fetchone()[0]
        print(f"✅ {chat_table}: {count} records")
    else:
        print(f"❌ {chat_table}: NOT FOUND")

# Check mentorship requests
print("\n" + "=" * 60)
print("MENTORSHIP REQUESTS")
print("=" * 60)

cursor.execute("SELECT COUNT(*) FROM mentorship_requests WHERE final_status='approved'")
approved_count = cursor.fetchone()[0]
print(f"✅ Approved mentorships: {approved_count}")

if approved_count > 0:
    cursor.execute("""
        SELECT mr.id, u1.name as mentee, u2.name as mentor, mr.final_status
        FROM mentorship_requests mr
        JOIN signup_details u1 ON mr.mentee_id = u1.id
        JOIN signup_details u2 ON mr.mentor_id = u2.id
        WHERE mr.final_status = 'approved'
        LIMIT 5
    """)
    print("\nSample approved mentorships:")
    for row in cursor.fetchall():
        print(f"  - {row[1]} ↔ {row[2]} (Status: {row[3]})")

# Check users
print("\n" + "=" * 60)
print("USERS BY ROLE")
print("=" * 60)

for role_id, role_name in [("0", "Supervisor"), ("1", "Mentor"), ("2", "Mentee"), ("3", "Institution")]:
    cursor.execute(f"SELECT COUNT(*) FROM signup_details WHERE user_type='{role_id}'")
    count = cursor.fetchone()[0]
    print(f"{role_name}: {count} users")

conn.close()
print("\n" + "=" * 60)
