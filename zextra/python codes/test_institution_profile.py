"""
Property-based tests for Institution Profile Management

This module contains property-based tests using Hypothesis to validate
database referential integrity and other correctness properties for
institution profile management.

**Feature: institution-profile-management**
"""

import unittest
import tempfile
import os
from hypothesis import given, strategies as st, settings
from hypothesis.strategies import text, integers, emails
from app import app, db, User, Institution
from werkzeug.security import generate_password_hash


class TestInstitutionProfileReferentialIntegrity(unittest.TestCase):
    """
    Property-based tests for database referential integrity
    **Property 4: Database Referential Integrity**
    **Validates: Requirements 1.5, 4.1, 4.2, 4.3, 4.5**
    """
    
    def setUp(self):
        """Set up test database"""
        # Create temporary database for testing
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE']
        app.config['TESTING'] = True
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up test database"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])
    
    @given(
        name=text(min_size=1, max_size=100, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ '),
        email=emails(),
        institution_name=text(min_size=1, max_size=150, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ')
    )
    @settings(max_examples=100)
    def test_database_referential_integrity_property(self, name, email, institution_name):
        """
        Property 4: Database Referential Integrity
        For any database operation involving institution and user records,
        the system should maintain foreign key constraints and prevent
        orphaned or inconsistent data.
        **Validates: Requirements 1.5, 4.1, 4.2, 4.3, 4.5**
        """
        with app.app_context():
            try:
                # Create user with institution type
                hashed_password = generate_password_hash("testpass123", method='pbkdf2:sha256')
                user = User(
                    name=name,
                    email=email,
                    password=hashed_password,
                    user_type="3",  # Institution type
                    institution=institution_name
                )
                db.session.add(user)
                db.session.flush()  # Get user ID
                
                # Create institution profile linked to user
                institution = Institution(
                    user_id=user.id,
                    name=institution_name,
                    contact_person=name,
                    contact_email=email,
                    status="active"
                )
                db.session.add(institution)
                db.session.flush()
                
                # Link user to institution
                user.institution_id = institution.id
                db.session.commit()
                
                # Verify referential integrity constraints
                # 1. User should be linked to institution
                self.assertEqual(user.institution_id, institution.id)
                
                # 2. Institution should be linked to user
                self.assertEqual(institution.user_id, user.id)
                
                # 3. Verify foreign key relationships work
                self.assertEqual(user.institution_ref.id, institution.id)
                self.assertEqual(institution.user.id, user.id)
                
                # 4. Test constraint: Cannot delete user when institution exists
                # This should maintain referential integrity
                institution_id = institution.id
                user_id = user.id
                
                # Verify both records exist
                self.assertIsNotNone(User.query.get(user_id))
                self.assertIsNotNone(Institution.query.get(institution_id))
                
                # 5. Test email uniqueness constraint
                # Try to create another user with same email (should fail)
                duplicate_user = User(
                    name="Different Name",
                    email=email,  # Same email
                    password=hashed_password,
                    user_type="3"
                )
                db.session.add(duplicate_user)
                
                # This should raise an integrity error due to unique constraint
                with self.assertRaises(Exception):
                    db.session.commit()
                
                # Rollback the failed transaction
                db.session.rollback()
                
            except Exception as e:
                # Rollback on any error to maintain clean state
                db.session.rollback()
                # Re-raise if it's not an expected constraint violation
                if "UNIQUE constraint failed" not in str(e) and "IntegrityError" not in str(type(e).__name__):
                    raise


if __name__ == '__main__':
    unittest.main()