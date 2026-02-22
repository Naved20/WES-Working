# Mentor Connect Platform - Application Flow & User Workflow

## Overview
Mentor Connect is a mentorship platform that connects mentors, mentees, supervisors, and institutions in a structured ecosystem for professional and educational growth.

## User Types & Roles

### 1. **Mentee** (`user_type = "2"`)
- Students, professionals, entrepreneurs, freelancers, or individuals on career breaks
- Seek guidance, skill development, and career advancement
- Can request mentorship from available mentors

### 2. **Mentor** (`user_type = "1"`)
- Experienced professionals, industry experts, educators
- Provide guidance, share knowledge, and support mentees
- Must complete detailed profile with qualifications and mentorship preferences

### 3. **Supervisor** (`user_type = "0"`)
- Platform administrators and moderators
- Manage users, approve mentorship requests, oversee platform operations
- Have access to all system data and administrative functions

### 4. **Institution** (`user_type = "3"`)
- Educational institutions, organizations, companies
- Manage their members (mentors and mentees)
- Track institutional mentorship programs

## Application Architecture Flow

### Frontend Structure
```
base2.html (Main Layout)
├── Navigation Bar (Top)
├── Sidebar (Conditional - based on show_sidebar)
└── Content Block (Dynamic per page)
```

### Backend Structure
```
app.py (Main Flask Application)
├── Database Models (SQLAlchemy)
├── Route Handlers
├── Authentication System
├── Profile Management
├── Mentorship System
├── Meeting/Task Management
└── Chat System
```

## Normal User Workflow

### Phase 1: Registration & Onboarding

#### Step 1: Account Creation
```
User Visits Platform → Sign Up Page → Select User Type → Create Account
```

**Registration Options:**
- Traditional email/password signup
- Google OAuth authentication
- Supervisor-created accounts (for institutions/organizations)

#### Step 2: Profile Completion (Mandatory)
```
Account Created → Redirect to Profile Completion → Fill Required Fields → Submit
```

**Profile Requirements by User Type:**

**Mentee Profile:**
- Personal information (name, contact, location)
- Educational/professional background
- Mentorship expectations and goals
- Profile picture (mandatory)

**Mentor Profile:**
- Professional details (role, organization, experience)
- Educational qualifications
- Mentorship preferences (topics, availability, duration)
- Profile picture (mandatory)
- Criminal certificate (for Luxembourg-based mentors)

**Supervisor Profile:**
- Organization details
- Contact information
- Role description
- Profile picture (mandatory)

**Institution Profile:**
- Institution details
- Contact person information
- Address and contact details
- Profile picture (mandatory)

### Phase 2: Platform Navigation

#### Dashboard Access
```
Login → Role-based Dashboard → Sidebar Navigation → Feature Access
```

**Dashboard Features by Role:**

**Mentee Dashboard:**
- Find Mentors (search and filter)
- My Mentors (connected mentorships)
- Meeting Requests
- Task Management
- Calendar View
- Chat System

**Mentor Dashboard:**
- Find Mentees (search and filter)
- Mentorship Requests (incoming)
- My Mentees (active mentorships)
- Meeting Management
- Task Assignment
- Calendar View
- Chat System

**Supervisor Dashboard:**
- User Management (all users)
- Mentorship Request Approval
- Institution Management
- Platform Analytics
- Account Creation (for others)
- Password Reset Management
- System-wide Calendar & Tasks

**Institution Dashboard:**
- Institution Mentors/Mentees
- Mentorship Tracking
- Institutional Calendar
- Task Overview
- Chat with Supervisors

### Phase 3: Mentorship Lifecycle

#### Step 1: Mentor Discovery (Mentee Perspective)
```
Find Mentors Page → Search/Filters → View Profiles → Select Mentor
```

**Mentor Search Filters:**
- Profession/Industry
- Location
- Education Level
- Years of Experience
- Mentorship Topics

#### Step 2: Mentorship Request
```
Select Mentor → Request Mentorship → Fill Request Form → Submit
```

**Request Form Details:**
- Purpose of mentorship (career guidance, interview prep, skill development)
- Mentor type preference (anchor/special)
- Term preference (short/long)
- Duration (auto-calculated based on rules)
- "Why I need a mentor" statement

#### Step 3: Approval Workflow
```
Mentee Submits Request → Mentor Review → Supervisor Approval → Connection Established
```

**Approval States:**
1. **Pending** - Request submitted, awaiting mentor response
2. **Mentor Accepted** - Mentor approves, awaiting supervisor
3. **Supervisor Approved** - Final approval, mentorship active
4. **Rejected** - Request denied at any stage

#### Step 4: Active Mentorship
```
Approval Complete → Master Tasks Assigned → Meetings Scheduled → Progress Tracking
```

**Automatic System Actions:**
- Master tasks assigned based on duration
- Meeting templates created
- Progress tracking initialized
- Communication channels opened

### Phase 4: Mentorship Execution

#### Meeting Management
```
Create Meeting Request → Set Date/Time → Google Calendar Integration → Meeting Conducted
```

**Meeting Features:**
- Google Calendar integration
- Meet link generation
- Rescheduling capabilities
- Meeting notes and follow-ups

#### Task Management
```
System-assigned Tasks → Personal Tasks → Progress Tracking → Completion
```

**Task Types:**
- **Master Tasks**: Pre-defined structured tasks based on mentorship phase
- **Personal Tasks**: Custom tasks created by mentor for mentee
- **Progress Tracking**: Percentage completion with deadlines

#### Communication
```
Chat System → Role-based Access Control → Real-time Messaging → File Sharing
```

**Chat Rules:**
- Mentees can chat with: assigned mentors and supervisors
- Mentors can chat with: assigned mentees and supervisors
- Supervisors can chat with: any mentor or mentee
- Institutions can chat with: supervisors only

### Phase 5: Progress Monitoring & Completion

#### Progress Tracking
```
Task Completion → Meeting Attendance → Skill Development → Goal Achievement
```

**Tracking Metrics:**
- Task completion percentage
- Meeting attendance rate
- Skill development milestones
- Goal achievement progress

#### Feedback & Rating
```
Task Completion → Mentor Feedback → Rating System → Continuous Improvement
```

**Feedback System:**
- 1-5 star ratings for tasks
- Strengths and improvements feedback
- Mentorship effectiveness evaluation

## Key System Features

### 1. **Profile Completion Enforcement**
- Mandatory profile completion before accessing platform features
- Role-specific required fields
- Profile picture requirement for all users

### 2. **India-Specific Fields**
- Conditional display of "School Type" and "Stream" fields for Indian users
- Country-based field visibility
- Government/private school classification

### 3. **Accessibility & CSP Compliance**
- WCAG accessibility standards
- Content Security Policy (CSP) compliance
- Proper label associations for form fields
- ARIA attributes for screen readers

### 4. **Google Integration**
- OAuth authentication
- Calendar API for meeting management
- Service account for organization-wide calendar

### 5. **Email System**
- Welcome emails for new users
- OTP-based password reset
- Meeting notifications
- System announcements

### 6. **File Upload System**
- Profile pictures (jpg, png, jpeg, gif)
- Criminal certificates (pdf)
- Secure file storage with validation

## Data Models & Relationships

### Core Tables:
1. **User** (`signup_details`) - Base user information
2. **MentorProfile** - Mentor-specific details
3. **MenteeProfile** - Mentee-specific details  
4. **SupervisorProfile** - Supervisor details
5. **Institution** - Institution information
6. **MentorshipRequest** - Mentorship connection requests
7. **MeetingRequest** - Scheduled meetings
8. **MasterTask** - Pre-defined mentorship tasks
9. **MenteeTask** - Assigned tasks to mentees
10. **PersonalTask** - Custom tasks
11. **TaskRating** - Task feedback and ratings
12. **ChatConversation** - Chat conversations
13. **ChatMessage** - Individual messages

### Key Relationships:
- One-to-one: User ↔ Profile (based on user_type)
- One-to-many: User → MentorshipRequests (as mentee/mentor)
- Many-to-many: Through MentorshipRequest table
- Hierarchical: Supervisor oversees all relationships

## Security & Access Control

### Authentication:
- Session-based authentication
- Password hashing (pbkdf2:sha256)
- Google OAuth integration
- Session timeout (10 days)

### Authorization:
- Role-based access control (RBAC)
- Route protection with decorators
- Profile completion requirement
- Chat access control based on mentorship relationships

### Data Protection:
- SQL injection prevention (SQLAlchemy)
- XSS protection (template escaping)
- File upload validation
- Secure password reset with OTP

## Error Handling & Validation

### Client-side:
- Form validation with JavaScript
- Real-time feedback
- Input sanitization

### Server-side:
- Database transaction management
- Exception handling with rollback
- Flash messages for user feedback
- Logging for debugging

## Deployment & Configuration

### Environment Configuration:
- Production vs development modes
- Database configuration (SQLite/PostgreSQL)
- Email server settings
- Google API credentials

### File Structure:
```
mentor_connect/
├── app.py (main application)
├── requirements.txt (dependencies)
├── static/ (CSS, JS, images, uploads)
├── templates/ (HTML templates)
├── migrations/ (database migrations)
├── instance/ (database files)
└── .kiro/ (Kiro IDE configuration)
```

## Future Enhancements

### Planned Features:
1. **Video Conferencing** - Integrated video calls
2. **Document Sharing** - Secure file sharing within chats
3. **Analytics Dashboard** - Advanced reporting and insights
4. **Mobile Application** - Native mobile apps
5. **Payment Integration** - Premium mentorship features
6. **Certificate Generation** - Completion certificates
7. **Community Forums** - Group discussions and knowledge sharing
8. **Skill Assessment** - Pre/post mentorship skill evaluation

## Support & Maintenance

### User Support:
- In-app chat with supervisors
- Email support system
- FAQ and documentation
- Tutorial videos and guides

### System Maintenance:
- Regular database backups
- Performance monitoring
- Security updates
- Feature enhancements based on user feedback

---

*This document provides a comprehensive overview of the Mentor Connect platform's application flow and user workflows. For specific implementation details, refer to the source code and database schema.*