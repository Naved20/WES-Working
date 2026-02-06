"""
Quick script to add profile_completion_email_sent column to database
"""
from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Add column to signup_details table
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE signup_details ADD COLUMN profile_completion_email_sent BOOLEAN DEFAULT 0 NOT NULL'))
            conn.commit()
        print("✅ Successfully added profile_completion_email_sent column to signup_details table")
    except Exception as e:
        if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
            print("ℹ️  Column already exists - no action needed")
        else:
            print(f"❌ Error: {e}")
