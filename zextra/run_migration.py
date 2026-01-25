#!/usr/bin/env python
"""Run database migration to create chat tables"""

import subprocess
import sys

print("=" * 60)
print("RUNNING DATABASE MIGRATION")
print("=" * 60)

try:
    result = subprocess.run([sys.executable, "-m", "flask", "db", "upgrade"], 
                          capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode == 0:
        print("\n✅ Migration completed successfully!")
    else:
        print(f"\n❌ Migration failed with return code {result.returncode}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error running migration: {e}")
    sys.exit(1)

# Verify tables were created
print("\n" + "=" * 60)
print("VERIFYING TABLES")
print("=" * 60)

import sqlite3
conn = sqlite3.connect('instance/mentors_connect.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'chat_%'")
tables = cursor.fetchall()

if tables:
    print("✅ Chat tables created:")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"   - {table[0]}: {count} records")
else:
    print("❌ Chat tables not found!")
    sys.exit(1)

conn.close()
print("\n✅ All chat tables verified!")
