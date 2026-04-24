"""
Change admin password
"""
from app import app, db, User
from werkzeug.security import generate_password_hash

def change_admin_password():
    with app.app_context():
        # Find admin user
        admin = User.query.filter_by(email='info@wazireducationsocity.com').first()
        
        if not admin:
            print("❌ Admin user not found!")
            return
        
        print(f"✅ Found admin user: {admin.name} ({admin.email})")
        print(f"   User ID: {admin.id}")
        print(f"   User Type: {admin.user_type}")
        
        # New password
        new_password = "X7m#Q2vL9@pR4!Ks"
        
        # Hash the password
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=8)
        
        # Update password
        admin.password = hashed_password
        db.session.commit()
        
        print(f"\n✅ Password changed successfully!")
        print(f"   New password: {new_password}")
        print(f"   Email: {admin.email}")

if __name__ == "__main__":
    change_admin_password()
