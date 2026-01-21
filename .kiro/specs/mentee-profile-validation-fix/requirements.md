# Requirements Document

## Introduction

This specification addresses critical issues in the mentee profile management system of a Flask-based mentorship application. The system currently has validation inconsistencies, navigation problems, and display issues that prevent proper user experience and profile completion workflows.

## Glossary

- **Mentee_Profile_System**: The complete system for managing mentee user profiles including creation, editing, validation, and display
- **Dynamic_Validation**: Validation logic that changes based on the selected "Who am I" category
- **Profile_Completion_Check**: Backend logic that determines if a mentee profile is complete enough to access other features
- **AJAX_Form_Handler**: Frontend JavaScript that handles form submission without page refresh
- **Navigation_System**: The system that handles transitions between profile pages and dashboard

## Requirements

### Requirement 1: Dynamic Field Validation

**User Story:** As a mentee, I want the form validation to only require fields relevant to my selected "Who am I" category, so that I'm not forced to fill irrelevant information.

#### Acceptance Criteria

1. WHEN a mentee selects a "Who am I" category, THE Mentee_Profile_System SHALL show only the fields relevant to that category
2. WHEN a mentee changes their "Who am I" selection, THE Mentee_Profile_System SHALL update the required fields dynamically without page refresh
3. WHEN validating form submission, THE Mentee_Profile_System SHALL only validate fields that are visible and relevant to the selected category
4. WHEN a field is hidden due to category selection, THE Mentee_Profile_System SHALL not trigger validation errors for that field
5. THE Mentee_Profile_System SHALL disable HTML5 browser validation using the novalidate attribute
6. THE Mentee_Profile_System SHALL remove all hardcoded required attributes from conditional fields

### Requirement 2: Consistent Frontend-Backend Validation

**User Story:** As a mentee, I want the frontend and backend validation to be consistent, so that I don't get conflicting error messages.

#### Acceptance Criteria

1. WHEN frontend validation passes, THE Mentee_Profile_System SHALL ensure backend validation uses the same rules
2. WHEN backend validation fails, THE Mentee_Profile_System SHALL return specific field-level error messages
3. THE Mentee_Profile_System SHALL validate only fields required for the currently selected "Who am I" category
4. WHEN a mentee submits the form, THE Mentee_Profile_System SHALL ignore missing values for hidden or non-relevant fields
5. THE Mentee_Profile_System SHALL maintain a single source of truth for validation rules between frontend and backend

### Requirement 3: AJAX Form Submission

**User Story:** As a mentee, I want the profile form to save without refreshing the page, so that I have a smooth editing experience.

#### Acceptance Criteria

1. WHEN a mentee clicks "Save Profile", THE AJAX_Form_Handler SHALL prevent the default form submission
2. WHEN form validation passes, THE AJAX_Form_Handler SHALL submit the form data via AJAX
3. WHEN the server responds successfully, THE AJAX_Form_Handler SHALL display a success message without page refresh
4. WHEN the server responds with validation errors, THE AJAX_Form_Handler SHALL display error messages without page refresh
5. WHEN the save operation completes successfully, THE AJAX_Form_Handler SHALL redirect to the profile view page after a brief delay

### Requirement 4: Age Display Instead of Date of Birth

**User Story:** As a system user, I want to see ages instead of full dates of birth, so that personal information is displayed more appropriately.

#### Acceptance Criteria

1. WHEN displaying mentee information anywhere in the system, THE Mentee_Profile_System SHALL show age in years instead of date of birth
2. THE Mentee_Profile_System SHALL calculate age from the stored date of birth
3. WHEN a mentee has no date of birth, THE Mentee_Profile_System SHALL handle the missing data gracefully
4. THE Mentee_Profile_System SHALL format age display as "X years" (e.g., "22 years")
5. THE Mentee_Profile_System SHALL update age calculations to be current as of the display date

### Requirement 5: General Details Section Management

**User Story:** As a mentee, I want to provide my general contact and address information in a dedicated section, so that my basic details are properly organized.

#### Acceptance Criteria

1. THE Mentee_Profile_System SHALL display a "General Details" section above the "Who am I" section
2. THE Mentee_Profile_System SHALL include father's name as a mandatory field in General Details
3. THE Mentee_Profile_System SHALL include address fields (line 1, line 2, city, state, postal code, country) in General Details
4. THE Mentee_Profile_System SHALL save all General Details fields to the database
5. THE Mentee_Profile_System SHALL validate all General Details fields as mandatory except address line 2

### Requirement 6: Navigation System Fix

**User Story:** As a mentee, I want to be able to navigate back to my dashboard from profile pages, so that I can access other features after editing my profile.

#### Acceptance Criteria

1. WHEN a mentee clicks "Back to Dashboard" from the edit profile page, THE Navigation_System SHALL redirect to the mentee dashboard
2. WHEN a mentee's profile is complete, THE Profile_Completion_Check SHALL allow access to the dashboard
3. WHEN a mentee's profile is incomplete, THE Profile_Completion_Check SHALL redirect to the edit profile page with appropriate messaging
4. THE Navigation_System SHALL not create redirect loops between dashboard and edit profile pages
5. THE Navigation_System SHALL properly handle profile completion status checks

### Requirement 7: Profile Completion Logic Update

**User Story:** As a mentee, I want the system to correctly determine when my profile is complete, so that I can access all features when I've provided the necessary information.

#### Acceptance Criteria

1. THE Profile_Completion_Check SHALL validate only fields that are mandatory for the selected "Who am I" category
2. THE Profile_Completion_Check SHALL include General Details fields in the completion check
3. THE Profile_Completion_Check SHALL not require fields that are not relevant to the selected category
4. WHEN all mandatory fields for a category are filled, THE Profile_Completion_Check SHALL return true
5. THE Profile_Completion_Check SHALL handle cases where the "Who am I" selection changes after initial profile creation

### Requirement 8: Field Requirement Management

**User Story:** As a mentee, I want only the truly necessary fields to be marked as required, so that I can complete my profile efficiently.

#### Acceptance Criteria

1. THE Mentee_Profile_System SHALL not require Course Stream, Class Year, or Career Interest as mandatory for all categories
2. THE Mentee_Profile_System SHALL not require Key Skills, Career Goals, or Education Level as mandatory for all categories  
3. THE Mentee_Profile_System SHALL save GDPR agreement status to the database
4. THE Mentee_Profile_System SHALL require GDPR agreement for profile completion
5. THE Mentee_Profile_System SHALL make field requirements conditional based on the selected "Who am I" category

### Requirement 9: Error Message Improvement

**User Story:** As a mentee, I want clear and specific error messages when validation fails, so that I know exactly what needs to be corrected.

#### Acceptance Criteria

1. WHEN validation fails, THE Mentee_Profile_System SHALL provide specific field names in error messages
2. THE Mentee_Profile_System SHALL not show generic "fill all fields" messages
3. WHEN a field is missing, THE Mentee_Profile_System SHALL indicate which specific field needs attention
4. THE Mentee_Profile_System SHALL group related validation errors logically
5. THE Mentee_Profile_System SHALL display validation errors in a user-friendly format

### Requirement 10: Data Persistence and Integrity

**User Story:** As a mentee, I want my profile data to be saved correctly and completely, so that I don't lose information when switching between categories.

#### Acceptance Criteria

1. WHEN a mentee changes their "Who am I" selection, THE Mentee_Profile_System SHALL preserve previously entered data
2. THE Mentee_Profile_System SHALL save all form data to the appropriate database fields
3. THE Mentee_Profile_System SHALL handle database schema updates for new fields like General Details
4. WHEN profile data is retrieved, THE Mentee_Profile_System SHALL populate all form fields with existing values
5. THE Mentee_Profile_System SHALL maintain data integrity across profile updates