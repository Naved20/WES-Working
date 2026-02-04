"""
Database Migration Script: Add Father Name Field to MenteeProfile

This script adds the father_name field to the mentee_profile table.

Field to be added:
- father_name (VARCHAR 150)

Usage:
    python add_father_name_migration.py
"""

from app import app, db
from sqlalchemy import text

def run_migration():
    """Add father_name column to mentee_profile table"""
    
    with app.app_context():
        try:
            # Check if column already exists
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('mentee_profile')]
            
            if 'father_name' not in existing_columns:
                # Add the column
                sql = "ALTER TABLE mentee_profile ADD COLUMN father_name VARCHAR(150)"
                db.session.execute(text(sql))
                db.session.commit()
                print("✓ Added column: father_name")
                print("\n" + "="*50)
                print("Migration completed successfully!")
                print("="*50)
            else:
                print("⊘ Column already exists: father_name")
                print("\n" + "="*50)
                print("Migration skipped - column already exists")
                print("="*50)
                    
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error during migration: {str(e)}")
            raise

if __name__ == "__main__":
    print("="*50)
    print("Starting Database Migration")
    print("Adding Father Name Field to MenteeProfile")
    print("="*50)
    print()
    
    run_migration()
    
    print("\n✅ Migration script completed!")
    print("You can now use the father_name field in the mentee profile.")
