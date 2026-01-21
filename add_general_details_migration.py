"""
Database Migration Script: Add General Details Fields to MenteeProfile

This script adds address and general information fields to the mentee_profile table.

Fields to be added:
- address_line1 (VARCHAR 200)
- address_line2 (VARCHAR 200)
- city (VARCHAR 100)
- state (VARCHAR 100)
- postal_code (VARCHAR 20)
- country (VARCHAR 100)

Usage:
    python add_general_details_migration.py
"""

from app import app, db
from sqlalchemy import text

def run_migration():
    """Add general details columns to mentee_profile table"""
    
    with app.app_context():
        try:
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('mentee_profile')]
            
            columns_to_add = {
                'address_line1': 'VARCHAR(200)',
                'address_line2': 'VARCHAR(200)',
                'city': 'VARCHAR(100)',
                'state': 'VARCHAR(100)',
                'postal_code': 'VARCHAR(20)',
                'country': 'VARCHAR(100)'
            }
            
            added_columns = []
            skipped_columns = []
            
            for column_name, column_type in columns_to_add.items():
                if column_name not in existing_columns:
                    # Add the column
                    sql = f"ALTER TABLE mentee_profile ADD COLUMN {column_name} {column_type}"
                    db.session.execute(text(sql))
                    added_columns.append(column_name)
                    print(f"✓ Added column: {column_name}")
                else:
                    skipped_columns.append(column_name)
                    print(f"⊘ Column already exists: {column_name}")
            
            # Commit the changes
            db.session.commit()
            
            print("\n" + "="*50)
            print("Migration completed successfully!")
            print("="*50)
            print(f"Columns added: {len(added_columns)}")
            print(f"Columns skipped: {len(skipped_columns)}")
            
            if added_columns:
                print("\nAdded columns:")
                for col in added_columns:
                    print(f"  - {col}")
            
            if skipped_columns:
                print("\nSkipped columns (already exist):")
                for col in skipped_columns:
                    print(f"  - {col}")
                    
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error during migration: {str(e)}")
            raise

if __name__ == "__main__":
    print("="*50)
    print("Starting Database Migration")
    print("Adding General Details Fields to MenteeProfile")
    print("="*50)
    print()
    
    run_migration()
    
    print("\n✅ Migration script completed!")
    print("You can now use the general details fields in the mentee profile.")
