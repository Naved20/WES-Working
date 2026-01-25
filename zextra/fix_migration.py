#!/usr/bin/env python
"""Fix migration heads and create chat tables"""

import subprocess
import sys
import os

print("=" * 60)
print("FIXING MIGRATION HEADS")
print("=" * 60)

# First, let's see what heads exist
print("\n1. Checking migration heads...")
result = subprocess.run([sys.executable, "-m", "flask", "db", "heads"], 
                       capture_output=True, text=True)
print(result.stdout)

# Try to merge heads
print("\n2. Attempting to merge heads...")
result = subprocess.run([sys.executable, "-m", "flask", "db", "merge", "-m", "Merge migration heads"], 
                       capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

# Now upgrade
print("\n3. Running upgrade with heads...")
result = subprocess.run([sys.executable, "-m", "flask", "db", "upgrade", "heads"], 
                       capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

if result.returncode == 0:
    print("\n✅ Migration completed successfully!")
else:
    print(f"\n⚠️ Migration returned code {result.returncode}, but may have succeeded")

# Verify tables
print("\n" + "=" * 60)
print("VERIFYING CHAT TABLES")
print("=" * 60)

import sqlite3
conn = sqlite3.connect('instance/mentors_connect.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'chat_%' ORDER BY name")
tables = cursor.fetchall()

if tables:
    print("✅ Chat tables found:")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"   - {table[0]}: {count} records")
else:
    print("❌ Chat tables not found!")

conn.close()
