# Institution Profile Management Implementation

## Overview

This implementation addresses the requirement for proper institution profile management where institutions create their own profiles during signup, with clear separation between signup data and profile data.

## Key Changes Made

### 1. Database Schema Updates

#### Institution Model Changes (`app.py`)
- **Removed** `name` and `contact_email` columns from the `institutions` table
- **Made** `user_id` required (NOT NULL) - every institution must be linked to a user
- **Added** properties `name` and `contact_email` that dynamically fetch from the linked User record
- **Enforced** unique constraint on `user_id` to prevent duplicate institution profiles

```python
@property
def name(self):
    """Institution name comes from linked User.name"""
    return self.user.name if self.user else None

@property
def contact_email(self):
    """Institution email comes from linked User.email"""
    return self.user.email if self.user else None
```

### 2. Account Creation Flow Updates

#### Supervisor Create Account (`templates/supervisor/create_account.html`)
- **Modified** UI to handle institution creation differently
- **For institutions**: Name field becomes auto-filled with institution name
- **Separated** institution selection (for mentors/mentees) from institution creation (for institution admins)
- **Added** JavaScript to auto-fill user name with institution name for institution admins

#### Create Account Route (`app.py`)
- **Updated** logic to properly handle institution admin creation
- **For institution admins**: User name is set to institution name
- **Enforced** unique institution names by checking existing User records
- **Automatically** creates linked Institution profile when creating institution admin

### 3. Institution Profile Management

#### Edit Institution Profile (`templates/institution/editinstitutionprofile.html`)
- **Made** institution name and email **read-only** fields
- **Added** visual indicators (🔒) to show fields are not editable
- **Updated** form validation to exclude read-only fields
- **Added** CSS styles for read-only inputs

#### Institution Profile Routes (`app.py`)
- **Updated** `institutionprofile()` to use property-based name/email
- **Updated** `editinstitutionprofile()` to exclude name/email from form processing
- **Maintained** all other editable fields (type, address, contact person, etc.)

### 4. Database Migration

#### Migration File (`migrations/versions/20260206_update_institution_profile_management.py`)
- **Safely** removes `name` and `contact_email` columns
- **Enforces** NOT NULL constraint on `user_id`
- **Handles** existing data by cleaning up orphaned records
- **Provides** proper rollback functionality

## Business Logic Implemented

### Institution Signup Flow
1. **Supervisor creates institution admin account**
   - Institution name becomes the user name
   - Institution email becomes the user email
   - Linked Institution profile is automatically created

2. **Institution admin logs in**
   - Redirected to complete profile if incomplete
   - Can edit profile details but NOT name or email

3. **Profile Management**
   - Institution name and email are **read-only** (from signup)
   - All other fields are editable (address, type, contact person, etc.)
   - Changes are saved to Institution profile, not User record

### Data Integrity
- **One-to-one relationship** between User and Institution enforced at DB level
- **Referential integrity** maintained through foreign key constraints
- **Unique constraints** prevent duplicate institutions
- **Cascade handling** for related data

## Files Modified

### Core Application Files
- `app.py` - Institution model, routes, and account creation logic
- `migrations/versions/20260206_update_institution_profile_management.py` - Database schema migration

### Templates
- `templates/supervisor/create_account.html` - Account creation UI
- `templates/institution/editinstitutionprofile.html` - Profile editing UI with read-only fields
- `templates/institution/institutionprofile.html` - Profile display UI

### Test Files
- `test_institution_profile_management.py` - Comprehensive test suite

## Key Features

### ✅ Implemented Requirements
1. **No institution selection during institution signup** - Institution admins don't select from existing institutions
2. **Email as official institution email** - User email becomes institution email (read-only)
3. **Name as institution name** - User name becomes institution name (read-only)
4. **Separate but linked data** - Signup data (User) and profile data (Institution) are separate tables but linked
5. **Non-editable name/email** - Institution name and email cannot be changed on profile page
6. **Database-level enforcement** - Constraints ensure data integrity

### 🔒 Security & Data Integrity
- Foreign key constraints ensure referential integrity
- Unique constraints prevent duplicate institutions
- NOT NULL constraints ensure required relationships
- Proper cascade handling for data cleanup

### 🧪 Testing
- Comprehensive test suite validates all functionality
- Tests database constraints and business logic
- Verifies read-only behavior of name/email fields
- Confirms proper separation of signup and profile data

## Usage Examples

### Creating Institution Admin (Supervisor)
```python
# Supervisor creates institution admin
institution_name = "University of Example"
institution_email = "admin@example.edu"

# User record (signup data)
user = User(
    name=institution_name,  # Institution name
    email=institution_email,  # Institution email
    user_type="3"  # Institution admin
)

# Linked institution profile
institution = Institution(
    user_id=user.id,
    # name and contact_email come from user via properties
    institution_type="university",
    city="Example City",
    # ... other profile fields
)
```

### Accessing Institution Data
```python
institution = Institution.query.first()
print(institution.name)  # From user.name (read-only)
print(institution.contact_email)  # From user.email (read-only)
print(institution.city)  # From institution profile (editable)
```

## Migration Notes

The migration safely handles existing data by:
1. Cleaning up orphaned institution records
2. Preserving all profile data except name/email
3. Enforcing new constraints
4. Providing rollback capability

## Future Considerations

1. **Bulk Operations** - Consider batch operations for large datasets
2. **Audit Trail** - Track changes to institution profiles
3. **API Integration** - Expose institution data via REST API
4. **Advanced Validation** - Add more sophisticated validation rules
5. **Reporting** - Generate reports on institution data

## Conclusion

This implementation successfully separates institution signup data from profile data while maintaining a clean, intuitive user experience. Institution names and emails are properly protected from editing while allowing full customization of other profile fields.