#!/usr/bin/env python3
"""
Check database file permissions and write access
"""
import os
import sys

print("="*60)
print("DATABASE PERMISSIONS CHECKER")
print("="*60)

db_path = "instance/mentors_connect.db"

# Check if database exists
if not os.path.exists(db_path):
    print(f"\n❌ Database file not found: {db_path}")
    sys.exit(1)

print(f"\n✅ Database file exists: {db_path}")

# Check file permissions
import stat
st = os.stat(db_path)
mode = st.st_mode

print(f"\n📋 File Information:")
print(f"   Owner UID: {st.st_uid}")
print(f"   Group GID: {st.st_gid}")
print(f"   Permissions: {oct(mode)[-3:]}")
print(f"   Readable: {bool(mode & stat.S_IRUSR)}")
print(f"   Writable: {bool(mode & stat.S_IWUSR)}")

# Check directory permissions
dir_path = "instance"
if os.path.exists(dir_path):
    dir_st = os.stat(dir_path)
    dir_mode = dir_st.st_mode
    print(f"\n📁 Directory Information:")
    print(f"   Directory: {dir_path}")
    print(f"   Permissions: {oct(dir_mode)[-3:]}")
    print(f"   Writable: {bool(dir_mode & stat.S_IWUSR)}")

# Test write access
print(f"\n🔧 Testing write access...")
try:
    # Try to open database in write mode
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Try a simple write operation
    cursor.execute("CREATE TABLE IF NOT EXISTS test_write (id INTEGER)")
    cursor.execute("INSERT INTO test_write VALUES (1)")
    conn.commit()
    
    # Clean up
    cursor.execute("DROP TABLE test_write")
    conn.commit()
    conn.close()
    
    print("✅ Database is WRITABLE - write test successful!")
    
except sqlite3.OperationalError as e:
    print(f"❌ Database is READ-ONLY or locked!")
    print(f"   Error: {e}")
    print(f"\n🔧 FIX:")
    print(f"   Run these commands:")
    print(f"   sudo chown www-data:www-data {db_path}")
    print(f"   sudo chmod 664 {db_path}")
    print(f"   sudo chown www-data:www-data {dir_path}")
    print(f"   sudo chmod 775 {dir_path}")
    
except Exception as e:
    print(f"❌ Error testing write access: {e}")

# Check current user
import pwd
current_user = pwd.getpwuid(os.getuid()).pw_name
print(f"\n👤 Current user: {current_user}")

# Check if current user can write
if os.access(db_path, os.W_OK):
    print(f"✅ Current user CAN write to database")
else:
    print(f"❌ Current user CANNOT write to database")
    print(f"\n🔧 FIX:")
    print(f"   Run: sudo chown {current_user}:{current_user} {db_path}")
    print(f"   Or: sudo chmod 666 {db_path}")

print("\n" + "="*60)
print("Check complete!")
print("="*60)
