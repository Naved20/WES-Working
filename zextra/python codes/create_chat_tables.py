#!/usr/bin/env python
"""Directly create chat tables using SQLAlchemy"""

from app import app, db, ChatConversation, ChatMessage

print("=" * 60)
print("CREATING CHAT TABLES DIRECTLY")
print("=" * 60)

with app.app_context():
    try:
        # Create tables
        print("\n1. Creating chat_conversations table...")
        db.create_all()
        print("✅ Tables created successfully!")
        
        # Verify
        print("\n2. Verifying tables...")
        import sqlite3
        conn = sqlite3.connect('instance/mentors_connect.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'chat_%' ORDER BY name")
        tables = cursor.fetchall()
        
        if tables:
            print("✅ Chat tables verified:")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"   - {table[0]}: {count} records")
        else:
            print("❌ Chat tables not found!")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 60)
print("DONE")
print("=" * 60)
