from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from sqlalchemy import cast, Integer, or_, and_, text
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy.orm import Session
import os
import json 
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime as dt
from flask_migrate import Migrate


# ============================================================
# PRODUCTION CONFIGURATION
# ============================================================
# Set to True for production, False for local development
PRODUCTION = True  # Change to False for local development

app = Flask(__name__)

# Secret key - USE A STRONG RANDOM KEY IN PRODUCTION!
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
if PRODUCTION:
    app.secret_key = os.environ.get("SECRET_KEY", "your-production-secret-key-change-this")
else:
    app.secret_key = "1234"  # Only for local development

app.permanent_session_lifetime = timedelta(days=10)

# Image upload configuration
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "signin" 

# --- User Loader ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ============================================================
# GOOGLE OAUTH CONFIGURATION
# ============================================================
if PRODUCTION:
    # Production settings - HTTPS required
    # Remove OAUTHLIB_INSECURE_TRANSPORT in production
    CLIENT_SECRETS_FILE = "client_secret.json"
    REDIRECT_URI = "https://mentorship.weslux.lu/callback"
else:
    # Development settings - HTTP allowed
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # ONLY for local dev (http)
    CLIENT_SECRETS_FILE = "client_secret.json"
    REDIRECT_URI = "http://127.0.0.1:5000/callback"

# Scopes for Google OAuth Login (user info only)
LOGIN_SCOPES = [
    "openid", 
    "https://www.googleapis.com/auth/userinfo.email", 
    "https://www.googleapis.com/auth/userinfo.profile"
]

# Scopes for Google Calendar (meetings)
CALENDAR_SCOPES = [
    "https://www.googleapis.com/auth/calendar"
]

# Combined scopes (for backward compatibility)
SCOPES = LOGIN_SCOPES



#--------------User_type Code------------------------
# -------------supervisor = "0"----------------------
# -------------mentor = "1"--------------------------
# -------------mantee = "2"--------------------------

# ============================================================
# DATABASE CONFIGURATION
# ============================================================
if PRODUCTION:
    # Production database - Use PostgreSQL or MySQL
    # Example: app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    # For now, using SQLite (not recommended for production with multiple workers)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///mentors_connect.db")
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mentors_connect.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

migrate = Migrate(app, db)

def mentor_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_type") != "1":
            flash("Please login as mentor first!", "error")
            return redirect(url_for("signin"))
        return f(*args, **kwargs)
    return decorated_function

#-------------- signup details ----------------
class User(db.Model):
    __tablename__ = "signup_details"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=True)   # nullable for OAuth users
    user_type = db.Column(db.String(10), nullable=True)  # nullable until user selects type
    institution = db.Column(db.String(150), nullable=True)
    institution_id = db.Column(db.Integer, db.ForeignKey("institutions.id"), nullable=True)

    # OAuth fields
    google_id = db.Column(db.String(200), unique=True, nullable=True)
    oauth_provider = db.Column(db.String(50), nullable=True)  # 'google', 'facebook', etc.
    profile_picture_url = db.Column(db.String(500), nullable=True)  # OAuth profile picture
    oauth_created_at = db.Column(db.DateTime, nullable=True)

    #connect form another table
    mentor_profile = db.relationship("MentorProfile", backref="user", uselist=False)
    institution_ref = db.relationship("Institution", backref="users", foreign_keys="User.institution_id")

    def __repr__(self):
        return f"<user {self.name}>"

#------------table mentors details-------------------
class MentorProfile(db.Model):
    __tablename__="mentor_profile"

    id = db.Column(db.Integer, primary_key=True)

    # foregin key link to User table
    user_id= db.Column(db.Integer, db.ForeignKey("signup_details.id"),nullable=False)

    # Personal & Professional Details
    profession = db.Column(db.String(100))
    skills = db.Column(db.Text)  # New field - comma separated skills
    role = db.Column(db.String(100))  # New field - job role/position
    industry_sector = db.Column(db.String(100))  # New field - industry/sector
    organisation = db.Column(db.String(150))
    years_of_experience = db.Column(db.String(100))     
    
    # Contact Information
    whatsapp = db.Column(db.String(20))
    location = db.Column(db.String(100))  # New field - country
    
    # Education & Background
    education = db.Column(db.String(150))
    language = db.Column(db.String(100))  # Can store multiple languages comma separated
    
    # Social Links
    linkedin_link = db.Column(db.String(200))  # New field
    github_link = db.Column(db.String(200))  # New field
    portfolio_link = db.Column(db.String(200))  # New field
    other_social_link = db.Column(db.String(200))
    
    # Mentorship Preferences
    mentorship_topics = db.Column(db.Text)  # New field - topics they can mentor on
    mentorship_type_preference = db.Column(db.String(200))  # New field - school, women, etc.
    preferred_communication = db.Column(db.String(100))  # online, offline, hybrid
    availability = db.Column(db.String(100))
    connect_frequency = db.Column(db.String(100))
    preferred_duration = db.Column(db.String(100))  # New field - 1 month, 6 months, etc.
    
    # Mentor Philosophy
    why_mentor = db.Column(db.Text)  # Changed from "why become mentor" to "why mentor"
    mentorship_philosophy = db.Column(db.Text)  # New field
    mentorship_motto = db.Column(db.String(300))  # New field
    
    # Additional Information
    additional_info = db.Column(db.Text)
    profile_picture = db.Column(db.String(100)) 
    status = db.Column(db.String(20), default="pending")

#------------ table mentee details-------------------
class MenteeProfile(db.Model):
    __tablename__ = "mentee_profile"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("signup_details.id"), nullable=False)

    # mentee details
    dob = db.Column(db.String(20))
    school_college_name = db.Column(db.String(150))
    mobile_number = db.Column(db.String(20))
    whatsapp_number = db.Column(db.String(20))
    govt_private = db.Column(db.String(50))
    stream = db.Column(db.String(100))
    class_year = db.Column(db.String(50))
    favourite_subject = db.Column(db.String(100))
    goal = db.Column(db.Text)

    # parent info
    parent_name = db.Column(db.String(150))
    parent_mobile = db.Column(db.String(20))

    # other
    comments = db.Column(db.Text)
    terms_agreement = db.Column(db.String(10))  # Yes / No
    profile_picture = db.Column(db.String(100))  # store image filename
    status = db.Column(db.String(20), default="pending")  # Add this
    user = db.relationship("User", backref="mentee_profile", uselist=False)

#------------ table supervisor details-------------------
class SupervisorProfile(db.Model):
    __tablename__ = "supervisor_profile"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("signup_details.id"), nullable=False, unique=True)

    organisation = db.Column(db.String(150))
    whatsapp = db.Column(db.String(20))
    location = db.Column(db.String(100))
    role = db.Column(db.String(100))
    additional_info = db.Column(db.Text)
    profile_picture = db.Column(db.String(100))

    # One-to-one relationship with User
    user = db.relationship("User", backref="supervisor_profile", uselist=False)

#------------Institution Table-------------------
class Institution(db.Model):
    __tablename__ = "institutions"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("signup_details.id"), nullable=True, unique=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    email_domain = db.Column(db.String(100), nullable=True)  # For auto-detection
    contact_person = db.Column(db.String(100))
    contact_email = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100))
    website = db.Column(db.String(200))
    institution_type = db.Column(db.String(50), default="other")  # university, college, school, other
    status = db.Column(db.String(20), default="active")  # active, inactive
    profile_picture = db.Column(db.String(100), nullable=True)  # Store image filename
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with User (institution admin) - via user_id
    user = db.relationship("User", backref="institution_profile", uselist=False, foreign_keys="Institution.user_id")
    
    def __repr__(self):
        return f"<Institution {self.name}>"

#------------------mentorship request table-------------------
class MentorshipRequest(db.Model):
    __tablename__ = "mentorship_requests"
    id = db.Column(db.Integer, primary_key=True)
    mentee_id = db.Column(db.Integer, db.ForeignKey("signup_details.id"), nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey("signup_details.id"), nullable=False)
    
    # Details from the form
    purpose = db.Column(db.String(1000))  # career guidance / interview prep / skill development / others
    mentor_type = db.Column(db.String(20))   # anchor / special
    term = db.Column(db.String(20))          # short / long
    duration_months = db.Column(db.Integer)  # auto set depending on rules
    why_need_mentor = db.Column(db.Text, nullable=False)
    
    # Request status tracking
    mentor_status = db.Column(db.String(20), default="pending") # 'pending', 'accepted', 'rejected'
    supervisor_status = db.Column(db.String(20), default="pending") # 'pending', 'approved', 'rejected'
    final_status = db.Column(db.String(20), default="pending") # 'pending', 'approved', 'rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationships for easy access
    mentee = db.relationship("User", foreign_keys=[mentee_id], backref="sent_requests")
    mentor = db.relationship("User", foreign_keys=[mentor_id], backref="received_requests")

#------------Meeting Request table-------------------
class MeetingRequest(db.Model):
    __tablename__ = "meeting_requests"
    id = db.Column(db.Integer, primary_key=True)

    # Who created the request (requester) and who it's for
    requester_id = db.Column(db.Integer, db.ForeignKey("signup_details.id"), nullable=False)
    requested_to_id = db.Column(db.Integer, db.ForeignKey("signup_details.id"), nullable=False)

    # Meeting details
    meeting_title = db.Column(db.String(200), nullable=False)
    meeting_description = db.Column(db.Text)
    meeting_date = db.Column(db.Date, nullable=False)
    meeting_time = db.Column(db.Time, nullable=False)   # start time
    meeting_duration = db.Column(db.Integer, default=60)  # in minutes

    # Google Calendar info
    meet_link = db.Column(db.String(500), nullable=True)
    gcal_event_id = db.Column(db.String(200), nullable=True)

    # Status tracking
    status = db.Column(db.String(20), default="pending")  # 'pending', 'approved', 'rejected', 'rescheduled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Reschedule fields
    is_rescheduled = db.Column(db.Boolean, default=False)
    reschedule_reason = db.Column(db.Text, nullable=True)  # Required if rescheduling within 8 hours
    original_date = db.Column(db.Date, nullable=True)  # Store original date before reschedule
    original_time = db.Column(db.Time, nullable=True)  # Store original time before reschedule
    rescheduled_at = db.Column(db.DateTime, nullable=True)  # When was it rescheduled
    rescheduled_by_id = db.Column(db.Integer, db.ForeignKey("signup_details.id"), nullable=True)

    # Relationships
    requester = db.relationship("User", foreign_keys=[requester_id], backref="sent_meeting_requests")
    requested_to = db.relationship("User", foreign_keys=[requested_to_id], backref="received_meeting_requests")
    rescheduled_by = db.relationship("User", foreign_keys=[rescheduled_by_id])


#------------Master Task Table-------------------
class MasterTask(db.Model):
    __tablename__ = "MasterTask"
    
    id = db.Column(db.Integer, primary_key=True)
    meeting_number = db.Column(db.Integer, nullable=False, unique=True)
    month = db.Column(db.String(50), nullable=False)
    journey_phase = db.Column(db.String(200), nullable=False)
    purpose_of_call = db.Column(db.Text, nullable=False)
    mentor_focus = db.Column(db.Text, nullable=False)
    mentee_focus = db.Column(db.Text, nullable=False)
    program_incharge_actions = db.Column(db.Text, nullable=False)
    meeting_plan_overview = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return f"<MeetingStructure {self.meeting_number}: {self.month}>"

class MenteeTask(db.Model):
    __tablename__ = "mentee_tasks"
    
    id = db.Column(db.Integer, primary_key=True)
    mentee_id = db.Column(db.Integer, db.ForeignKey("signup_details.id"), nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey("signup_details.id"), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey("MasterTask.id"), nullable=False)
    meeting_number = db.Column(db.Integer, nullable=False)
    month = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default="pending")
    progress = db.Column(db.Integer, default=0)
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    completed_date = db.Column(db.DateTime)
    
    # Relationships
    mentee = db.relationship("User", foreign_keys=[mentee_id])
    mentor = db.relationship("User", foreign_keys=[mentor_id])
    master_task = db.relationship("MasterTask")

class PersonalTask(db.Model):
    __tablename__ = "personal_tasks"
    
    id = db.Column(db.Integer, primary_key=True)
    mentee_id = db.Column(db.Integer, db.ForeignKey("signup_details.id"), nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey("signup_details.id"), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    priority = db.Column(db.String(20), default="medium")  # low, medium, high
    status = db.Column(db.String(20), default="pending")  # pending, in-progress, completed
    progress = db.Column(db.Integer, default=0)  # 0-100%
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    completed_date = db.Column(db.DateTime)
    
    # Relationship
    mentee = db.relationship("User", foreign_keys=[mentee_id])
    mentor = db.relationship("User", foreign_keys=[mentor_id])


#------------Task feedback Table-------------------
class TaskRating(db.Model):
    __tablename__ = "task_ratings"
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, nullable=False)  # Can be from MenteeTask or PersonalTask
    task_type = db.Column(db.String(20), nullable=False)  # 'master' or 'personal'
    mentee_id = db.Column(db.Integer, db.ForeignKey("signup_details.id"), nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey("signup_details.id"), nullable=False)
    
    # Rating (1-5 stars)
    rating = db.Column(db.Integer, nullable=False)  # 1 to 5
    
    # Feedback
    feedback = db.Column(db.Text)
    strengths = db.Column(db.Text)  # What mentee did well
    improvements = db.Column(db.Text)  # Areas for improvement
    
    # Timestamps
    rated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    mentee = db.relationship("User", foreign_keys=[mentee_id])
    mentor = db.relationship("User", foreign_keys=[mentor_id])
    
    def __repr__(self):
        return f"<TaskRating {self.rating}/5 for task {self.task_id}>"

def assign_master_tasks_to_mentorship(mentorship_request):
    print("🔧 assign_master_tasks_to_mentorship function called")
    
    try:
        # Check mentorship request data
        print(f"📋 Mentorship Details:")
        print(f"   - Mentee ID: {mentorship_request.mentee_id}")
        print(f"   - Mentor ID: {mentorship_request.mentor_id}") 
        print(f"   - Duration: {mentorship_request.duration_months} months")
        
        # ✅ Use current time since created_at doesn't exist or is None
        start_date = datetime.utcnow()
        print(f"   - Start Date (Current Time): {start_date}")
        
        # Get master tasks
        master_tasks = MasterTask.query\
            .order_by(MasterTask.meeting_number)\
            .limit(20)\
            .all()
        
        print(f"📁 Top {len(master_tasks)} master tasks found (limited to 20)")
        
        if not master_tasks:
            print("❌ NO MASTER TASKS IN DATABASE!")
            return []
        
        assigned_tasks = []
        start_date = datetime.utcnow()

        
        for i, master_task in enumerate(master_tasks):
            print(f"\n🎯 Processing Task {i+1}:")
            print(f"   Month: {master_task.month}")
            print(f"   Meeting Number: {master_task.meeting_number}")
            print(f"   Purpose: {master_task.purpose_of_call[:50]}...")  # ✅ Use existing field
            
            due_date = calculate_due_date(start_date, master_task.month)
            print(f"   Final Due Date: {due_date}")
            
            # Create mentee task
            mentee_task = MenteeTask(
                mentee_id=mentorship_request.mentee_id,
                mentor_id=mentorship_request.mentor_id,
                task_id=master_task.id,
                meeting_number=master_task.meeting_number,
                month=master_task.month,
                due_date=due_date
            )
            
            db.session.add(mentee_task)
            assigned_tasks.append(mentee_task)
        
        # Commit se pehle
        print(f"\n💾 Committing {len(assigned_tasks)} tasks to database...")
        db.session.commit()
        print("✅ Database commit successful!")
        
        return assigned_tasks
        
    except Exception as e:
        print(f"❌ ERROR in task assignment: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return []

def calculate_due_date(start_date, month_string):
    """
    Month string (e.g., "Month 1", "Month 2") ko due date mein convert kare
    """
    try:
        print(f"📅 CALCULATION STARTED:")
        print(f"   Start Date: {start_date}")
        print(f"   Month String: {month_string}")
        
        # ✅ Ensure start_date is not None
        if start_date is None:
            start_date = datetime.utcnow()
            print(f"   ⚠️  Start date was None, using current time: {start_date}")
        
        # Month string se number nikalne ka logic
        if "Month" in month_string:
            month_num = int(month_string.split(" ")[1])
        else:
            # Try to extract any number from string
            import re
            numbers = re.findall(r'\d+', month_string)
            month_num = int(numbers[0]) if numbers else 1
        
        print(f"   Extracted month number: {month_num}")
        
        # Start date se days add karo (30 days per month)
        days_to_add = 30 * month_num
        print(f"   Days to add: {days_to_add}")
        
        due_date = start_date + timedelta(days=days_to_add)
        
        print(f"   Calculated due date: {due_date}")
        print("📅 CALCULATION COMPLETED\n")
        
        return due_date
        
    except Exception as e:
        print(f"❌ Error in calculate_due_date: {str(e)}")
        import traceback
        traceback.print_exc()
        # Fallback: 30 days from current time
        return datetime.utcnow() + timedelta(days=30)

def calculate_due_date(start_date, month_string):
    """
    Month string (e.g., "Month 1", "Month 2") ko due date mein convert kare
    """
    try:
        print(f"📅 CALCULATION STARTED:")
        print(f"   Start Date: {start_date}")
        print(f"   Month String: {month_string}")
        print(f"   Start Date Type: {type(start_date)}")
        
        # Month string se number nikalne ka logic
        if "Month" in month_string:
            month_num = int(month_string.split(" ")[1])
        else:
            # Try to extract any number from string
            import re
            numbers = re.findall(r'\d+', month_string)
            month_num = int(numbers[0]) if numbers else 1
        
        print(f"   Extracted month number: {month_num}")
        
        # Start date se days add karo (30 days per month)
        days_to_add = 30 * month_num
        print(f"   Days to add: {days_to_add}")
        
        due_date = start_date + timedelta(days=days_to_add)
        
        print(f"   Calculated due date: {due_date}")
        print(f"   Due Date Type: {type(due_date)}")
        print("📅 CALCULATION COMPLETED\n")
        
        return due_date
        
    except Exception as e:
        print(f"❌ Error in calculate_due_date: {str(e)}")
        import traceback
        traceback.print_exc()
        # Fallback: 30 days from start
        return start_date + timedelta(days=30)

# Context processor to make profile_complete available in all templates
@app.context_processor
def inject_profile_complete():
    profile_complete = True  # Default to True (no popup)
    
    if "email" in session and session.get("user_type") in ["1", "2"]:
        user = User.query.filter_by(email=session["email"]).first()
        if user:
            profile_complete = check_profile_complete(user.id, session.get("user_type"))    
    return dict(profile_complete=profile_complete)


# ---------- Profile Completion Check Function ----------
def check_profile_complete(user_id, user_type):
    """
    Check if user profile is FULLY complete with ALL mandatory fields
    Returns True only if ALL required fields are filled, False otherwise
    """
    print(f"🔍 Checking profile completion for user_id: {user_id}, user_type: {user_type}")
    
    if user_type == "1":  # Mentor
        profile = MentorProfile.query.filter_by(user_id=user_id).first()
        print(f"📊 Mentor profile found: {profile is not None}")
        if profile:
            # Check if ALL mandatory fields are filled (including profile picture)
            has_all_required = all([
                profile.profession, 
                profile.organisation, 
                profile.whatsapp,
                profile.location,
                profile.education,
                profile.years_of_experience,
                profile.skills,
                profile.role,
                profile.industry_sector,
                profile.language,
                profile.linkedin_link,
                profile.mentorship_topics,
                profile.mentorship_type_preference,
                profile.preferred_communication,
                profile.availability,
                profile.connect_frequency,
                profile.preferred_duration,
                profile.why_mentor,
                profile.mentorship_philosophy,
                profile.mentorship_motto,
                profile.profile_picture  # Profile picture is now mandatory
            ])
            print(f"✅ Mentor profile complete: {has_all_required}")
            return has_all_required
        print("❌ No mentor profile found")
        return False
    
    elif user_type == "2":  # Mentee
        profile = MenteeProfile.query.filter_by(user_id=user_id).first()
        print(f"📊 Mentee profile found: {profile is not None}")
        if profile:
            # Check if ALL mandatory fields are filled (including profile picture)
            has_all_required = all([
                profile.dob,
                profile.school_college_name, 
                profile.mobile_number,
                profile.whatsapp_number,
                profile.govt_private,
                profile.stream,
                profile.class_year,
                profile.favourite_subject,
                profile.goal,
                profile.parent_name,
                profile.parent_mobile,
                profile.comments,
                profile.terms_agreement,
                profile.profile_picture  # Profile picture is now mandatory
            ])
            print(f"✅ Mentee profile complete: {has_all_required}")
            return has_all_required
        print("❌ No mentee profile found")
        return False
    
    elif user_type == "0":  # Supervisor
        profile = SupervisorProfile.query.filter_by(user_id=user_id).first()
        print(f"📊 Supervisor profile found: {profile is not None}")
        if profile:
            has_all_required = all([
                profile.organisation,
                profile.whatsapp,
                profile.location,
                profile.role,
                profile.additional_info,
                profile.profile_picture  # Profile picture is now mandatory
            ])
            print(f"✅ Supervisor profile complete: {has_all_required}")
            return has_all_required
        print("❌ No supervisor profile found")
        return False
    
    elif user_type == "3":  # Institution
        institution = Institution.query.filter_by(user_id=user_id).first()
        print(f"📊 Institution profile found: {institution is not None}")
        if institution:
            has_all_required = all([
                institution.name,
                institution.contact_person,
                institution.contact_email,
                institution.contact_phone,
                institution.address,
                institution.city,
                institution.state,
                institution.country,
                institution.profile_picture  # Profile picture is now mandatory
            ])
            print(f"✅ Institution profile complete: {has_all_required}")
            return has_all_required
        print("❌ No institution profile found")
        return False
    
    print(f"⚠️ Unknown user type: {user_type}")
    return True  # Default to True for unknown types (no popup)

# Decorator to enforce profile completion
def profile_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("signin"))
        
        user = User.query.filter_by(email=session["email"]).first()
        user_type = session.get("user_type")
        
        if not user:
            return redirect(url_for("signin"))
        
        # Check if profile is complete
        if not check_profile_complete(user.id, user_type):
            flash("Please complete your profile first before accessing this section.", "warning")
            # Redirect to appropriate profile edit page
            if user_type == "1":
                return redirect(url_for("editmentorprofile"))
            elif user_type == "2":
                return redirect(url_for("editmenteeprofile"))
            elif user_type == "0":
                return redirect(url_for("editsupervisorprofile"))
            elif user_type == "3":
                return redirect(url_for("editinstitutionprofile"))
        
        return f(*args, **kwargs)
    return decorated_function

#-------------HOME----------------
@app.route("/")
def home():
    return render_template("index.html")

#--------------SIGNUP----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        user_type = request.form.get("user-type")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")
        institution_name = request.form.get("institution", "")

        # Password check
        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for("signup"))

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("User already exists! Please sign in.", "error")
            return redirect(url_for("signin"))

        # Hash password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        
        # Create new user first
        new_user = User(
            name=name, 
            email=email, 
            password=hashed_password, 
            user_type=user_type, 
            institution=institution_name
        )
        db.session.add(new_user)
        db.session.flush()  # Get user ID
        
        # For institution admin (user_type = "3"), create/link institution profile
        if user_type == "3":
            # Check if institution exists
            institution = Institution.query.filter_by(name=institution_name).first()
            if not institution:
                # Create new institution with admin user link
                institution = Institution(
                    user_id=new_user.id,
                    name=institution_name, 
                    contact_person=name,
                    contact_email=email,
                    status="active"
                )
                db.session.add(institution)
                db.session.flush()
            
            # Link user to institution
            new_user.institution_id = institution.id
        
        db.session.commit()

        # Store in session
        session["email"] = email
        session["user_type"] = user_type
        session["user_id"] = new_user.id
        session["user_name"] = name

        # Redirect to profile completion (mandatory)
        if user_type == "1":
            flash("Welcome! Please complete your profile to continue.", "info")
            return redirect(url_for("editmentorprofile"))
        elif user_type == "2":
            flash("Welcome! Please complete your profile to continue.", "info")
            return redirect(url_for("editmenteeprofile"))
        elif user_type == "0":
            flash("Welcome! Please complete your profile to continue.", "info")
            return redirect(url_for("editsupervisorprofile"))
        elif user_type == "3":  # Institution admin
            flash("Welcome! Please complete your profile to continue.", "info")
            return redirect(url_for("editinstitutionprofile"))
        
        return redirect(url_for("signin"))

    # Show signup form with active institutions
    institutions = Institution.query.filter_by(status="active").all()
    return render_template("auth/signup.html", institutions=institutions)

    return render_template("auth/signup.html")

#--------------SIGNIN----------------
@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        session.permanent = True
        email = request.form["email"]
        password = request.form["password"]

        # fetch user from "database"
        user = User.query.filter_by(email=email).first()

        # Check if user exists
        if not user:
            return "User not found! Please sign up first."

        # Check password
        if not check_password_hash(user.password, password):
            return "Incorrect password!"

        # Save session
        session["email"] = user.email
        session["user_type"] = user.user_type
        session["user_id"] = user.id
        session["user_name"] = user.name

        # Redirect based on role
        if user.user_type == "1":
            return redirect(url_for("mentordashboard"))
        elif user.user_type == "2":
            return redirect(url_for("menteedashboard"))
        elif user.user_type == "0":
            return redirect(url_for("supervisordashboard"))
        elif user.user_type == "3":
            return redirect(url_for("institutiondashboard"))
        
        
        return redirect(url_for("home"))

   
    return render_template("auth/signin.html")

# ------------------- GOOGLE OAUTH LOGIN -------------------
@app.route("/google_login")
def google_login():
    """Redirect to Google OAuth consent screen for login"""
    # Check if user is already logged in
    if "email" in session and "user_id" in session:
        user = User.query.get(session["user_id"])
        if user:
            # User already logged in, redirect to dashboard
            if user.user_type == "1":
                return redirect(url_for("mentordashboard"))
            elif user.user_type == "2":
                return redirect(url_for("menteedashboard"))
            elif user.user_type == "0":
                return redirect(url_for("supervisordashboard"))
            elif user.user_type == "3":
                return redirect(url_for("institutiondashboard"))
            else:
                return redirect(url_for("select_user_type"))
    
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=LOGIN_SCOPES,  # Use login scopes only
        redirect_uri=REDIRECT_URI
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='select_account'  # Allow user to select account but skip consent if already authorized
    )
    session['state'] = state
    session['oauth_type'] = 'login'  # Mark this as login flow
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    """Handle Google OAuth callback"""
    print("\n" + "="*60)
    print("🔄 CALLBACK ROUTE CALLED")
    print("="*60)
    
    try:
        print(f"📍 Step 1: Getting state from session")
        state = session.get('state')
        print(f"   State: {state}")
        
        print(f"📍 Step 2: Creating Flow from client secrets")
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=LOGIN_SCOPES,  # Use login scopes
            state=state,
            redirect_uri=REDIRECT_URI
        )
        print(f"   ✅ Flow created")
        
        print(f"📍 Step 3: Getting authorization response")
        authorization_response = request.url
        print(f"   URL: {authorization_response}")
        
        print(f"📍 Step 4: Fetching token")
        # Set environment variable to allow scope changes
        os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
        flow.fetch_token(authorization_response=authorization_response)
        print(f"   ✅ Token fetched")
        
        print(f"📍 Step 5: Getting credentials")
        credentials = flow.credentials
        access_token = credentials.token
        print(f"   ✅ Credentials obtained")
        print(f"   Token: {access_token[:30]}..." if access_token else "   No token")
        
        print(f"📍 Step 6: Getting user info via HTTP request")
        # Use requests library to get user info directly with access token
        import requests as http_requests
        
        headers = {'Authorization': f'Bearer {access_token}'}
        user_info_response = http_requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers=headers
        )
        
        print(f"   Response status: {user_info_response.status_code}")
        
        if user_info_response.status_code != 200:
            print(f"   ❌ Error response: {user_info_response.text}")
            flash("Error getting user info from Google. Please try again.", "error")
            return redirect(url_for("signin"))
        
        user_info = user_info_response.json()
        print(f"   ✅ User info retrieved")
        
        google_id = user_info.get('id')
        email = user_info.get('email')
        name = user_info.get('name', email.split('@')[0] if email else 'User')
        picture_url = user_info.get('picture')
        
        print(f"\n📊 Google User Data:")
        print(f"   Name: {name}")
        print(f"   Email: {email}")
        print(f"   Google ID: {google_id}")
        print(f"   Picture: {picture_url}")
        
        if not email:
            print(f"   ❌ ERROR: No email in response!")
            flash("Could not get email from Google. Please try again.", "error")
            return redirect(url_for("signin"))
        
        print(f"\n📍 Step 7: Checking if user exists in database")
        user = User.query.filter_by(email=email).first()
        
        if user:
            print(f"   ✅ Existing user found: {user.email}")
            print(f"   User ID: {user.id}")
            print(f"   User Type: {user.user_type}")
            
            # Update Google ID if not set
            if not user.google_id:
                user.google_id = google_id
                user.oauth_provider = 'google'
                user.profile_picture_url = picture_url
                db.session.commit()
                print(f"   ✅ Updated user with Google ID")
            
            print(f"\n📍 Step 8: Setting session for existing user")
            session.permanent = True
            session["email"] = user.email
            session["user_type"] = user.user_type
            session["user_id"] = user.id
            session["user_name"] = user.name
            print(f"   ✅ Session set")
            print(f"      Email: {session.get('email')}")
            print(f"      Type: {session.get('user_type')}")
            print(f"      ID: {session.get('user_id')}")
            
            print(f"\n📍 Step 9: Redirecting based on user type")
            if user.user_type == "1":
                print(f"   ➡️ Redirecting to mentordashboard")
                return redirect(url_for("mentordashboard"))
            elif user.user_type == "2":
                print(f"   ➡️ Redirecting to menteedashboard")
                return redirect(url_for("menteedashboard"))
            elif user.user_type == "0":
                print(f"   ➡️ Redirecting to supervisordashboard")
                return redirect(url_for("supervisordashboard"))
            elif user.user_type == "3":
                print(f"   ➡️ Redirecting to institutiondashboard")
                return redirect(url_for("institutiondashboard"))
            else:
                print(f"   ➡️ No user type set, redirecting to select_user_type")
                return redirect(url_for("select_user_type"))
        else:
            print(f"   ❌ User not found, creating new account")
            
            print(f"\n📍 Step 8: Creating new user object")
            new_user = User(
                name=name,
                email=email,
                google_id=google_id,
                oauth_provider='google',
                profile_picture_url=picture_url,
                oauth_created_at=datetime.utcnow()
            )
            print(f"   ✅ User object created")
            print(f"      Name: {new_user.name}")
            print(f"      Email: {new_user.email}")
            print(f"      Google ID: {new_user.google_id}")
            
            print(f"\n📍 Step 9: Adding user to database session")
            db.session.add(new_user)
            print(f"   ✅ User added to session")
            
            print(f"\n📍 Step 10: Committing to database")
            db.session.commit()
            print(f"   ✅ Committed successfully")
            print(f"   New User ID: {new_user.id}")
            
            print(f"\n📍 Step 11: Setting session for new user")
            session.permanent = True
            session["email"] = email
            session["user_id"] = new_user.id
            session["oauth_user"] = True
            session["user_name"] = new_user.name
            print(f"   ✅ Session set")
            print(f"      Email: {session.get('email')}")
            print(f"      ID: {session.get('user_id')}")
            
            print(f"\n📍 Step 12: Redirecting to select_user_type")
            print(f"   ➡️ Redirecting to select_user_type")
            print("="*60 + "\n")
            return redirect(url_for("select_user_type"))
    
    except Exception as e:
        print(f"\n❌ ERROR in callback: {str(e)}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        print("="*60 + "\n")
        flash("Error during Google login. Please try again.", "error")
        return redirect(url_for("signin"))

@app.route("/select_user_type", methods=["GET", "POST"])
def select_user_type():
    """Allow OAuth users to select their user type"""
    if "email" not in session:
        print("❌ No email in session - redirecting to signin")
        return redirect(url_for("signin"))
    
    print(f"✅ Email in session: {session.get('email')}")
    
    user = User.query.filter_by(email=session["email"]).first()
    
    if not user:
        print(f"❌ User not found for email: {session.get('email')}")
        return redirect(url_for("signin"))
    
    print(f"✅ User found: {user.email}, Current type: {user.user_type}")
    
    # If user already has a type, redirect to dashboard
    if user.user_type:
        session.permanent = True
        session["user_type"] = user.user_type
        session["user_id"] = user.id
        
        print(f"📝 User already has type: {user.user_type}, redirecting to dashboard")
        
        if user.user_type == "1":
            return redirect(url_for("mentordashboard"))
        elif user.user_type == "2":
            return redirect(url_for("menteedashboard"))
        elif user.user_type == "0":
            return redirect(url_for("supervisordashboard"))
        elif user.user_type == "3":
            return redirect(url_for("institutiondashboard"))
    
    if request.method == "POST":
        user_type = request.form.get("user_type")
        
        print(f"📝 User selected type: {user_type}")
        
        if user_type not in ["0", "1", "2", "3"]:
            flash("Invalid user type selected", "error")
            return redirect(url_for("select_user_type"))
        
        # Update user type
        user.user_type = user_type
        db.session.commit()
        
        print(f"✅ User type saved to database: {user_type}")
        
        # Update session
        session.permanent = True
        session["user_type"] = user_type
        session["user_id"] = user.id
        session["user_name"] = user.name
        
        print(f"📝 Session updated - Type: {session.get('user_type')}, ID: {session.get('user_id')}")
        
        # Redirect to profile completion
        if user_type == "1":
            flash("Welcome! Please complete your mentor profile to continue.", "info")
            return redirect(url_for("editmentorprofile"))
        elif user_type == "2":
            flash("Welcome! Please complete your mentee profile to continue.", "info")
            return redirect(url_for("editmenteeprofile"))
        elif user_type == "0":
            flash("Welcome! Please complete your supervisor profile to continue.", "info")
            return redirect(url_for("editsupervisorprofile"))
        elif user_type == "3":
            flash("Welcome! Please complete your institution profile to continue.", "info")
            return redirect(url_for("editinstitutionprofile"))
    
    return render_template("auth/select_user_type.html", user=user)

# ------------------ DASHBOARDS ------------------
@app.route("/mentordashboard", methods=["GET", "POST"])
@profile_required
def mentordashboard():
    if "email" not in session or session.get("user_type") != "1":  # Only mentors
        return redirect(url_for("signin"))

    mentor_id = session.get("user_id")

    
    # ------------------- Check Profile Completion -------------------
    user = User.query.filter_by(email=session["email"]).first()
    profile_complete = check_profile_complete(user.id, "1")



    # ------------------- mentee requests -------------------
            # Fetch current mentor
    mentor = User.query.filter_by(email=session["email"]).first()


    if not mentor:
            flash("Mentor profile not found.", "error")
            return redirect(url_for("signin"))

        # Fetch incoming mentorship requests for this mentor
    incoming_requests = MentorshipRequest.query.filter_by(
            mentor_id=mentor.id
        ).all()

        # Fetch all mentees
    all_mentees = MenteeProfile.query.all()

        # Unique filter values from mentees
    streams = [row.stream for row in MenteeProfile.query.with_entities(MenteeProfile.stream).distinct() if row.stream]
    schools = [row.school_college_name for row in MenteeProfile.query.with_entities(MenteeProfile.school_college_name).distinct() if row.school_college_name]
    goals = [row.goal for row in MenteeProfile.query.with_entities(MenteeProfile.goal).distinct() if row.goal]

        # Get a specific mentee for the profile section (if needed)
        # For example, get the first mentee from the requests if available
    example_mentee = None
    if incoming_requests and incoming_requests[0].mentee:
            example_mentee = incoming_requests[0].mentee

        # Mentor profile info
    mentor_info = {
            "full_name": mentor.name, 
            "username": mentor.email,
            "date_time": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }



    # ------------------- find mentees (with filters) -------------------
    query = MenteeProfile.query.join(User, MenteeProfile.user_id == User.id)

    search_query = request.args.get("search", "").lower()
    stream_filter = request.args.get("stream", "")
    school_filter = request.args.get("school", "")
    goal_filter = request.args.get("goal", "")

    if search_query:
        query = query.filter(
            or_(
                User.name.ilike(f"%{search_query}%"),
                MenteeProfile.stream.ilike(f"%{search_query}%"),
                MenteeProfile.school_college_name.ilike(f"%{search_query}%")
            )
        )
    if stream_filter:
        query = query.filter(MenteeProfile.stream == stream_filter)
    if school_filter:
        query = query.filter(MenteeProfile.school_college_name == school_filter)
    if goal_filter:
        query = query.filter(MenteeProfile.goal == goal_filter)

    all_mentees = query.all()

    # dropdown options
    streams = sorted({m.stream for m in MenteeProfile.query.distinct() if m.stream})
    schools = sorted({m.school_college_name for m in MenteeProfile.query.distinct() if m.school_college_name})
    goals = sorted({m.goal for m in MenteeProfile.query.distinct() if m.goal})

    return render_template(
        "mentor/mentordashboard.html",
        mentorship_requests=incoming_requests,
        all_mentees=all_mentees,
        streams=streams,
        schools=schools,
        goals=goals,
        incoming_requests=incoming_requests,
        mentor_info=mentor_info,
        active_section="dashboard",
        show_sidebar=True,
        mentee=example_mentee,
        profile_complete=profile_complete
    )

@app.route("/mentor_mentorship_request", methods=["GET", "POST"])
def mentor_mentorship_request():
    if "email" not in session or session.get("user_type") != "1":  # Only mentors
        return redirect(url_for("signin"))

    mentor_id = session.get("user_id")

    user = User.query.filter_by(email=session["email"]).first()
    profile_complete = check_profile_complete(user.id, "1")

    # ------------------- mentee requests -------------------
            # Fetch current mentor
    mentor = User.query.filter_by(email=session["email"]).first()

    if not mentor:
            flash("Mentor profile not found.", "error")
            return redirect(url_for("signin"))

        # Fetch incoming mentorship requests for this mentor
    incoming_requests = MentorshipRequest.query.filter_by(
            mentor_id=mentor.id).filter(
                (MentorshipRequest.mentor_status == "pending") | 
                (MentorshipRequest.supervisor_status == "pending")
        ).all()


    mentee_id = request.args.get("mentee_id")  # or request.form.get("mentee_id")
    mentee = MenteeProfile.query.get(mentee_id)

        # Fetch all mentees
    all_mentees = MenteeProfile.query.all()

        # Unique filter values from mentees
    streams = [row.stream for row in MenteeProfile.query.with_entities(MenteeProfile.stream).distinct() if row.stream]
    schools = [row.school_college_name for row in MenteeProfile.query.with_entities(MenteeProfile.school_college_name).distinct() if row.school_college_name]
    goals = [row.goal for row in MenteeProfile.query.with_entities(MenteeProfile.goal).distinct() if row.goal]

        # Get a specific mentee for the profile section (if needed)
        # For example, get the  first mentee from the requests if available
    example_mentee = None
    if incoming_requests and incoming_requests[0].mentee:
            example_mentee = incoming_requests[0].mentee

        # Mentor profile info
    mentor_info = {
            "full_name": mentor.name, 
            "username": mentor.email,

        }


    existing_pending_request = None
    existing_active_mentorship = None





    return render_template(
        "mentor/mentor_mentorship_request.html",
        mentorship_requests=incoming_requests,
        all_mentees=all_mentees,
        streams=streams,   
        schools=schools,
        goals=goals,
        incoming_requests=incoming_requests,
        mentor_info=mentor_info,
        active_section="meetingrequests",
        show_sidebar=True,
        mentee=example_mentee,
        profile_complete=profile_complete
    )

@app.route("/menteedashboard")
@profile_required
def menteedashboard():
    if "email" in session and session.get("user_type") == "2":
        # Fetch current mentee
        user = User.query.filter_by(email=session["email"]).first()

        profile_complete = check_profile_complete(user.id, "2")

        all_mentors = MentorProfile.query.filter_by().all()



        all_mentors = MentorProfile.query.filter_by().all()

        # unique filter value from db
        professions = [row.profession for row in MentorProfile.query.with_entities(MentorProfile.profession).distinct() if row]
        locations = [row.location for row in MentorProfile.query.with_entities(MentorProfile.location).distinct() if row.location]
        educations = [row.education for row in MentorProfile.query.with_entities(MentorProfile.education).distinct() if row.education]
        experiences = [row.years_of_experience for row in MentorProfile.query.with_entities(MentorProfile.years_of_experience).distinct() if row.years_of_experience]


        # Optionally, fetch mentors already assigned to this mentee
        # This depends if you have a "mentorship" table, for now we just show all mentors
    
        return render_template(
            "mentee/menteedashboard.html",
            all_mentors=all_mentors,
            professions=[row.profession for row in MentorProfile.query.with_entities(MentorProfile.profession).distinct() if row.profession],
            locations=[row.location for row in MentorProfile.query.with_entities(MentorProfile.location).distinct() if row.location],
            educations=[row.education for row in MentorProfile.query.with_entities(MentorProfile.education).distinct() if row.education],
            experiences=[row.years_of_experience for row in MentorProfile.query.with_entities(MentorProfile.years_of_experience).distinct() if row.years_of_experience],
            show_sidebar=True,
            profile_complete=profile_complete
        )




    return redirect(url_for("signin"))

@app.route("/supervisordashboard")
@profile_required
def supervisordashboard():
    if "email" not in session or session.get("user_type") != "0":
        return redirect(url_for("signin"))

    user = User.query.filter_by(email=session["email"]).first()
    profile_complete = check_profile_complete(user.id, "0")



    source_page = request.args.get("from", "supervisor")

    # ----------------- Mentors -----------------
    mentor_query = MentorProfile.query
    profession = request.args.get("profession")
    location = request.args.get("location")
    education = request.args.get("education")
    experience = request.args.get("experience")

    if profession:
        mentor_query = mentor_query.filter_by(profession=profession)
    if location:
        mentor_query = mentor_query.filter_by(location=location)
    if education:
        mentor_query = mentor_query.filter_by(education=education)
    if experience:
        if experience == "0-2":
            mentor_query = mentor_query.filter(cast(MentorProfile.years_of_experience, Integer).between(0, 2))
        elif experience == "3-5":
            mentor_query = mentor_query.filter(cast(MentorProfile.years_of_experience, Integer).between(3, 5))
        elif experience == "6-10":
            mentor_query = mentor_query.filter(cast(MentorProfile.years_of_experience, Integer).between(6, 10))
        elif experience == "10+":
            mentor_query = mentor_query.filter(cast(MentorProfile.years_of_experience, Integer) >= 10)

    mentors = mentor_query.all()

    options = {
        "professions": sorted({row[0] for row in MentorProfile.query.with_entities(MentorProfile.profession).distinct() if row[0]}),
        "locations": sorted({row[0] for row in MentorProfile.query.with_entities(MentorProfile.location).distinct() if row[0]}),
        "educations": sorted({row[0] for row in MentorProfile.query.with_entities(MentorProfile.education).distinct() if row[0]}),
        "experiences": sorted({row[0] for row in MentorProfile.query.with_entities(MentorProfile.years_of_experience).distinct() if row[0]}),
    }

    # ----------------- Mentees -----------------
    mentee_query = MenteeProfile.query.join(User, MenteeProfile.user_id == User.id)
    search_query = request.args.get("search", "").lower()
    stream_filter = request.args.get("stream", "")
    school_filter = request.args.get("school", "")
    goal_filter = request.args.get("goal", "")

    if search_query:
        mentee_query = mentee_query.filter(
            or_(
                User.name.ilike(f"%{search_query}%"),
                MenteeProfile.stream.ilike(f"%{search_query}%"),
                MenteeProfile.school_college_name.ilike(f"%{search_query}%")
            )
        )
    if stream_filter:
        mentee_query = mentee_query.filter(MenteeProfile.stream == stream_filter)
    if school_filter:
        mentee_query = mentee_query.filter(MenteeProfile.school_college_name == school_filter)
    if goal_filter:
        mentee_query = mentee_query.filter(MenteeProfile.goal == goal_filter)

    all_mentees = mentee_query.all()

    # ----------------- Mentee dropdowns -----------------
    mentee_streams = sorted({row[0] for row in MenteeProfile.query.with_entities(MenteeProfile.stream).distinct() if row[0]})
    mentee_schools = sorted({row[0] for row in MenteeProfile.query.with_entities(MenteeProfile.school_college_name).distinct() if row[0]})
    mentee_goals = sorted({row[0] for row in MenteeProfile.query.with_entities(MenteeProfile.goal).distinct() if row[0]})

    # ----------------- Requests -----------------
    all_requests = MentorshipRequest.query.all()
    mentor_requests = MentorProfile.query.filter_by(status="pending").all()
    mentee_requests = MenteeProfile.query.filter_by(status="pending").all()

    return render_template(
        "supervisor/supervisordashboard.html",
        show_sidebar=True,
        user_email=session["email"],
        mentors=mentors,
        mentees=all_mentees,
        all_requests=all_requests,
        mentor_requests=mentor_requests,
        mentee_requests=mentee_requests,
        professions=options["professions"],
        locations=options["locations"],
        educations=options["educations"],
        experiences=options["experiences"],
        mentee_streams=mentee_streams,
        mentee_schools=mentee_schools,
        mentee_goals=mentee_goals,
        active_section="dashboard",
        source_page=source_page,
        profile_complete=profile_complete
    )
    
@app.route("/institution")
def institution():
    if "email" not in session or session.get("user_type") != "0":
        return redirect(url_for("signin"))

    # Get all institutions
    institutions = Institution.query.order_by(Institution.name.asc()).all()
    
    # Get institution statistics
    institution_stats = []
    for inst in institutions:
        # Count mentors in this institution
        mentors_count = User.query.filter(
            (User.user_type == "1") & 
            ((User.institution_id == inst.id) | (User.institution == inst.name))
        ).count()
        
        # Count mentees in this institution
        mentees_count = User.query.filter(
            (User.user_type == "2") & 
            ((User.institution_id == inst.id) | (User.institution == inst.name))
        ).count()
        
        # Count active mentorships
        active_mentorships = MentorshipRequest.query\
            .join(User, MentorshipRequest.mentee_id == User.id)\
            .filter(
                ((User.institution_id == inst.id) | (User.institution == inst.name)) &
                (MentorshipRequest.final_status == "approved")
            ).count()
        
        institution_stats.append({
            'institution': inst,
            'mentors_count': mentors_count,
            'mentees_count': mentees_count,
            'active_mentorships': active_mentorships,
            'status': inst.status
        })
    
    return render_template(
        "supervisor/institution.html",
        show_sidebar=True,
        active_section="institution",
        institution_stats=institution_stats
    )

@app.route("/view_institution/<int:institution_id>")
def view_institution(institution_id):
    if "email" not in session or session.get("user_type") != "0":
        return redirect(url_for("signin"))
    
    institution = Institution.query.get_or_404(institution_id)
    
    # Get institution admin
    admin = None
    if institution.user_id:
        admin = User.query.get(institution.user_id)
    
    # Get all users from this institution
    # First get users by institution_id (new system)
    users_by_id = User.query.filter_by(institution_id=institution_id).all()
    
    # Then get users by institution name (legacy system)
    users_by_name = User.query.filter(
        User.institution == institution.name,
        User.institution_id.is_(None)  # Only get legacy records
    ).all()
    
    # Combine both lists
    all_users = list(users_by_id) + list(users_by_name)
    
    # Separate mentors and mentees
    institution_mentors = [user for user in all_users if user.user_type == "1"]
    institution_mentees = [user for user in all_users if user.user_type == "2"]
    
    # Get mentorship requests involving institution members
    # First get mentee IDs
    mentee_ids = [user.id for user in institution_mentees]
    
    institution_mentorship_requests = []
    if mentee_ids:
        institution_mentorship_requests = MentorshipRequest.query\
            .filter(MentorshipRequest.mentee_id.in_(mentee_ids))\
            .all()
    
    # Calculate statistics
    total_mentors = len(institution_mentors)
    total_mentees = len(institution_mentees)
    active_mentorships = len([req for req in institution_mentorship_requests if req.final_status == "approved"])
    
    return render_template(
        "supervisor/view_institution.html",
        show_sidebar=True,
        active_section="institution",
        institution=institution,
        admin=admin,
        institution_mentors=institution_mentors,
        institution_mentees=institution_mentees,
        mentorship_requests=institution_mentorship_requests,
        total_mentors=total_mentors,
        total_mentees=total_mentees,
        active_mentorships=active_mentorships,
        now=datetime.utcnow()
    )

@app.route("/update_institution_status/<int:institution_id>", methods=["POST"])
def update_institution_status(institution_id):
    if "email" not in session or session.get("user_type") != "0":
        return jsonify({"success": False, "message": "Unauthorized"})
    
    institution = Institution.query.get_or_404(institution_id)
    
    action = request.form.get("action")
    if action == "activate":
        institution.status = "active"
        message = "Institution activated successfully!"
    elif action == "deactivate":
        institution.status = "inactive"
        message = "Institution deactivated successfully!"
    else:
        return jsonify({"success": False, "message": "Invalid action"})
    
    try:
        db.session.commit()
        return jsonify({"success": True, "message": message, "new_status": institution.status})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})

@app.route("/institution_users/<int:institution_id>/<user_type>")
def institution_users(institution_id, user_type):
    if "email" not in session or session.get("user_type") != "0":
        return redirect(url_for("signin"))
    
    institution = Institution.query.get_or_404(institution_id)
    
    # Get users based on type
    if user_type == "mentors":
        # Get mentors by institution_id (new system)
        mentors_by_id = User.query.filter_by(
            user_type="1", 
            institution_id=institution_id
        ).all()
        
        # Get mentors by institution name (legacy system)
        mentors_by_name = User.query.filter(
            User.user_type == "1",
            User.institution == institution.name,
            User.institution_id.is_(None)
        ).all()
        
        users = list(mentors_by_id) + list(mentors_by_name)
        title = f"Mentors - {institution.name}"
        
    elif user_type == "mentees":
        # Get mentees by institution_id (new system)
        mentees_by_id = User.query.filter_by(
            user_type="2", 
            institution_id=institution_id
        ).all()
        
        # Get mentees by institution name (legacy system)
        mentees_by_name = User.query.filter(
            User.user_type == "2",
            User.institution == institution.name,
            User.institution_id.is_(None)
        ).all()
        
        users = list(mentees_by_id) + list(mentees_by_name)
        title = f"Mentees - {institution.name}"
    
    else:
        flash("Invalid user type", "error")
        return redirect(url_for("view_institution", institution_id=institution_id))
    
    return render_template(
        "supervisor/institution_users.html",
        show_sidebar=True,
        active_section="institution",
        institution=institution,
        users=users,
        user_type=user_type,
        title=title
    )



# ============ PASSWORD RESET ROUTES (Supervisor) ============

@app.route("/reset_user_password/<int:user_id>", methods=["GET", "POST"])
def reset_user_password(user_id):
    """Supervisor can reset any user's password"""
    if "email" not in session or session.get("user_type") != "0":
        flash("Only supervisors can reset passwords!", "error")
        return redirect(url_for("signin"))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == "POST":
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        
        # Validate passwords
        if not new_password or not confirm_password:
            flash("Please enter both password fields!", "error")
            return redirect(url_for("reset_user_password", user_id=user_id))
        
        if len(new_password) < 6:
            flash("Password must be at least 6 characters long!", "error")
            return redirect(url_for("reset_user_password", user_id=user_id))
        
        if new_password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for("reset_user_password", user_id=user_id))
        
        try:
            # Hash and update password
            hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=8)
            user.password = hashed_password
            db.session.commit()
            
            flash(f"✅ Password reset successfully for {user.name} ({user.email})", "success")
            return redirect(url_for("supervisordashboard"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error resetting password: {str(e)}", "error")
            return redirect(url_for("reset_user_password", user_id=user_id))
    
    return render_template(
        "supervisor/reset_password.html",
        user=user,
        show_sidebar=True
    )


@app.route("/manage_users_passwords")
def manage_users_passwords():
    """Supervisor dashboard to manage user passwords"""
    if "email" not in session or session.get("user_type") != "0":
        flash("Only supervisors can access this page!", "error")
        return redirect(url_for("signin"))
    
    # Get all users
    all_users = User.query.all()
    
    # Group by user type
    mentors = [u for u in all_users if u.user_type == "1"]
    mentees = [u for u in all_users if u.user_type == "2"]
    supervisors = [u for u in all_users if u.user_type == "0"]
    
    return render_template(
        "supervisor/manage_passwords.html",
        show_sidebar=True,
        mentors=mentors,
        mentees=mentees,
        supervisors=supervisors,
        total_users=len(all_users)
    )


# ============ CREATE ACCOUNT ROUTES (Supervisor) ============

@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    """Supervisor can create accounts for mentors, mentees, and institutions"""
    if "email" not in session or session.get("user_type") != "0":
        flash("Only supervisors can create accounts!", "error")
        return redirect(url_for("signin"))
    
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        user_type = request.form.get("user_type")
        institution_name = request.form.get("institution", "")
        
        # Validation
        if not all([name, email, password, confirm_password, user_type]):
            flash("Please fill all required fields!", "error")
            return redirect(url_for("create_account"))
        
        if len(password) < 6:
            flash("Password must be at least 6 characters long!", "error")
            return redirect(url_for("create_account"))
        
        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for("create_account"))
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists! Please use a different email.", "error")
            return redirect(url_for("create_account"))
        
        try:
            # Hash password
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            
            # Create new user
            new_user = User(
                name=name,
                email=email,
                password=hashed_password,
                user_type=user_type,
                institution=institution_name
            )
            db.session.add(new_user)
            db.session.flush()  # Get user ID
            
            # For institution admin (user_type = "3"), create institution profile
            if user_type == "3":
                institution = Institution.query.filter_by(name=institution_name).first()
                if not institution:
                    institution = Institution(
                        user_id=new_user.id,
                        name=institution_name,
                        contact_person=name,
                        contact_email=email,
                        status="active"
                    )
                    db.session.add(institution)
                    db.session.flush()
                
                new_user.institution_id = institution.id
            
            db.session.commit()
            
            flash(f"✅ Account created successfully for {name} ({email})", "success")
            return redirect(url_for("manage_created_accounts"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating account: {str(e)}", "error")
            return redirect(url_for("create_account"))
    
    # Get institutions for dropdown
    institutions = Institution.query.filter_by(status="active").all()
    
    return render_template(
        "supervisor/create_account.html",
        show_sidebar=True,
        institutions=institutions
    )


@app.route("/manage_created_accounts")
def manage_created_accounts():
    """View all accounts created by supervisors"""
    if "email" not in session or session.get("user_type") != "0":
        flash("Only supervisors can access this page!", "error")
        return redirect(url_for("signin"))
    
    # Get all users
    all_users = User.query.all()
    
    # Group by user type
    mentors = [u for u in all_users if u.user_type == "1"]
    mentees = [u for u in all_users if u.user_type == "2"]
    institutions = [u for u in all_users if u.user_type == "3"]
    
    return render_template(
        "supervisor/manage_created_accounts.html",
        show_sidebar=True,
        mentors=mentors,
        mentees=mentees,
        institutions=institutions,
        total_accounts=len(all_users)
    )


# ============ EDIT & DELETE USER ROUTES (Supervisor) ============

@app.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    """Supervisor can edit user details"""
    if "email" not in session or session.get("user_type") != "0":
        flash("Only supervisors can edit users!", "error")
        return redirect(url_for("signin"))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        institution = request.form.get("institution")
        
        # Validation
        if not all([name, email]):
            flash("Please fill all required fields!", "error")
            return redirect(url_for("edit_user", user_id=user_id))
        
        # Check if email is already taken by another user
        existing_user = User.query.filter(User.email == email, User.id != user_id).first()
        if existing_user:
            flash("Email already taken by another user!", "error")
            return redirect(url_for("edit_user", user_id=user_id))
        
        try:
            user.name = name
            user.email = email
            user.institution = institution
            db.session.commit()
            
            flash(f"✅ User details updated successfully for {name}", "success")
            return redirect(url_for("manage_created_accounts"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating user: {str(e)}", "error")
            return redirect(url_for("edit_user", user_id=user_id))
    
    # Get institutions for dropdown
    institutions = Institution.query.filter_by(status="active").all()
    
    return render_template(
        "supervisor/edit_user.html",
        user=user,
        institutions=institutions,
        show_sidebar=True
    )


@app.route("/delete_user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    """Supervisor can delete users"""
    if "email" not in session or session.get("user_type") != "0":
        flash("Only supervisors can delete users!", "error")
        return redirect(url_for("signin"))
    
    user = User.query.get_or_404(user_id)
    user_email = user.email
    user_name = user.name
    
    try:
        # Delete related records first (due to foreign key constraints)
        tables_to_clean = [
            ("mentor_profile", "user_id"),
            ("mentee_profile", "user_id"),
            ("supervisor_profile", "user_id"),
            ("mentorship_requests", "mentee_id"),
            ("mentorship_requests", "mentor_id"),
            ("meeting_requests", "requester_id"),
            ("meeting_requests", "requested_to_id"),
            ("mentee_tasks", "mentee_id"),
            ("mentee_tasks", "mentor_id"),
            ("personal_tasks", "mentee_id"),
            ("personal_tasks", "mentor_id"),
            ("task_ratings", "mentee_id"),
            ("task_ratings", "mentor_id"),
        ]
        
        for table, column in tables_to_clean:
            db.session.execute(text(f"DELETE FROM {table} WHERE {column} = {user_id}"))
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        
        flash(f"✅ User {user_name} ({user_email}) has been deleted successfully", "success")
        return redirect(url_for("manage_created_accounts"))
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting user: {str(e)}", "error")
        return redirect(url_for("manage_created_accounts"))


# ✅ UPDATE THIS ROUTE (remove profile references)

@app.route("/institutiondashboard")
@profile_required
def institutiondashboard():
    if "email" not in session or session.get("user_type") != "3":
        return redirect(url_for("signin"))

    user = User.query.filter_by(email=session["email"]).first()
    profile_complete = check_profile_complete(user.id, "3")

    # Get institution details by ID (primary) or fall back to name (legacy)
    institution = None
    if user.institution_id:
        institution = Institution.query.filter_by(id=user.institution_id).first()
    if not institution:
        institution = Institution.query.filter_by(name=user.institution).first()
    
    # Get mentors and mentees who selected this institution
    # Match by either institution_id (new) or institution name (legacy)
    institution_name = institution.name if institution else user.institution
    
    institution_mentors = User.query.filter(
        (User.user_type == "1") & (
            (User.institution_id == user.institution_id) |
            (User.institution == institution_name)
        )
    ).all()
    
    institution_mentees = User.query.filter(
        (User.user_type == "2") & (
            (User.institution_id == user.institution_id) |
            (User.institution == institution_name)
        )
    ).all()

    # Get mentorship requests involving institution members
    institution_mentorship_requests = MentorshipRequest.query\
        .join(User, MentorshipRequest.mentee_id == User.id)\
        .filter(
            (User.institution_id == user.institution_id) |
            (User.institution == institution_name)
        )\
        .all()

    return render_template(
        "institution/institutiondashboard.html",
        show_sidebar=True,
        user=user,
        institution=institution,
        institution_mentors=institution_mentors,
        institution_mentees=institution_mentees,
        mentorship_requests=institution_mentorship_requests,
        profile_complete=profile_complete
    )

# Institution specific routes
@app.route("/institution_mentors")
def institution_mentors():
    if "email" not in session or session.get("user_type") != "3":
        return redirect(url_for("signin"))
    
    user = User.query.filter_by(email=session["email"]).first()
    institution_name = user.institution
    
    # Get mentors who selected this institution (by ID or name)
    institution_mentors = User.query.filter(
        (User.user_type == "1") & (
            (User.institution_id == user.institution_id) |
            (User.institution == institution_name)
        )
    ).all()
    
    return render_template(
        "institution/institution_mentors.html",
        show_sidebar=True,
        mentors=institution_mentors
    )

@app.route("/institution_mentees")
def institution_mentees():
    if "email" not in session or session.get("user_type") != "3":
        return redirect(url_for("signin"))
    
    user = User.query.filter_by(email=session["email"]).first()
    institution_name = user.institution
    
    # Get mentees who selected this institution (by ID or name)
    institution_mentees = User.query.filter(
        (User.user_type == "2") & (
            (User.institution_id == user.institution_id) |
            (User.institution == institution_name)
        )
    ).all()
    
    return render_template(
        "institution/institution_mentees.html",
        show_sidebar=True,
        mentees=institution_mentees
        
    )

@app.route("/institution_mentorships")
def institution_mentorships():
    if "email" not in session or session.get("user_type") != "3":
        return redirect(url_for("signin"))
    
    user = User.query.filter_by(email=session["email"]).first()
    institution_name = user.institution
    
    # Get all mentorships involving institution members (by ID or name)
    institution_mentorships = MentorshipRequest.query\
        .join(User, MentorshipRequest.mentee_id == User.id)\
        .filter(
            (User.institution_id == user.institution_id) |
            (User.institution == institution_name)
        )\
        .all()
    
    return render_template(
        "institution/institution_mentorships.html",
        show_sidebar=True,
        mentorships=institution_mentorships
    )
from sqlalchemy.orm import aliased
from sqlalchemy import and_, or_
from datetime import datetime


@app.route("/institution_all_tasks")
def institution_all_tasks():
    if "email" not in session or session.get("user_type") != "3":
        return redirect(url_for("signin"))

    user = User.query.filter_by(email=session["email"]).first()
    institution_id = user.institution_id
    institution_name = user.institution

    if not institution_id and not institution_name:
        flash("Institution not linked to your account.", "error")
        return redirect(url_for("institutiondashboard"))

    all_institution_tasks = []
    
    # Get all users from the institution
    institution_users = User.query.filter(
        (User.institution == institution_name) | 
        (User.institution_id == institution_id)
    ).all()
    
    institution_user_ids = [user.id for user in institution_users]

    # 1. PERSONAL TASKS (Self-assigned by mentees)
    personal_tasks_self = PersonalTask.query.filter(
        PersonalTask.mentee_id.in_(institution_user_ids),
        PersonalTask.mentor_id == None
    ).all()

    for task in personal_tasks_self:
        mentee = User.query.get(task.mentee_id)
        all_institution_tasks.append({
            "id": f"personal_{task.id}",
            "serial": f"P-{task.id}",
            "title": task.title,
            "description": task.description,
            "due_date": task.due_date,
            "status": task.status or "pending",
            "progress": task.progress or 0,
            "priority": task.priority or "medium",
            "category": task.category or "Personal",
            "mentor_id": None,
            "mentor_name": "Self-assigned",
            "mentee_id": task.mentee_id,
            "mentee_name": mentee.name if mentee else "Unknown",
            "mentee_email": mentee.email if mentee else "",
            "type": "personal",
            "rating": task.rating or 0,
            "isCritical": task.is_critical if hasattr(task, 'is_critical') else False,
            "comments": task.comments if hasattr(task, 'comments') else None
        })

    # 2. PERSONAL TASKS (Assigned by mentors)
    personal_tasks_by_mentors = PersonalTask.query.filter(
        PersonalTask.mentee_id.in_(institution_user_ids),
        PersonalTask.mentor_id != None
    ).all()

    for task in personal_tasks_by_mentors:
        mentee = User.query.get(task.mentee_id)
        mentor = User.query.get(task.mentor_id)
        
        # Check if mentor belongs to same institution
        if mentor and (mentor.institution == institution_name or mentor.institution_id == institution_id):
            all_institution_tasks.append({
                "id": f"personal_{task.id}",
                "serial": f"P-{task.id}",
                "title": task.title,
                "description": task.description,
                "due_date": task.due_date,
                "status": task.status or "pending",
                "progress": task.progress or 0,
                "priority": task.priority or "medium",
                "category": task.category or "Personal",
                "mentor_id": task.mentor_id,
                "mentor_name": mentor.name if mentor else "Unknown",
                "mentor_email": mentor.email if mentor else "",
                "mentee_id": task.mentee_id,
                "mentee_name": mentee.name if mentee else "Unknown",
                "mentee_email": mentee.email if mentee else "",
                "type": "personal",
                "isCritical": task.is_critical if hasattr(task, 'is_critical') else False,
                "comments": task.comments if hasattr(task, 'comments') else None
            })

    # 3. MENTEE TASKS (Master Tasks)
    mentee_tasks = MenteeTask.query.filter(
        MenteeTask.mentee_id.in_(institution_user_ids)
    ).all()

    for task in mentee_tasks:
        mentee = db.session.get(User, task.mentee_id)
        mentor = db.session.get(User, task.mentor_id)
        master_task = db.session.get(MasterTask, task.task_id) if task.task_id else None
        
        if mentor and (mentor.institution == institution_name or mentor.institution_id == institution_id):
            all_institution_tasks.append({
                "id": f"master_{task.id}",
                "serial": f"M-{task.id}",
                "title": master_task.purpose_of_call if master_task else "Master Task",
                "description": master_task.mentee_focus if master_task else "No description",
                "due_date": task.due_date,
                "status": task.status or "pending",
                "progress": task.progress or 0,
                "priority": "high",  # Master tasks are typically high priority
                "category": "Master Task",
                "mentor_id": task.mentor_id,
                "mentor_name": mentor.name if mentor else "Unknown",
                "mentor_email": mentor.email if mentor else "",
                "mentee_id": task.mentee_id,
                "mentee_name": mentee.name if mentee else "Unknown",
                "mentee_email": mentee.email if mentee else "",
                "type": "master",
                "isCritical": True,  # Master tasks are always critical
                "comments": task.comments if hasattr(task, 'comments') else None
            })

    # Sort by due date (most urgent first)
    all_institution_tasks.sort(key=lambda x: x['due_date'] if x['due_date'] else datetime.max)

    # Get mentors and mentees for filters
    institution_mentors = User.query.filter(
        User.id.in_(institution_user_ids),
        User.user_type == "1"  # Mentor type
    ).all()
    
    institution_mentees = User.query.filter(
        User.id.in_(institution_user_ids),
        User.user_type == "2"  # Mentee type
    ).all()

    return render_template(
        "institution/institution_all_tasks.html",
        show_sidebar=True,
        tasks=all_institution_tasks,
        mentors=[{"id": m.id, "name": m.name} for m in institution_mentors],
        mentees=[{"id": m.id, "name": m.name} for m in institution_mentees],
        now=datetime.now(),
        profile_complete=True
    )

@app.route("/get_institution_tasks_data")
def get_institution_tasks_data():
    if "email" not in session or session.get("user_type") != "3":
        return jsonify({"success": False, "message": "Unauthorized"})

    user = User.query.filter_by(email=session["email"]).first()
    institution_id = user.institution_id
    institution_name = user.institution

    # Get all users from the institution
    institution_users = User.query.filter(
        (User.institution == institution_name) | 
        (User.institution_id == institution_id)
    ).all()
    
    institution_user_ids = [user.id for user in institution_users]
    
    tasks_data = []
    
    # Get Personal Tasks
    personal_tasks = PersonalTask.query.filter(
        PersonalTask.mentee_id.in_(institution_user_ids)
    ).all()
    
    for task in personal_tasks:
        mentee = User.query.get(task.mentee_id)
        mentor = User.query.get(task.mentor_id) if task.mentor_id else None
        
        tasks_data.append({
            "id": f"personal_{task.id}",
            "serial": f"P-{task.id}",
            "title": task.title,
            "description": task.description,
            "dueDate": task.due_date.isoformat() if task.due_date else None,
            "status": task.status or "pending",
            "progress": task.progress or 0,
            "priority": task.priority or "medium",
            "category": task.category or "Personal",
            "mentorId": task.mentor_id,
            "mentorName": mentor.name if mentor else "Self-assigned",
            "menteeId": task.mentee_id,
            "menteeName": mentee.name if mentee else "Unknown",
            "type": "personal",
            "isCritical": task.is_critical if hasattr(task, 'is_critical') else False
        })
    
    # Get Mentee Tasks (Master Tasks)
    mentee_tasks = MenteeTask.query.filter(
        MenteeTask.mentee_id.in_(institution_user_ids)
    ).all()
    
    for task in mentee_tasks:
        mentee = db.session.get(User, task.mentee_id)
        mentor = db.session.get(User, task.mentor_id)
        master_task = db.session.get(MasterTask, task.task_id) if task.task_id else None
        
        tasks_data.append({
            "id": f"master_{task.id}",
            "serial": f"M-{task.id}",
            "title": master_task.purpose_of_call if master_task else "Master Task",
            "description": master_task.mentee_focus if master_task else "No description",
            "dueDate": task.due_date.isoformat() if task.due_date else None,
            "status": task.status or "pending",
            "progress": task.progress or 0,
            "priority": "high",
            "category": "Master Task",
            "mentorId": task.mentor_id,
            "mentorName": mentor.name if mentor else "Unknown",
            "menteeId": task.mentee_id,
            "menteeName": mentee.name if mentee else "Unknown",
            "type": "master",
            "isCritical": True
        })
    
    # Get institution mentors and mentees for filters
    institution_mentors = User.query.filter(
        User.id.in_(institution_user_ids),
        User.user_type == "1"
    ).all()
    
    institution_mentees = User.query.filter(
        User.id.in_(institution_user_ids),
        User.user_type == "2"
    ).all()

    return jsonify({
        "success": True,
        "tasks": tasks_data,
        "mentors": [{"id": m.id, "name": m.name} for m in institution_mentors],
        "mentees": [{"id": m.id, "name": m.name} for m in institution_mentees],
        "institutionName": institution_name
    })



@app.route("/institution_profile")
def institutionprofile():
    if "email" not in session or session.get("user_type") != "3":
        return redirect(url_for("signin"))

    user = User.query.filter_by(email=session["email"]).first()
    
    # Get institution by user_id (primary - linked as admin) or by institution_id
    institution_details = None
    if user.id:
        institution_details = Institution.query.filter_by(user_id=user.id).first()
    if not institution_details and user.institution_id:
        institution_details = Institution.query.filter_by(id=user.institution_id).first()
    if not institution_details:
        institution_details = Institution.query.filter_by(name=user.institution).first()
    
    # If institution not found, create default data
    if not institution_details:
        print(f"Institution '{user.institution}' not found, creating default data")
        # Create default institution object
        from datetime import datetime
        institution_details = type('obj', (object,), {
            'name': user.institution,
            'email_domain': user.email.split('@')[1] if '@' in user.email else 'example.com',
            'contact_person': user.name,
            'contact_email': user.email,
            'contact_phone': 'Not provided',
            'address': 'Not provided',
            'city': 'Not provided',
            'state': 'Not provided',
            'country': 'Not provided',
            'website': 'Not provided',
            'status': 'active',
            'created_at': datetime.utcnow(),
            'id': 0
        })()
    
    # Calculate statistics using institution_id
    total_students = User.query.filter_by(
        user_type="2", 
        institution_id=user.institution_id
    ).count()
    
    total_mentors = User.query.filter_by(
        user_type="1", 
        institution_id=user.institution_id
    ).count()
    
    # Count active mentorships
    active_mentorships = MentorshipRequest.query\
        .join(User, MentorshipRequest.mentee_id == User.id)\
        .filter(
            User.institution_id == user.institution_id,
            MentorshipRequest.final_status == "approved"
        ).count()

    completed_mentorships = 0  # Placeholder

    return render_template(
        "institution/institutionprofile.html",
        show_sidebar=False,
        full_name=user.name,
        email=user.email,
        institution=user.institution,
        total_students=total_students,
        total_mentors=total_mentors,
        active_mentorships=active_mentorships,
        completed_mentorships=completed_mentorships,
        institution_details=institution_details
    )


@app.route("/editinstitutionprofile", methods=["GET", "POST"])
def editinstitutionprofile():
    if "email" not in session or session.get("user_type") != "3":
        return redirect(url_for("signin"))

    user = User.query.filter_by(email=session["email"]).first()
    
    # Get institution by user_id (primary - linked as admin) or by institution_id
    institution_details = None
    if user.id:
        institution_details = Institution.query.filter_by(user_id=user.id).first()
    if not institution_details and user.institution_id:
        institution_details = Institution.query.filter_by(id=user.institution_id).first()
    if not institution_details:
        institution_details = Institution.query.filter_by(name=user.institution).first()

    if request.method == "POST":
        try:
            # Validate all mandatory fields
            mandatory_fields = {
                "name": request.form.get("name"),
                "contact_person": request.form.get("contact_person"),
                "contact_email": request.form.get("contact_email"),
                "contact_phone": request.form.get("contact_phone"),
                "address": request.form.get("address"),
                "city": request.form.get("city"),
                "state": request.form.get("state"),
                "country": request.form.get("country"),
                "website": request.form.get("website"),
            }
            
            # Check for empty fields
            missing_fields = []
            for field_name, field_value in mandatory_fields.items():
                if not field_value:
                    missing_fields.append(field_name.replace("_", " ").title())
            
            if missing_fields:
                flash(f"Please fill all mandatory fields: {', '.join(missing_fields)}", "error")
                return redirect(url_for("editinstitutionprofile"))
            
            # If institution doesn't exist, create it with user_id link
            if not institution_details:
                institution_details = Institution(
                    user_id=user.id,  # Link to admin user
                    name=request.form.get("name", user.institution)
                )
                db.session.add(institution_details)
                db.session.flush()
            
            # Update institution details from form
            institution_details.name = request.form.get("name", user.institution)
            institution_details.email_domain = request.form.get("email_domain", "")
            institution_details.contact_person = request.form.get("contact_person", "")
            institution_details.contact_email = request.form.get("contact_email", "")
            institution_details.contact_phone = request.form.get("contact_phone", "")
            institution_details.address = request.form.get("address", "")
            institution_details.city = request.form.get("city", "")
            institution_details.state = request.form.get("state", "")
            institution_details.country = request.form.get("country", "")
            institution_details.website = request.form.get("website", "")
            
            # Sync institution name to user's institution field
            user.institution = request.form.get("name", user.institution)
            
            # Safely set institution_type
            try:
                institution_type = request.form.get("institution_type", "other")
                if hasattr(institution_details, 'institution_type'):
                    institution_details.institution_type = institution_type
            except Exception as e:
                print(f"Warning: Could not set institution_type: {e}")
            
            # Link both ways: user.institution_id and institution.user_id
            user.institution_id = institution_details.id
            if not institution_details.user_id:
                institution_details.user_id = user.id
            
            # Handle profile picture upload
            if 'profile_picture' in request.files:
                file = request.files['profile_picture']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(f"institution_{institution_details.id}_{file.filename}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    institution_details.profile_picture = filename
            
            # Update user details
            if hasattr(user, 'designation'):
                user.designation = request.form.get("designation", "")
            if hasattr(user, 'department'):
                user.department = request.form.get("department", "")
            if hasattr(user, 'phone'):
                user.phone = request.form.get("official_phone", "")
            
            db.session.commit()
            flash("Institution profile updated successfully!", "success")
            return redirect(url_for("institutionprofile"))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating institution profile: {str(e)}")
            flash(f"Error updating profile: {str(e)}", "error")
            return redirect(url_for("editinstitutionprofile"))

    # GET request - prepare data for the form
    institution_type = 'other'
    if institution_details and hasattr(institution_details, 'institution_type'):
        institution_type = institution_details.institution_type or 'other'

    return render_template(
        "institution/editinstitutionprofile.html",
        show_sidebar=False,
        user=user,
        full_name=user.name,
        email=user.email,
        institution=user.institution,
        institution_details=institution_details
    )

#-------- find function------------
@app.route("/find_mentor", methods=["GET"])
def find_mentor():
    query = MentorProfile.query

    source_page = request.args.get("from", "mentor")


    source_page = request.args.get("from", "mentees")
    profession = request.args.get("profession")
    location = request.args.get("location")
    education = request.args.get("education")
    experience = request.args.get("experience")

    # --- Apply filters ---
    if profession:
        query = query.filter_by(profession=profession)
    if location:
        query = query.filter_by(location=location)
    if education:
        query = query.filter_by(education=education)
    if experience:
        if experience == "0-2":
            query = query.filter(cast(MentorProfile.years_of_experience, Integer).between(0, 2))
        elif experience == "3-5":
            query = query.filter(cast(MentorProfile.years_of_experience, Integer).between(3, 5))
        elif experience == "6-10":
            query = query.filter(cast(MentorProfile.years_of_experience, Integer).between(6, 10))
        elif experience == "10+":
            query = query.filter(cast(MentorProfile.years_of_experience, Integer) >= 10)

    mentors = query.all()
    
    # Get filter options directly instead of calling the function
    options = {
        "professions": sorted({row.profession for row in MentorProfile.query.with_entities(MentorProfile.profession).distinct() if row.profession}),
        "locations": sorted({row.location for row in MentorProfile.query.with_entities(MentorProfile.location).distinct() if row.location}),
        "educations": sorted({row.education for row in MentorProfile.query.with_entities(MentorProfile.education).distinct() if row.education}),
        "experiences": sorted({row.years_of_experience for row in MentorProfile.query.with_entities(MentorProfile.years_of_experience).distinct() if row.years_of_experience}),
    }

        # Dynamic render/redirect based on source
    if source_page == "supervisor_find_mentor":
        return render_template(
        "supervisor/supervisor_find_mentor.html",
        all_mentors=mentors,
        professions=options["professions"],
        locations=options["locations"],
        educations=options["educations"],
        experiences=options["experiences"],
        show_sidebar=True
        )
    else:  # default mentor

        return render_template(
        "mentee/mentee_find_mentors.html",
        all_mentors=mentors,
        professions=options["professions"],
        locations=options["locations"],
        educations=options["educations"],
        experiences=options["experiences"],
        active_section="findmentor",
        show_sidebar=True
    )

@app.route("/find_mentees", methods=["GET"])
def find_mentees():
    if "email" not in session or session.get("user_type") != "1": 
        return redirect(url_for("signin"))

    # Base query
    query = MenteeProfile.query.join(User, MenteeProfile.user_id == User.id)

    source_page = request.args.get("from", "mentor")

    # Filters
    search_query = request.args.get("search", "").lower()
    stream_filter = request.args.get("stream", "")
    school_filter = request.args.get("school", "")
    goal_filter = request.args.get("goal", "")

    if search_query:
        query = query.filter(
            or_(
                User.name.ilike(f"%{search_query}%"),
                MenteeProfile.stream.ilike(f"%{search_query}%"),
                MenteeProfile.school_college_name.ilike(f"%{search_query}%")
            )
        )

    if stream_filter:
        query = query.filter(MenteeProfile.stream == stream_filter)
    if school_filter:
        query = query.filter(MenteeProfile.school_college_name == school_filter)
    if goal_filter:
        query = query.filter(MenteeProfile.goal == goal_filter)

    filtered_mentees = query.all()
    

    # Get filter options directly
    streams = sorted({m.stream for m in MenteeProfile.query.with_entities(MenteeProfile.stream).distinct() if m.stream})
    schools = sorted({m.school_college_name for m in MenteeProfile.query.with_entities(MenteeProfile.school_college_name).distinct() if m.school_college_name})
    goals = sorted({m.goal for m in MenteeProfile.query.with_entities(MenteeProfile.goal).distinct() if m.goal})

    
    # Dynamic render/redirect based on source
    if source_page == "supervisor":
        return render_template(
            "supervisor/supervisor_find_mentee.html",
            all_mentees=filtered_mentees,
            streams=streams,
            schools=schools,
            goals=goals,
            active_section="mentees",
            show_sidebar=True
        )
    else:  # default mentor
        return render_template(
            "mentor/mentor_find_mentees.html",
            all_mentees=filtered_mentees,
            streams=streams,
            schools=schools,
            goals=goals,
            active_section="findmentees",
            show_sidebar=True
        )

# mentee dashboard to my mentors
@app.route("/my_mentors")
def my_mentors():
    if "email" not in session or session.get("user_type") != "2":
        return redirect(url_for("signin"))

    # Fetch current mentee
    mentee = User.query.filter_by(email=session["email"]).first()
    profile_complete = check_profile_complete(mentee.id, "2")

    if not mentee:
        flash("Mentee profile not found.", "error")
        return redirect(url_for("signin"))

    # A fully approved request means: Mentor accepted AND Supervisor approved AND system final approval is done.
    accepted_requests = MentorshipRequest.query.filter_by(
        mentee_id=mentee.id,
        mentor_status="accepted",
        supervisor_status="approved",
        final_status="approved"
    ).all()

    my_mentors = []
    for req in accepted_requests:
        # req.mentor is the Mentor's User object.
        # req.mentor.mentor_profile is the MentorProfile object attached to that User.
        if req.mentor and req.mentor.mentor_profile:
             my_mentors.append(req.mentor.mentor_profile)

    return render_template(
        "mentee/mentee_my_mentors.html",
        my_mentors=my_mentors,
        show_sidebar=True,
        profile_complete=profile_complete
    )

@app.route("/my_mentees")
def my_mentees():
    if "email" not in session or session.get("user_type") != "1":
        return redirect(url_for("signin"))

    mentor = User.query.filter_by(email=session["email"]).first()
    profile_complete = check_profile_complete(mentor.id, "1")
    
    if not mentor:
        flash("Mentor profile not found.", "error")
        return redirect(url_for("signin"))

    accepted_requests = MentorshipRequest.query.filter_by(
        mentor_id=mentor.id,
        mentor_status="accepted",
        supervisor_status="approved",
        final_status="approved"
    ).all()

    my_mentees_data = []
    for req in accepted_requests:
        if req.mentee:
            mentee_profile = MenteeProfile.query.filter_by(user_id=req.mentee.id).first()
            if mentee_profile:
                # Use the check_profile_complete function instead of accessing non-existent attribute
                mentee_profile_complete = check_profile_complete(req.mentee.id, "2")
                
                my_mentees_data.append({
                    "user": {
                        "name": req.mentee.name,
                        "email": req.mentee.email
                    },
                    "profile": {
                        "dob": mentee_profile.dob,
                        "school_college_name": mentee_profile.school_college_name,
                        "mobile_number": mentee_profile.mobile_number,
                        "whatsapp_number": mentee_profile.whatsapp_number,
                        "govt_private": mentee_profile.govt_private,
                        "stream": mentee_profile.stream,
                        "class_year": mentee_profile.class_year,
                        "favourite_subject": mentee_profile.favourite_subject,
                        "goal": mentee_profile.goal,
                        "parent_name": mentee_profile.parent_name,
                        "parent_mobile": mentee_profile.parent_mobile,
                        "comments": mentee_profile.comments,
                        "terms_agreement": mentee_profile.terms_agreement,
                        "profile_picture": mentee_profile.profile_picture,
                        "profile_complete": mentee_profile_complete 
                    }
                })

    return render_template(
        "mentor/mentor_my_mentees.html",
        my_mentees=my_mentees_data,
        show_sidebar=True,
        profile_complete=profile_complete
    )

@app.route("/supervisor_find_mentor")
def supervisor_find_mentor():
    if "email" not in session or session.get("user_type") != "0":
        return redirect(url_for("signin"))

    mentor_query = MentorProfile.query
    profession = request.args.get("profession")
    location = request.args.get("location")
    education = request.args.get("education")
    experience = request.args.get("experience")

    if profession:
        mentor_query = mentor_query.filter_by(profession=profession)
    if location:
        mentor_query = mentor_query.filter_by(location=location)
    if education:
        mentor_query = mentor_query.filter_by(education=education)
    if experience:
        if experience == "0-2":
            mentor_query = mentor_query.filter(cast(MentorProfile.years_of_experience, Integer).between(0, 2))
        elif experience == "3-5":
            mentor_query = mentor_query.filter(cast(MentorProfile.years_of_experience, Integer).between(3, 5))
        elif experience == "6-10":
            mentor_query = mentor_query.filter(cast(MentorProfile.years_of_experience, Integer).between(6, 10))
        elif experience == "10+":
            mentor_query = mentor_query.filter(cast(MentorProfile.years_of_experience, Integer) >= 10)

    mentors = mentor_query.all()

    options = {
        "professions": sorted({row[0] for row in MentorProfile.query.with_entities(MentorProfile.profession).distinct() if row[0]}),
        "locations": sorted({row[0] for row in MentorProfile.query.with_entities(MentorProfile.location).distinct() if row[0]}),
        "educations": sorted({row[0] for row in MentorProfile.query.with_entities(MentorProfile.education).distinct() if row[0]}),
        "experiences": sorted({row[0] for row in MentorProfile.query.with_entities(MentorProfile.years_of_experience).distinct() if row[0]}),
    }

    return render_template(
        "supervisor/supervisor_find_mentor.html",
        mentors=mentors,
        professions=options["professions"],
        locations=options["locations"],
        educations=options["educations"],
        experiences=options["experiences"],
        active_section="mentors",
        show_sidebar=True
        
    )

@app.route("/supervisor_find_mentee")
def supervisor_find_mentee():
    if "email" not in session or session.get("user_type") != "0":
        return redirect(url_for("signin"))

    mentee_query = MenteeProfile.query.join(User, MenteeProfile.user_id == User.id)
    search_query = request.args.get("search", "").lower()
    stream_filter = request.args.get("stream", "")
    school_filter = request.args.get("school", "")
    goal_filter = request.args.get("goal", "")

    if search_query:
        mentee_query = mentee_query.filter(
            or_(
                User.name.ilike(f"%{search_query}%"),
                MenteeProfile.stream.ilike(f"%{search_query}%"),
                MenteeProfile.school_college_name.ilike(f"%{search_query}%")
            )
        )
    if stream_filter:
        mentee_query = mentee_query.filter(MenteeProfile.stream == stream_filter)
    if school_filter:
        mentee_query = mentee_query.filter(MenteeProfile.school_college_name == school_filter)
    if goal_filter:
        mentee_query = mentee_query.filter(MenteeProfile.goal == goal_filter)

    all_mentees = mentee_query.all()

    mentee_streams = sorted({row[0] for row in MenteeProfile.query.with_entities(MenteeProfile.stream).distinct() if row[0]})
    mentee_schools = sorted({row[0] for row in MenteeProfile.query.with_entities(MenteeProfile.school_college_name).distinct() if row[0]})
    mentee_goals = sorted({row[0] for row in MenteeProfile.query.with_entities(MenteeProfile.goal).distinct() if row[0]})

    return render_template(
        "supervisor/supervisor_find_mentee.html",
        mentees=all_mentees,
        mentee_streams=mentee_streams,
        mentee_schools=mentee_schools,
        mentee_goals=mentee_goals,
        active_section="mentees",
        show_sidebar=True

    )

# supervisor view requests
@app.route("/requests")
def view_requests():
    if "email" not in session or session.get("user_type") != "0":
        return redirect(url_for("signin"))

    # Fetch mentorship requests that are still pending approval from supervisor
    pending_mentorship_requests = MentorshipRequest.query.filter(
        (MentorshipRequest.supervisor_status == "pending") | 
        (MentorshipRequest.mentor_status == "pending")
    ).all()
    
    mentor_requests = MentorProfile.query.filter_by(status="pending").all()
    mentee_requests = MenteeProfile.query.filter_by(status="pending").all()

    return render_template(
        "supervisor/supervisor_request.html",
        all_requests=pending_mentorship_requests,
        mentor_requests=mentor_requests,
        mentee_requests=mentee_requests,
        active_section="requests",
        show_sidebar=True
    )

@app.route("/mentee_calendar")
def mentee_calendar():
    if "email" not in session or session.get("user_type") != "2":
        return redirect(url_for("signin"))
    
    # Get logged-in mentee
    mentee = User.query.filter_by(email=session["email"]).first()
    
    # Fetch all meetings created by this mentee
    meetings = MeetingRequest.query.filter_by(requester_id=mentee.id).order_by(
        MeetingRequest.meeting_date.asc(),
        MeetingRequest.meeting_time.asc()
    ).all()
    
    # Prepare meeting data for the calendar
    calendar_meetings = []
    for meeting in meetings:
        # Get mentor details
        mentor = User.query.get(meeting.requested_to_id)
        
        # Determine meeting status based on date/time
        meeting_datetime = datetime.combine(meeting.meeting_date, meeting.meeting_time)
        now = datetime.now()
        
        if meeting.status == "cancelled":
            status = "cancelled"
        elif meeting_datetime < now:
            status = "completed"
        else:
            status = "upcoming"
        
        calendar_meetings.append({
            "id": meeting.id,
            "title": meeting.meeting_title,
            "date": meeting_datetime,
            "duration": meeting.meeting_duration,
            "mentor": mentor.name if mentor else "Unknown Mentor",
            "type": "Video Call",  # You can add this field to your MeetingRequest model if needed
            "status": status,
            "description": meeting.meeting_description or "No description provided",
            "meet_link": meeting.meet_link
        })
    
    return render_template(
        "mentee/mentee_calendar.html",
        show_sidebar=True,
        meetings=calendar_meetings  # Pass real meetings to template
    )


@app.route("/mentor_calendar")
def mentor_calendar():
    if "email" not in session or session.get("user_type") != "1":
        return redirect(url_for("signin"))
    
    # Get logged-in mentor
    mentor = User.query.filter_by(email=session["email"]).first()
    
    # Fetch all meetings where this mentor is the requested_to person
    meetings = MeetingRequest.query.filter_by(requested_to_id=mentor.id).order_by(
        MeetingRequest.meeting_date.asc(),
        MeetingRequest.meeting_time.asc()
    ).all()
    
    # Prepare meeting data for the calendar
    calendar_meetings = []
    for meeting in meetings:
        # Get mentee details
        mentee = User.query.get(meeting.requester_id)
        
        # Determine meeting status based on date/time
        meeting_datetime = datetime.combine(meeting.meeting_date, meeting.meeting_time)
        now = datetime.now()
        
        if meeting.status == "cancelled":
            status = "cancelled"
        elif meeting_datetime < now:
            status = "completed"
        else:
            status = "upcoming"
        
        calendar_meetings.append({
            "id": meeting.id,
            "title": meeting.meeting_title,
            "date": meeting_datetime,
            "duration": meeting.meeting_duration,
            "mentee": mentee.name if mentee else "Unknown Mentee",
            "mentee_email": mentee.email if mentee else "",
            "type": "Video Call",
            "status": status,
            "description": meeting.meeting_description or "No description provided",
            "meet_link": meeting.meet_link
        })
    
    return render_template(
        "mentor/mentor_calendar.html",
        show_sidebar=True,
        meetings=calendar_meetings
    )


@app.route("/supervisor_calendar")
def supervisor_calendar():
    if "email" not in session or session.get("user_type") != "0":
        return redirect(url_for("signin"))
    
    # Fetch ALL meetings from the database
    meetings = MeetingRequest.query.order_by(
        MeetingRequest.meeting_date.asc(),
        MeetingRequest.meeting_time.asc()
    ).all()
    
    # Prepare meeting data for the calendar
    calendar_meetings = []
    for meeting in meetings:
        # Get mentee and mentor details
        mentee = User.query.get(meeting.requester_id)
        mentor = User.query.get(meeting.requested_to_id)
        
        # Determine meeting status based on date/time
        meeting_datetime = datetime.combine(meeting.meeting_date, meeting.meeting_time)
        now = datetime.now()
        
        if meeting.status == "cancelled":
            status = "cancelled"
        elif meeting_datetime < now:
            status = "completed"
        else:
            status = "upcoming"
        
        calendar_meetings.append({
            "id": meeting.id,
            "title": meeting.meeting_title,
            "date": meeting_datetime,
            "duration": meeting.meeting_duration,
            "mentee": mentee.name if mentee else "Unknown Mentee",
            "mentee_email": mentee.email if mentee else "",
            "mentor": mentor.name if mentor else "Unknown Mentor",
            "mentor_email": mentor.email if mentor else "",
            "type": "Video Call",
            "status": status,
            "description": meeting.meeting_description or "No description provided",
            "meet_link": meeting.meet_link,
            "created_at": meeting.created_at
        })
    
    return render_template(
        "supervisor/supervisor_calendar.html",
        show_sidebar=True,
        meetings=calendar_meetings
    )




    #          task




# ------------------ TASK MANAGEMENT ROUTES ------------------

@app.route("/mentee_tasks")
def mentee_tasks():
    if "email" not in session or session.get("user_type") != "2":
        return redirect(url_for("signin"))
    
    # Get logged-in mentee
    mentee = User.query.filter_by(email=session["email"]).first()
    
    # ✅ FETCH MENTORS FOR DROPDOWN (only approved mentors)
    approved_mentors = MentorshipRequest.query\
        .filter_by(
            mentee_id=mentee.id,
            mentor_status="accepted", 
            supervisor_status="approved",
            final_status="approved"
        )\
        .join(User, MentorshipRequest.mentor_id == User.id)\
        .all()
    
    mentors_list = [{"id": req.mentor.id, "name": req.mentor.name} for req in approved_mentors]
    
    # Fetch tasks
    assigned_tasks = MenteeTask.query\
        .filter_by(mentee_id=mentee.id)\
        .join(MasterTask, MenteeTask.task_id == MasterTask.id)\
        .order_by(MenteeTask.meeting_number)\
        .all()
    
    personal_tasks = PersonalTask.query\
        .filter_by(mentee_id=mentee.id)\
        .order_by(PersonalTask.created_date.desc())\
        .all()
    
    # Add serial numbers: continue numbering across assigned + personal tasks
    try:
        start_index = 1
        for i, t in enumerate(assigned_tasks, start_index):
            setattr(t, 'serial', i)
        # personal tasks continue numbering after assigned tasks
        start_index = len(assigned_tasks) + 1
        for i, t in enumerate(personal_tasks, start=start_index):
            setattr(t, 'serial', i)
    except Exception:
        # If we can't set attributes (unlikely), ignore and continue
        pass

    # Calculate statistics
    total_tasks = len(assigned_tasks) + len(personal_tasks)
    completed_tasks = len([t for t in assigned_tasks if t.status == 'completed']) + len([t for t in personal_tasks if t.status == 'completed'])
    pending_tasks = len([t for t in assigned_tasks if t.status == 'pending']) + len([t for t in personal_tasks if t.status == 'pending'])
    
    today = datetime.utcnow().date()
    overdue_tasks = len([t for t in assigned_tasks if t.due_date and t.due_date.date() < today and t.status != 'completed']) + \
                   len([t for t in personal_tasks if t.due_date and t.due_date.date() < today and t.status != 'completed'])
    
    return render_template(
        "mentee/mentee_tasks.html",
        show_sidebar=True,
        assigned_tasks=assigned_tasks,
        personal_tasks=personal_tasks,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        overdue_tasks=overdue_tasks,
        today=today,
        mentors_list=mentors_list,  # ✅ PASS MENTORS TO TEMPLATE
        profile_complete=check_profile_complete(mentee.id, "2")
    )


# ------------------ MENTEE RATING VIEW ROUTES ------------------
@app.route('/mentee_get_task_rating/<task_type>/<int:task_id>')
def mentee_get_task_rating(task_type, task_id):
    try:
        if "email" not in session or session.get("user_type") != "2":
            return jsonify({'success': False, 'message': 'Unauthorized'})
        
        # Get current mentee
        mentee = User.query.filter_by(email=session["email"]).first()
        if not mentee:
            return jsonify({'success': False, 'message': 'Mentee not found'})
        
        # Verify the task belongs to this mentee
        if task_type == 'master':
            task = MenteeTask.query.filter_by(id=task_id, mentee_id=mentee.id).first()
        else:
            task = PersonalTask.query.filter_by(id=task_id, mentee_id=mentee.id).first()
            
        if not task:
            return jsonify({'success': False, 'message': 'Task not found or access denied'})
        
        # Get rating for this task
        rating = TaskRating.query.filter_by(
            task_id=task_id,
            task_type=task_type
        ).first()
        
        if rating:
            # Get mentor details
            mentor = User.query.get(rating.mentor_id)
            
            return jsonify({
                'success': True,
                'rating': {
                    'rating': rating.rating,
                    'feedback': rating.feedback,
                    'strengths': rating.strengths,
                    'improvements': rating.improvements,
                    'rated_at': rating.rated_at.isoformat(),
                    'mentor_name': mentor.name if mentor else 'Unknown Mentor'
                }
            })
        else:
            return jsonify({'success': True, 'rating': None})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})



@app.route("/update_task_status", methods=["POST"])
def update_task_status():
    if "email" not in session or session.get("user_type") != "2":
        return jsonify({"success": False, "message": "Unauthorized"})
    
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        task_type = data.get('task_type')  # 'master' or 'personal'
        status = data.get('status')
        progress = data.get('progress', 0)
        
        # Get current mentee
        mentee = User.query.filter_by(email=session["email"]).first()
        
        # Find the task
        if task_type == 'master':
            # Update master task
            task = MenteeTask.query.filter_by(id=task_id, mentee_id=mentee.id).first()
            if not task:
                return jsonify({"success": False, "message": "Master task not found"})
            
            task.status = status
            if status == 'completed':
                task.completed_date = datetime.utcnow()
                task.progress = 100
            else:
                task.progress = progress
                
        elif task_type == 'personal':
            # Update personal task
            task = PersonalTask.query.filter_by(id=task_id, mentee_id=mentee.id).first()
            if not task:
                return jsonify({"success": False, "message": "Personal task not found"})
            
            task.status = status
            task.progress = progress
            if status == 'completed':
                task.completed_date = datetime.utcnow()
        
        else:
            return jsonify({"success": False, "message": "Invalid task type"})
        
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": f"Task marked as {status}",
            "progress": progress
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})

@app.route("/create_personal_task", methods=["POST"])
def create_personal_task():
    if "email" not in session or session.get("user_type") != "2":
        return jsonify({"success": False, "message": "Unauthorized"})
    
    try:
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        due_date_str = data.get('due_date')
        priority = data.get('priority', 'medium')
        mentor_id = data.get('mentor_id')
        
        # Get current mentee
        mentee = User.query.filter_by(email=session["email"]).first()
        
        # ✅ Validate mentor (if provided)
        selected_mentor = None
        if mentor_id and mentor_id != 'self':
            selected_mentor = User.query.get(int(mentor_id))
            if not selected_mentor or selected_mentor.user_type != "1":
                return jsonify({"success": False, "message": "Invalid mentor selected"})
        
        # Convert due date string to datetime
        due_date = None
        if due_date_str:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        
        # Create personal task
        personal_task = PersonalTask(
            mentee_id=mentee.id,
            mentor_id=selected_mentor.id if selected_mentor else None,  # ✅ SET MENTOR OR NULL
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            status="pending",
            progress=0
        )
        
        
        db.session.add(personal_task)
        db.session.commit()
        
        mentor_name = selected_mentor.name if selected_mentor else "Self"
        
        return jsonify({
            "success": True, 
            "message": f"Personal task created successfully under {mentor_name}",
            "task_id": personal_task.id,
            "task_type": "personal"
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})

@app.route("/get_task_details/<int:task_id>")
def get_task_details(task_id):
    if "email" not in session:
        return jsonify({"success": False, "message": "Unauthorized"})
    
    try:
        task_type = request.args.get('type', 'master')  # Default to master
        
        if task_type == 'master':
            # Get master task with all related data
            task = MenteeTask.query\
                .join(MasterTask, MenteeTask.task_id == MasterTask.id)\
                .filter(MenteeTask.id == task_id)\
                .first()
            
            if not task:
                return jsonify({"success": False, "message": "Master task not found"})
            
            # Verify access rights
            user = User.query.filter_by(email=session["email"]).first()
            user_type = session.get("user_type")
            
            if user_type == "2" and task.mentee_id != user.id:
                return jsonify({"success": False, "message": "Access denied"})
            
            task_data = {
                "id": task.id,
                "type": "master",
                "title": task.master_task.purpose_of_call,
                "description": task.master_task.mentee_focus,
                "due_date": task.due_date.strftime('%Y-%m-%d') if task.due_date else None,
                "status": task.status,
                "progress": task.progress or 0,
                "assigned_by": task.mentor.name if task.mentor else "System",
                "assigned_date": task.assigned_date.strftime('%Y-%m-%d') if task.assigned_date else None,
                "completed_date": task.completed_date.strftime('%Y-%m-%d') if task.completed_date else None,
                "month": task.month,
                "meeting_number": task.meeting_number,
                "mentor_focus": task.master_task.mentor_focus,
                "journey_phase": task.master_task.journey_phase,
                "meeting_plan": task.master_task.meeting_plan_overview
            }
            
        elif task_type == 'personal':
            # Get personal task
            task = PersonalTask.query.filter_by(id=task_id).first()
            
            if not task:
                return jsonify({"success": False, "message": "Personal task not found"})
            
            # Verify access rights
            user = User.query.filter_by(email=session["email"]).first()
            if task.mentee_id != user.id:
                return jsonify({"success": False, "message": "Access denied"})
            
            task_data = {
                "id": task.id,
                "type": "personal",
                "title": task.title,
                "description": task.description,
                "due_date": task.due_date.strftime('%Y-%m-%d') if task.due_date else None,
                "status": task.status,
                "progress": task.progress or 0,
                "priority": task.priority,
                "assigned_by": "Self",
                "created_date": task.created_date.strftime('%Y-%m-%d') if task.created_date else None,
                "completed_date": task.completed_date.strftime('%Y-%m-%d') if task.completed_date else None
            }
        
        else:
            return jsonify({"success": False, "message": "Invalid task type"})
        
        return jsonify({"success": True, "task": task_data})
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})



# ------------------ MENTOR TASK MANAGEMENT ROUTES ------------------
@app.route("/mentor_tasks")
def mentor_tasks():
    if "email" not in session or session.get("user_type") != "1":
        return redirect(url_for("signin"))
    
    # Get logged-in mentor
    mentor = User.query.filter_by(email=session["email"]).first()
    profile_complete = check_profile_complete(mentor.id, "1")
    
    if not mentor:
        flash("Mentor profile not found.", "error")
        return redirect(url_for("signin"))

    # Get mentor's mentees
    my_mentees_data = []
    accepted_requests = MentorshipRequest.query.filter_by(
        mentor_id=mentor.id,
        mentor_status="accepted",
        supervisor_status="approved",
        final_status="approved"
    ).all()

    for req in accepted_requests:
        if req.mentee:
            mentee_profile = MenteeProfile.query.filter_by(user_id=req.mentee.id).first()
            if mentee_profile:
                my_mentees_data.append({
                    "user": req.mentee,
                    "profile": mentee_profile
                })

    # Get personal tasks assigned by this mentor
    personal_tasks = PersonalTask.query.filter_by(mentor_id=mentor.id).all()
    
    # Get master tasks for mentees
    all_mentee_tasks = []
    for mentee_data in my_mentees_data:
        tasks = MenteeTask.query.filter_by(
            mentee_id=mentee_data["user"].id,
            mentor_id=mentor.id
        ).join(MasterTask, MenteeTask.task_id == MasterTask.id)\
         .order_by(MenteeTask.meeting_number)\
         .all()
        all_mentee_tasks.extend(tasks)

    # Assign serial numbers across mentor's personal tasks and mentee master tasks
    try:
        idx = 1
        for t in personal_tasks:
            setattr(t, 'serial', idx)
            idx += 1
        for t in all_mentee_tasks:
            setattr(t, 'serial', idx)
            idx += 1
    except Exception:
        pass

    # Calculate statistics
    all_tasks = list(personal_tasks) + list(all_mentee_tasks)
    total_tasks = len(all_tasks)
    completed_tasks = len([t for t in all_tasks if t.status == 'completed'])
    pending_tasks = len([t for t in all_tasks if t.status in ['pending', 'in-progress']])
    
    today = datetime.utcnow().date()
    overdue_tasks = len([t for t in all_tasks if t.due_date and t.due_date.date() < today and t.status != 'completed'])

    return render_template(
        "mentor/mentor_tasks.html",
        show_sidebar=True,
        my_mentees=my_mentees_data,
        personal_tasks=personal_tasks,
        mentee_tasks=all_mentee_tasks,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        overdue_tasks=overdue_tasks,
        today=today,
        profile_complete=profile_complete
    )

@app.route("/mentor_create_task", methods=["POST"])
def mentor_create_task():
    if "email" not in session or session.get("user_type") != "1":
        return jsonify({"success": False, "message": "Unauthorized"})
    
    try:
        data = request.get_json()
        mentee_id = data.get('mentee_id')
        title = data.get('title')
        description = data.get('description')
        due_date_str = data.get('due_date')
        priority = data.get('priority', 'medium')
        category = data.get('category', 'Other')
        
        # Get current mentor
        mentor = User.query.filter_by(email=session["email"]).first()
        
        # Validate mentee belongs to this mentor
        mentorship = MentorshipRequest.query.filter_by(
            mentor_id=mentor.id,
            mentee_id=mentee_id,
            mentor_status="accepted",
            supervisor_status="approved",
            final_status="approved"
        ).first()
        
        if not mentorship:
            return jsonify({"success": False, "message": "Mentee not found or not assigned to you"})
        
        # Convert due date string to datetime
        due_date = None
        if due_date_str:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        
        # Create personal task assigned by mentor
        personal_task = PersonalTask(
            mentee_id=mentee_id,
            mentor_id=mentor.id,
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            status="pending",
            progress=0
        )
        
        db.session.add(personal_task)
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": "Task assigned successfully to mentee",
            "task_id": personal_task.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})

@app.route("/get_mentor_task_details/<int:task_id>")
def get_mentor_task_details(task_id):
    if "email" not in session or session.get("user_type") != "1":
        return jsonify({"success": False, "message": "Unauthorized"})
    
    try:
        task_type = request.args.get('type', 'personal')
        
        if task_type == 'master':
            # Get master task with all related data
            task = MenteeTask.query\
                .join(MasterTask, MenteeTask.task_id == MasterTask.id)\
                .join(User, MenteeTask.mentee_id == User.id)\
                .filter(MenteeTask.id == task_id)\
                .first()
            
            if not task:
                return jsonify({"success": False, "message": "Master task not found"})
            
            # Verify the mentor has access to this task
            mentor = User.query.filter_by(email=session["email"]).first()
            if task.mentor_id != mentor.id:
                return jsonify({"success": False, "message": "Access denied"})
            
            task_data = {
                "id": task.id,
                "type": "master",
                "title": task.master_task.purpose_of_call,
                "purpose_of_call": task.master_task.journey_phase,
                "description": task.master_task.mentee_focus,
                "due_date": task.due_date.strftime('%Y-%m-%d') if task.due_date else None,
                "status": task.status,
                "progress": task.progress or 0,
                "mentee_name": task.mentee.name if task.mentee else "Unknown",
                "mentee_email": task.mentee.email if task.mentee else "",
                "assigned_by": "System",
                "assigned_date": task.assigned_date.strftime('%Y-%m-%d') if task.assigned_date else None,
                "completed_date": task.completed_date.strftime('%Y-%m-%d') if task.completed_date else None,
                "month": task.month,
                "meeting_number": task.meeting_number,
                "mentor_focus": task.master_task.mentor_focus,
                "journey_phase": task.master_task.journey_phase,
                "meeting_plan": task.master_task.meeting_plan_overview
            }
            
        elif task_type == 'personal':
            # Get personal task
            task = PersonalTask.query\
                .join(User, PersonalTask.mentee_id == User.id)\
                .filter(PersonalTask.id == task_id)\
                .first()
            
            if not task:
                return jsonify({"success": False, "message": "Personal task not found"})
            
            # Verify the mentor has access to this task
            mentor = User.query.filter_by(email=session["email"]).first()
            if task.mentor_id != mentor.id:
                return jsonify({"success": False, "message": "Access denied"})
            
            task_data = {
                "id": task.id,
                "type": "personal",
                "title": task.title,
                "description": task.description,
                "due_date": task.due_date.strftime('%Y-%m-%d') if task.due_date else None,
                "status": task.status,
                "progress": task.progress or 0,
                "priority": task.priority,
                "mentee_name": task.mentee.name if task.mentee else "Unknown",
                "mentee_email": task.mentee.email if task.mentee else "",
                "assigned_by": "You",
                "created_date": task.created_date.strftime('%Y-%m-%d') if task.created_date else None,
                "completed_date": task.completed_date.strftime('%Y-%m-%d') if task.completed_date else None
            }
        
        else:
            return jsonify({"success": False, "message": "Invalid task type"})
        
        return jsonify({"success": True, "task": task_data})
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})



# Task Rating Routes - FIXED VERSION
@app.route('/rate_task/<task_type>/<int:task_id>', methods=['POST'])
def rate_task(task_type, task_id):
    if "email" not in session or session.get("user_type") != "1":
        return jsonify({'success': False, 'message': 'Only mentors can rate tasks'})
    
    try:
        # Get current mentor from session
        mentor = User.query.filter_by(email=session["email"]).first()
        if not mentor:
            return jsonify({'success': False, 'message': 'Mentor not found'})
        
        data = request.get_json()
        
        # Check if task exists and belongs to mentor's mentee
        if task_type == 'master':
            task = MenteeTask.query.filter_by(id=task_id, mentor_id=mentor.id).first()
        else:
            task = PersonalTask.query.filter_by(id=task_id, mentor_id=mentor.id).first()
            
        if not task:
            return jsonify({'success': False, 'message': 'Task not found or access denied'})
        
        # Check if already rated
        existing_rating = TaskRating.query.filter_by(
            task_id=task_id, 
            task_type=task_type,
            mentor_id=mentor.id
        ).first()
        
        if existing_rating:
            # Update existing rating
            existing_rating.rating = data['rating']
            existing_rating.feedback = data.get('feedback', '')
            existing_rating.strengths = data.get('strengths', '')
            existing_rating.improvements = data.get('improvements', '')
            existing_rating.rated_at = datetime.utcnow()
        else:
            # Create new rating
            new_rating = TaskRating(
                task_id=task_id,
                task_type=task_type,
                mentee_id=task.mentee_id,
                mentor_id=mentor.id,
                rating=data['rating'],
                feedback=data.get('feedback', ''),
                strengths=data.get('strengths', ''),
                improvements=data.get('improvements', '')
            )
            db.session.add(new_rating)
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Task rated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/get_task_rating/<task_type>/<int:task_id>')
def get_task_rating(task_type, task_id):
    try:
        if "email" not in session or session.get("user_type") != "1":
            return jsonify({'success': False, 'message': 'Unauthorized'})
        
        mentor = User.query.filter_by(email=session["email"]).first()
        if not mentor:
            return jsonify({'success': False, 'message': 'Mentor not found'})
        
        rating = TaskRating.query.filter_by(
            task_id=task_id,
            task_type=task_type,
            mentor_id=mentor.id
        ).first()
        
        if rating:
            return jsonify({
                'success': True,
                'rating': {
                    'rating': rating.rating,
                    'feedback': rating.feedback,
                    'strengths': rating.strengths,
                    'improvements': rating.improvements,
                    'rated_at': rating.rated_at.isoformat()
                }
            })
        else:
            return jsonify({'success': True, 'rating': None})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route("/get_supervisor_tasks_data")
def get_supervisor_tasks_data():
    if "email" not in session or session.get("user_type") != "0":
        return jsonify({"success": False, "message": "Unauthorized"})
    
    try:
        # Get all tasks with ratings
        personal_tasks = PersonalTask.query.all()
        mentee_tasks = MenteeTask.query.all()

        tasks = []
        
        # Process personal tasks
        for task in personal_tasks:
            mentee = User.query.get(task.mentee_id)
            mentor = User.query.get(task.mentor_id) if task.mentor_id else None
            
            # Get rating for this task
            rating = TaskRating.query.filter_by(
                task_id=task.id,
                task_type='personal'
            ).first()
            
            due_date = task.due_date or datetime.utcnow() + timedelta(days=30)
            is_critical = task.priority == 'high' and task.status != 'completed'
            
            tasks.append({
                'id': f"personal_{task.id}",
                'title': task.title,
                'description': task.description or 'No description provided',
                'dueDate': due_date.isoformat(),
                'priority': task.priority,
                'status': task.status,
                'progress': task.progress or 0,
                'mentorName': mentor.name if mentor else 'Self',
                'menteeName': mentee.name if mentee else 'Unknown',
                'category': 'Personal Task',
                'rating': rating.rating if rating else None,
                'isCritical': is_critical,
                'type': 'personal',
                'journey_phase': 'Custom Task',  # Personal tasks don't have journey phase
                'month': 'N/A',
                'meeting_number': 'N/A'
            })
        
        # Process mentee tasks
        for task in mentee_tasks:
            master_task = db.session.get(MasterTask, task.task_id)
            mentee = db.session.get(User, task.mentee_id)
            mentor = db.session.get(User, task.mentor_id)
            
            if master_task and mentee and mentor:
                # Get rating for this task
                rating = TaskRating.query.filter_by(
                    task_id=task.id,
                    task_type='master'
                ).first()
                
                due_date = task.due_date or datetime.utcnow() + timedelta(days=30)
                is_overdue = due_date < datetime.utcnow() and task.status != 'completed'
                
                tasks.append({
                    'id': f"master_{task.id}",
                    'title': f"{master_task.purpose_of_call} - {master_task.month}",
                    'description': master_task.mentee_focus or 'No description provided',
                    'dueDate': due_date.isoformat(),
                    'priority': 'medium',
                    'status': task.status,
                    'progress': task.progress or 0,
                    'mentorName': mentor.name,
                    'menteeName': mentee.name,
                    'category': 'Mentorship Program',
                    'rating': rating.rating if rating else None,
                    'isCritical': is_overdue,
                    'type': 'master',
                    'journey_phase': master_task.journey_phase,  # Add journey phase
                    'month': master_task.month,
                    'meeting_number': task.meeting_number
                })

        # Get unique mentors and mentees
        # Add serial numbers to tasks for frontend display
        for i, t in enumerate(tasks, start=1):
            try:
                t['serial'] = i
            except Exception:
                pass

        mentors = list(set([task['mentorName'] for task in tasks]))
        mentees = list(set([task['menteeName'] for task in tasks]))

        return jsonify({
            "success": True,
            "tasks": tasks,
            "mentors": mentors,
            "mentees": mentees
        })
        
    except Exception as e:
        print(f"Error in get_supervisor_tasks_data: {str(e)}")
        return jsonify({
            "success": False,
            "message": str(e),
            "tasks": [],
            "mentors": [],
            "mentees": []
        })



#------------------------------------------------------------------------------------------------------------------- 
#------------------------------------------------------------------------------------------------------------------- 
#------------------------------------------------------------------------------------------------------------------- 


# ------------------ SUPERVISOR TASK MANAGEMENT ROUTES ------------------
@app.route("/supervisor_tasks")
def supervisor_tasks():
    if "email" not in session or session.get("user_type") != "0":
        return redirect(url_for("signin"))
    
    try:
        print("🔍 Starting supervisor_tasks data fetch...")
        
        # Get all tasks with proper joins
        personal_tasks = db.session.query(PersonalTask, User).join(
            User, PersonalTask.mentee_id == User.id
        ).all()
        
        print(f"📊 Found {len(personal_tasks)} personal tasks")
        
        mentee_tasks = db.session.query(MenteeTask, MasterTask, User).join(
            MasterTask, MenteeTask.task_id == MasterTask.id
        ).join(
            User, MenteeTask.mentee_id == User.id
        ).all()
        
        print(f"📊 Found {len(mentee_tasks)} mentee tasks")
        
        # Prepare tasks data
        all_tasks = []
        
        # Process personal tasks
        for task, user in personal_tasks:
            mentor = User.query.get(task.mentor_id) if task.mentor_id else None
            all_tasks.append({
                'id': f"personal_{task.id}",
                'title': task.title,
                'description': task.description,
                'due_date': task.due_date,
                'priority': task.priority,
                'status': task.status,
                'progress': task.progress,
                'mentee_name': user.name,
                'mentor_name': mentor.name if mentor else 'Self',
                'type': 'personal'
            })
        
        # Process mentee tasks  
        for task, master, user in mentee_tasks:
            mentor = User.query.get(task.mentor_id)
            all_tasks.append({
                'id': f"master_{task.id}",
                'title': f"{master.purpose_of_call} - {master.month}",
                'description': master.mentee_focus,
                'due_date': task.due_date,
                'priority': 'medium',
                'status': task.status,
                'progress': task.progress,
                'mentee_name': user.name,
                'mentor_name': mentor.name if mentor else 'Unknown',
                'type': 'master'
            })
        
        print(f"🎯 Total tasks prepared: {len(all_tasks)}")
        # Add serial numbers to all_tasks (dicts) for display
        for i, task in enumerate(all_tasks, start=1):
            try:
                task['serial'] = i
            except Exception:
                pass

        return render_template(
            "supervisor/supervisor_tasks.html",
            show_sidebar=True,
            profile_complete=True,
            all_tasks=all_tasks
        )
        
    except Exception as e:
        print(f"❌ Error in supervisor_tasks: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template(
            "supervisor/supervisor_tasks.html",
            show_sidebar=True,
            profile_complete=True,
            all_tasks=[]
        )
        

# ------------------ SUPERVISOR RATING VIEW ROUTES ------------------
@app.route('/supervisor_get_task_rating/<task_type>/<int:task_id>')
def supervisor_get_task_rating(task_type, task_id):
    try:
        if "email" not in session or session.get("user_type") != "0":
            return jsonify({'success': False, 'message': 'Unauthorized'})
        
        # Supervisor can see rating for any task
        rating = TaskRating.query.filter_by(
            task_id=task_id,
            task_type=task_type
        ).first()
        
        if rating:
            return jsonify({
                'success': True,
                'rating': {
                    'rating': rating.rating,
                    'feedback': rating.feedback,
                    'strengths': rating.strengths,
                    'improvements': rating.improvements,
                    'rated_at': rating.rated_at.isoformat()
                }
            })
        else:
            return jsonify({'success': True, 'rating': None})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route("/institution_calendar")
def institution_calendar():
    if "email" not in session or session.get("user_type") != "3":
        return redirect(url_for("signin"))
    
    user = User.query.filter_by(email=session["email"]).first()
    institution_name = user.institution
    institution_id = user.institution_id

    # Fetch all meetings involving mentees or mentors from this institution
    # We need to query MeetingRequest and join with User to filter by institution
    meetings = (
        MeetingRequest.query
        .join(User, or_(MeetingRequest.requester_id == User.id, MeetingRequest.requested_to_id == User.id))
        .filter(
            (User.user_type.in_(["1", "2"])) & # Only mentors and mentees
            (
                (User.institution_id == institution_id) |
                (User.institution == institution_name)
            )
        )
        .order_by(MeetingRequest.meeting_date.asc(), MeetingRequest.meeting_time.asc())
        .all()
    )

    from datetime import datetime, date
    now = datetime.now()

    calendar_meetings = []
    for meeting in meetings:
        mentee = User.query.get(meeting.requester_id)
        mentor = User.query.get(meeting.requested_to_id)
        
        meeting_datetime = datetime.combine(meeting.meeting_date, meeting.meeting_time)
        
        if meeting.status == "cancelled":
            status = "cancelled"
        elif meeting_datetime < now:
            status = "completed"
        else:
            status = "upcoming"
        
        calendar_meetings.append({
            "id": meeting.id,
            "title": meeting.meeting_title,
            "date": meeting_datetime,
            "duration": meeting.meeting_duration,
            "mentee": mentee.name if mentee else "Unknown Mentee",
            "mentee_email": mentee.email if mentee else "",
            "mentor": mentor.name if mentor else "Unknown Mentor",
            "mentor_email": mentor.email if mentor else "",
            "type": "Video Call",
            "status": status,
            "description": meeting.meeting_description or "No description provided",
            "meet_link": meeting.meet_link,
            "created_at": meeting.created_at
        })
    
    return render_template(
        "institution/institution_calendar.html",
        show_sidebar=True,
        meetings=calendar_meetings
    )


# ---------------meeting details----------------
@app.route("/mentee_meeting_details")
def mentee_meeting_details():
    if "email" not in session or session.get("user_type") != "2":
        return redirect(url_for("signin"))

    # Get logged-in mentee
    mentee = User.query.filter_by(email=session["email"]).first()

    # Fetch all meetings created by this mentee
    meetings = MeetingRequest.query.filter_by(requester_id=mentee.id).order_by(
        MeetingRequest.meeting_date.desc(),
        MeetingRequest.meeting_time.desc()
    ).all()

    return render_template(
        "mentee/mentee_meeting_details.html",
        show_sidebar=True,
        meetings=meetings
    )

@app.route("/mentor_meeting_details")
def mentor_meeting_details():
    if "email" not in session or session.get("user_type") != "1":
        return redirect(url_for("signin"))

    # Get logged-in mentee
    mentor = User.query.filter_by(email=session["email"]).first()

    # Fetch all meetings created by this mentee
    meetings = MeetingRequest.query.filter_by(requested_to_id=mentor.id).order_by(
        MeetingRequest.meeting_date.desc(),
        MeetingRequest.meeting_time.desc()
    ).all()

    return render_template(
        "mentor/mentor_meeting_details.html",
        show_sidebar=True,
        meetings=meetings
    )

# ------------------- RESCHEDULE MEETING -------------------
@app.route("/reschedule_meeting/<int:meeting_id>", methods=["POST"])
def reschedule_meeting(meeting_id):
    if "email" not in session or session.get("user_type") != "1":
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    try:
        data = request.get_json()
        new_date = data.get("new_date")
        new_time = data.get("new_time")
        reason = data.get("reason", "").strip()

        if not new_date or not new_time:
            return jsonify({"success": False, "message": "Please provide new date and time"}), 400

        mentor = User.query.filter_by(email=session["email"]).first()
        meeting = MeetingRequest.query.get(meeting_id)

        if not meeting:
            return jsonify({"success": False, "message": "Meeting not found"}), 404

        if meeting.requested_to_id != mentor.id:
            return jsonify({"success": False, "message": "You can only reschedule your own meetings"}), 403

        # Parse new date and time
        new_meeting_date = datetime.strptime(new_date, "%Y-%m-%d").date()
        new_meeting_time = datetime.strptime(new_time, "%H:%M").time()

        # Calculate original meeting datetime
        original_datetime = datetime.combine(meeting.meeting_date, meeting.meeting_time)
        now = datetime.now()

        # Check if rescheduling within 8 hours of original meeting time
        time_until_meeting = original_datetime - now
        hours_until_meeting = time_until_meeting.total_seconds() / 3600

        # If less than 8 hours until meeting, reason is mandatory
        if hours_until_meeting <= 8 and hours_until_meeting > 0:
            if not reason:
                return jsonify({
                    "success": False, 
                    "message": "Reason is required when rescheduling within 8 hours of the meeting",
                    "urgent": True
                }), 400

        # Store original date/time before updating
        if not meeting.original_date:  # Only store first original values
            meeting.original_date = meeting.meeting_date
            meeting.original_time = meeting.meeting_time

        # Update meeting with new date/time
        meeting.meeting_date = new_meeting_date
        meeting.meeting_time = new_meeting_time
        meeting.is_rescheduled = True
        meeting.reschedule_reason = reason if reason else None
        meeting.rescheduled_at = datetime.utcnow()
        meeting.rescheduled_by_id = mentor.id
        meeting.status = "rescheduled"

        # Update Google Calendar event if exists
        if meeting.gcal_event_id:
            try:
                service = get_calendar_service()
                
                # Calculate new start and end times
                new_start_datetime = datetime.combine(new_meeting_date, new_meeting_time)
                new_end_datetime = new_start_datetime + timedelta(minutes=meeting.meeting_duration)
                
                event_update = {
                    "start": {"dateTime": new_start_datetime.isoformat(), "timeZone": "Asia/Kolkata"},
                    "end": {"dateTime": new_end_datetime.isoformat(), "timeZone": "Asia/Kolkata"},
                }
                
                service.events().patch(
                    calendarId="primary",
                    eventId=meeting.gcal_event_id,
                    body=event_update,
                    sendUpdates="all"
                ).execute()
            except Exception as e:
                print(f"Error updating Google Calendar: {str(e)}")
                # Continue even if calendar update fails

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Meeting rescheduled successfully",
            "new_date": new_meeting_date.strftime("%Y-%m-%d"),
            "new_time": new_meeting_time.strftime("%I:%M %p")
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error rescheduling meeting: {str(e)}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

# ---------------- Supervisor - All Meeting Details ----------------
@app.route("/supervisor_meeting_details")
def supervisor_meeting_details():
    if "email" not in session or session.get("user_type") != "0":
        return redirect(url_for("signin"))

    # Fetch all meetings in ascending order (oldest first)
    meetings = (
        MeetingRequest.query
        .order_by(MeetingRequest.meeting_date.asc(), MeetingRequest.meeting_time.asc())
        .all()
    )

    # Get current date for timing calculations
    from datetime import datetime, date
    today = date.today()
    now = datetime.now()

    # Prepare formatted meeting data with mentee & mentor info
    meeting_data = []
    for meeting in meetings:
        mentee = User.query.get(meeting.requester_id)
        mentor = User.query.get(meeting.requested_to_id)

        # Calculate timing category
        meeting_datetime = datetime.combine(meeting.meeting_date, meeting.meeting_time)
        is_upcoming = meeting_datetime > now

        meeting_data.append({
            "id": meeting.id,
            "title": meeting.meeting_title,
            "description": meeting.meeting_description,
            "date": meeting.meeting_date.strftime("%d-%m-%Y"),
            "time": meeting.meeting_time.strftime("%I:%M %p"),
            "duration": meeting.meeting_duration,
            "status": meeting.status,
            "mentee_name": mentee.name if mentee else "Unknown",
            "mentee_email": mentee.email if mentee else "N/A",
            "mentor_name": mentor.name if mentor else "Unknown",
            "mentor_email": mentor.email if mentor else "N/A",
            "created_at": meeting.created_at.strftime("%d-%m-%Y %I:%M %p") if meeting.created_at else "",
            "is_upcoming": is_upcoming,
            "meet_link": meeting.meet_link,
        })

    return render_template(
        "supervisor/supervisor_meeting_details.html",
        show_sidebar=True,
        meetings=meeting_data
    )

# ------------------- HANDLE MENTORSHIP REQUEST ------------------
@app.route("/request_mentorship", methods=["POST"])
def request_mentorship(): 
    if "email" not in session or session.get("user_type") != "2":
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    try:
        data = request.json
        mentor_id = data.get("mentor_id")
        purpose = data.get("purpose")
        mentor_type = data.get("mentor_type")
        term = data.get("term")
        duration_months = data.get("duration_months")
        why_need_mentor = data.get("why_need_mentor")

        # Validate required fields
        if not all([mentor_id, purpose, mentor_type, term, duration_months, why_need_mentor]):
            return jsonify({"success": False, "message": "Missing required fields"}), 400

        # Validate duration_months is a positive integer
        try:
            duration_months = int(duration_months)
            if duration_months <= 0:
                return jsonify({"success": False, "message": "Duration must be a positive number"}), 400
        except (ValueError, TypeError):
            return jsonify({"success": False, "message": "Invalid duration value"}), 400

        # Get mentee (current user)
        mentee = User.query.filter_by(email=session["email"]).first()
        if not mentee:
            return jsonify({"success": False, "message": "User not found"}), 404

        # Verify mentor exists
        mentor = User.query.get(mentor_id)
        if not mentor:
            return jsonify({"success": False, "message": "Mentor not found"}), 404

        # Check if user is trying to request themselves as mentor
        if mentee.id == mentor_id:
            return jsonify({"success": False, "message": "Cannot request mentorship from yourself"}), 400
    
        # Check for existing pending request to same mentor
        existing_request = MentorshipRequest.query.filter_by(
            mentee_id=mentee.id,
            mentor_id=mentor_id,
            
        ).all()
        
        # loop through existing requests to check status
        for req in existing_request:
            if req.mentor_status == "pending" or req.supervisor_status == "pending":
                return jsonify({"success": False, "message": "You already have a pending request with this mentor."}), 400
            if req.mentor_status == "accepted" and req.supervisor_status == "approved" and req.final_status == "approved":
                return jsonify({"success": False, "message": "You are already assigned to this mentor."}), 400


        # Create new mentorship request
        new_request = MentorshipRequest(
            mentee_id=mentee.id,
            mentor_id=mentor_id,
            purpose=purpose,
            mentor_type=mentor_type,
            term=term,
            duration_months=duration_months,
            why_need_mentor=why_need_mentor,
            mentor_status="pending",
            supervisor_status="pending",
            final_status="pending"
        )
        
        db.session.add(new_request)
        db.session.commit()

        return jsonify({
            "success": True, 
            "message": "Mentorship request sent successfully!",
            "request_id": new_request.id
        }), 200

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error in request_mentorship: {str(e)}")
        return jsonify({"success": False, "message": "Internal server error"}), 500

@app.route("/mentor_response", methods=["POST"])
def mentor_response():
    # Get form data
    request_id = request.form.get("request_id")
    action = request.form.get("action")

    if not request_id or not action:
        flash("Invalid request!", "error")
        return redirect(url_for("mentordashboard"))

    # Fetch mentorship request
    mentorship_request = MentorshipRequest.query.get(int(request_id))
    if not mentorship_request:
        flash("Request not found!", "error")
        return redirect(url_for("mentordashboard"))

    # Ensure mentor is logged in
    mentor = None
    if "email" in session and session.get("user_type") == "1":
        mentor = User.query.filter_by(email=session["email"]).first()

    if not mentor or mentorship_request.mentor_id != mentor.id:
        flash("This is not your request or you are not logged in as mentor!", "error")
        return redirect(url_for("mentordashboard"))

    # Update status
    mentorship_request.mentor_status = "accepted" if action == "accept" else "rejected"

    try:
        db.session.commit()
        flash(f"Request {action}ed successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Something went wrong while updating the request.", "error")
        print("DB Commit Error:", e)

    # Always redirect to mentor dashboard
    return redirect(url_for("mentor_mentorship_request"))

#--------------x----- PROFILE PICTURE AT TOP ------------------
@app.context_processor
def inject_user_profile_pic():
    if "email" in session:
        user = User.query.filter_by(email=session["email"]).first()
        profile_pic = None
        if user:
            if session.get("user_type") == "1":  # Mentor
                profile = MentorProfile.query.filter_by(user_id=user.id).first()
                profile_pic = profile.profile_picture if profile else None
            elif session.get("user_type") == "2":  # Mentee
                profile = MenteeProfile.query.filter_by(user_id=user.id).first()
                profile_pic = profile.profile_picture if profile else None
            elif session.get("user_type") == "0":  # Supervisor
                profile = SupervisorProfile.query.filter_by(user_id=user.id).first()
                profile_pic = profile.profile_picture if profile else None
            elif session.get("user_type") == "3":  # Institution
                profile = Institution.query.filter_by(user_id=user.id).first()
                profile_pic = profile.profile_picture if profile else None
        return dict(current_user_profile_pic=profile_pic)
    return dict(current_user_profile_pic=None)

@app.route("/editmentorprofile", methods=["GET", "POST"])
def editmentorprofile():
    if "email" not in session or session.get("user_type") != "1":
        return redirect(url_for("signin"))

    # Current user
    user = User.query.filter_by(email=session["email"]).first()
    profile = MentorProfile.query.filter_by(user_id=user.id).first()
    
    # Get institutions for dropdown
    institutions = Institution.query.filter_by(status="active").all()

    if request.method == "POST":
        # Create profile if not exists
        if not profile:
            profile = MentorProfile(user_id=user.id)
            db.session.add(profile)

        # Validate all mandatory fields
        mandatory_fields = {
            "profession": request.form.get("profession"),
            "skills": request.form.get("skills"),
            "role": request.form.get("role"),
            "industry_sector": request.form.get("industry_sector"),
            "organisation": request.form.get("organisation"),
            "years_of_experience": request.form.get("years_of_experience"),
            "whatsapp": request.form.get("whatsapp"),
            "city": request.form.get("city"),
            "country": request.form.get("country"),
            "education": request.form.get("education"),
            "language": request.form.getlist("language"),
            "linkedin_link": request.form.get("linkedin_link"),
            "mentorship_topics": request.form.getlist("mentorship_topics"),
            "mentorship_type_preference": request.form.getlist("mentorship_type_preference"),
            "preferred_communication": request.form.get("preferred_communication"),
            "availability": request.form.get("availability"),
            "connect_frequency": request.form.get("connect_frequency"),
            "preferred_duration": request.form.get("preferred_duration"),
            "why_mentor": request.form.get("why_mentor"),
            "mentorship_philosophy": request.form.get("mentorship_philosophy"),
            "mentorship_motto": request.form.get("mentorship_motto"),
        }
        
        # Check for empty fields
        missing_fields = []
        for field_name, field_value in mandatory_fields.items():
            if not field_value or (isinstance(field_value, list) and len(field_value) == 0):
                missing_fields.append(field_name.replace("_", " ").title())
        
        if missing_fields:
            flash(f"Please fill all mandatory fields: {', '.join(missing_fields)}", "error")
            return redirect(url_for("editmentorprofile"))

        # Update institution if changed
        new_institution = request.form.get("institution")
        print(f" insitiution from from:{new_institution}")

        if new_institution and new_institution != user.institution:
            user.institution = new_institution
            db.session.add(user)

        if new_institution == "Other":
            other_institution = request.form.get("other_institution_name")
            if other_institution:
                user.institution = other_institution
                db.session.add(user)

       # Save form data to mentor profile
        # Handle "Other" option for profession
        profession = request.form.get("profession")
        if profession == "Other":
            other_profession = request.form.get("other_profession")
            profile.profession = other_profession if other_profession else profession
        else:
            profile.profession = profession
        
        profile.skills = request.form.get("skills")
        profile.role = request.form.get("role")
        
        # Handle "Other" option for industry_sector
        industry_sector = request.form.get("industry_sector")
        if industry_sector == "Other":
            other_industry_sector = request.form.get("other_industry_sector")
            profile.industry_sector = other_industry_sector if other_industry_sector else industry_sector
        else:
            profile.industry_sector = industry_sector
        
        profile.organisation = request.form.get("organisation")
        profile.years_of_experience = request.form.get("years_of_experience")
        
        # Handle WhatsApp with country code
        whatsapp_country_code = request.form.get("whatsapp_country_code", "+91")
        whatsapp_number = request.form.get("whatsapp")
        profile.whatsapp = whatsapp_number  # Store just the number, or combine: f"{whatsapp_country_code} {whatsapp_number}"
        
        # Handle "Other" option for country
        country = request.form.get("country")
        if country == "Other":
            other_country = request.form.get("other_country")
            country = other_country if other_country else country
        
        city = request.form.get("city")
        profile.location = f"{city}, {country}" if city and country else city or country
        
        # Handle "Other" option for education
        education = request.form.get("education")
        if education == "Other":
            other_education = request.form.get("other_education")
            profile.education = other_education if other_education else education
        else:
            profile.education = education
        
        # Handle multiple language selection with "Other" option
        languages = request.form.getlist("language")
        other_language = request.form.get("other_language")
        if "Other" in languages and other_language:
            languages = [lang for lang in languages if lang != "Other"]
            languages.append(other_language)
        profile.language = ", ".join(languages) if languages else None
        
        # Social links
        profile.linkedin_link = request.form.get("linkedin_link")
        profile.github_link = request.form.get("github_link")
        profile.portfolio_link = request.form.get("portfolio_link")
        profile.other_social_link = request.form.get("other_social_link")
        
        # Mentorship preferences
        mentorship_topics = request.form.getlist("mentorship_topics")
        profile.mentorship_topics = ", ".join(mentorship_topics) if mentorship_topics else None
        
        mentorship_types = request.form.getlist("mentorship_type_preference")
        profile.mentorship_type_preference = ", ".join(mentorship_types) if mentorship_types else None
        
        profile.preferred_communication = request.form.get("preferred_communication")
        profile.availability = request.form.get("availability")
        profile.connect_frequency = request.form.get("connect_frequency")
        profile.preferred_duration = request.form.get("preferred_duration")
        
        # Mentor philosophy
        profile.why_mentor = request.form.get("why_mentor")
        profile.mentorship_philosophy = request.form.get("mentorship_philosophy")
        profile.mentorship_motto = request.form.get("mentorship_motto")
        
        profile.additional_info = request.form.get("additional_info")

        # Handle profile picture upload
        file = request.files.get("profile_picture")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            profile.profile_picture = filename

        try:
            db.session.commit()
            flash("Profile updated successfully!", "success")
            print("✅ Database commit successful!")
            return redirect(url_for("mentorprofile"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating profile: {str(e)}", "error")
            print(f"❌ Database commit failed: {str(e)}")

    # GET request – pre-fill form with existing data
    # Parse location to get city and country separately
    location = profile.location if profile else ""
    city = ""
    country = ""
    if location and ", " in location:
        parts = location.split(", ", 1)
        city = parts[0]
        country = parts[1] if len(parts) > 1 else ""
    else:
        city = location
    
    return render_template(
        "mentor/editmentorprofile.html",
        full_name=user.name,
        email=user.email,
        institution=user.institution,  # Pass current institution
        institutions=institutions,     # Pass institutions list
        profession=profile.profession if profile else "",
        skills=profile.skills if profile else "",
        role=profile.role if profile else "",
        industry_sector=profile.industry_sector if profile else "",
        organisation=profile.organisation if profile else "",
        years_of_experience=profile.years_of_experience if profile else "",
        whatsapp=profile.whatsapp if profile else "",
        whatsapp_country_code="+91",  # Default country code
        location=location,
        city=city,
        country=country,
        education=profile.education if profile else "",
        language=profile.language if profile else "",
        linkedin_link=profile.linkedin_link if profile else "",
        github_link=profile.github_link if profile else "",
        portfolio_link=profile.portfolio_link if profile else "",
        other_social_link=profile.other_social_link if profile else "",
        mentorship_topics=(profile.mentorship_topics or "") if profile else "",
        mentorship_type_preference=(profile.mentorship_type_preference or "") if profile else "",
        preferred_communication=profile.preferred_communication if profile else "",
        availability=profile.availability if profile else "",
        connect_frequency=profile.connect_frequency if profile else "",
        preferred_duration=profile.preferred_duration if profile else "",
        why_mentor=profile.why_mentor if profile else "",
        mentorship_philosophy=profile.mentorship_philosophy if profile else "",
        mentorship_motto=profile.mentorship_motto if profile else "",
        additional_info=profile.additional_info if profile else "",
        profile_picture=profile.profile_picture if profile else None 
    )


#-----------------edit mentee profile-------------------
@app.route("/editmenteeprofile", methods=["GET", "POST"])
def editmenteeprofile():
    if "email" not in session or session.get("user_type") != "2":
        return redirect(url_for("signin"))

    # Current user
    user = User.query.filter_by(email=session["email"]).first()
    profile = MenteeProfile.query.filter_by(user_id=user.id).first()
    
    # Get institutions for dropdown
    institutions = Institution.query.filter_by(status="active").all()

    if request.method == "POST":
        # Create profile if not exists
        if not profile:
            profile = MenteeProfile(user_id=user.id)
            db.session.add(profile)

        # Check if same as WhatsApp is checked
        same_as_whatsapp = request.form.get("same_as_whatsapp")
        
        # Get mobile number with country code
        mobile_country_code = request.form.get("mobile_country_code", "+91")
        mobile_number = request.form.get("mobile_number")
        
        # Get WhatsApp number - use mobile if same_as_whatsapp is checked
        if same_as_whatsapp:
            whatsapp_country_code = mobile_country_code
            whatsapp_number = mobile_number
        else:
            whatsapp_country_code = request.form.get("whatsapp_country_code", "+91")
            whatsapp_number = request.form.get("whatsapp_number")

        # Validate all mandatory fields
        mandatory_fields = {
            "dob": request.form.get("dob"),
            "school_college_name": request.form.get("school_college_name"),
            "mobile_number": mobile_number,
            "govt_private": request.form.get("govt_private"),
            "stream": request.form.get("stream"),
            "class_year": request.form.get("class_year"),
            "favourite_subject": request.form.get("favourite_subject"),
            "goal": request.form.get("goal"),
            "parent_name": request.form.get("parent_name"),
            "parent_mobile": request.form.get("parent_mobile"),
            "comments": request.form.get("comments"),
        }
        
        # WhatsApp is only mandatory if not same as mobile
        if not same_as_whatsapp:
            mandatory_fields["whatsapp_number"] = whatsapp_number
        
        # Check for empty fields
        missing_fields = []
        for field_name, field_value in mandatory_fields.items():
            if not field_value:
                missing_fields.append(field_name.replace("_", " ").title())
        
        if missing_fields:
            flash(f"Please fill all mandatory fields: {', '.join(missing_fields)}", "error")
            return redirect(url_for("editmenteeprofile"))

        # Update institution if changed
        new_institution = request.form.get("institution")
        if new_institution:
            if new_institution == "Other":
                other_institution = request.form.get("other_institution_name")
                if other_institution:
                    user.institution = other_institution
            else:
                user.institution = new_institution

        # Save form data
        profile.dob = request.form.get("dob")
        profile.school_college_name = request.form.get("school_college_name")
        profile.mobile_number = mobile_number
        profile.whatsapp_number = whatsapp_number
        
        # Handle "Other" option for govt_private
        govt_private = request.form.get("govt_private")
        if govt_private == "Other":
            other_govt_private = request.form.get("other_govt_private")
            profile.govt_private = other_govt_private if other_govt_private else govt_private
        else:
            profile.govt_private = govt_private
        
        # Handle "Other" option for stream
        stream = request.form.get("stream")
        if stream == "Other":
            other_stream = request.form.get("other_stream")
            profile.stream = other_stream if other_stream else stream
        else:
            profile.stream = stream
        
        profile.class_year = request.form.get("class_year")
        profile.favourite_subject = request.form.get("favourite_subject")
        profile.goal = request.form.get("goal")
        profile.parent_name = request.form.get("parent_name")
        profile.parent_mobile = request.form.get("parent_mobile")
        profile.comments = request.form.get("comments")
        profile.terms_agreement = "Yes" if request.form.get("terms_agreement") else "No"

        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"mentee_{profile.id}_{file.filename}")
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                profile.profile_picture = filename

        db.session.commit()
        flash("Mentee profile updated successfully!", "success")
        return redirect(url_for("menteeprofile"))

    # GET request – pre-fill form with existing data
    # Determine if mobile and whatsapp are same
    same_as_whatsapp = "yes" if profile and profile.mobile_number == profile.whatsapp_number else ""
    
    return render_template(
        "mentee/editmenteeprofile.html",
        full_name=user.name,
        email=user.email,
        institution=user.institution,
        institutions=institutions,
        dob=profile.dob if profile else "",
        school_college_name=profile.school_college_name if profile else "",
        mobile_number=profile.mobile_number if profile else "",
        mobile_country_code="+91",  # Default country code
        whatsapp_number=profile.whatsapp_number if profile else "",
        whatsapp_country_code="+91",  # Default country code
        same_as_whatsapp=same_as_whatsapp,
        govt_private=profile.govt_private if profile else "",
        stream=profile.stream if profile else "",
        class_year=profile.class_year if profile else "",
        favourite_subject=profile.favourite_subject if profile else "",
        goal=profile.goal if profile else "",
        parent_name=profile.parent_name if profile else "",
        parent_mobile=profile.parent_mobile if profile else "",
        parent_country_code="+91",  # Default country code
        comments=profile.comments if profile else "",
        terms_agreement=profile.terms_agreement if profile else "",
        profile_picture=profile.profile_picture if profile else None
    )

@app.route("/edit_supervisor_profile", methods=["GET", "POST"])
def editsupervisorprofile():
    if "email" not in session or session.get("user_type") != "0":  
        return redirect(url_for("signin"))

    user = User.query.filter_by(email=session["email"]).first()
    profile = SupervisorProfile.query.filter_by(user_id=user.id).first()
    
    # Get institutions for dropdown
    institutions = Institution.query.filter_by(status="active").all()

    if request.method == "POST":
        if not profile:
            profile = SupervisorProfile(user_id=user.id)
            db.session.add(profile)

        # Validate all mandatory fields
        mandatory_fields = {
            "organisation_or_college": request.form.get("organisation_or_college"),
            "whatsapp_number": request.form.get("whatsapp_number"),
            "location": request.form.get("location"),
            "role": request.form.get("role"),
            "additional_info": request.form.get("additional_info"),
        }
        
        # Check for empty fields
        missing_fields = []
        for field_name, field_value in mandatory_fields.items():
            if not field_value:
                missing_fields.append(field_name.replace("_", " ").title())
        
        if missing_fields:
            flash(f"Please fill all mandatory fields: {', '.join(missing_fields)}", "error")
            return redirect(url_for("editsupervisorprofile"))

        # Update institution if changed
        new_institution = request.form.get("institution")
        if new_institution and new_institution != user.institution:
            user.institution = new_institution
            db.session.add(user)

        profile.organisation = request.form.get("organisation_or_college")
        profile.whatsapp = request.form.get("whatsapp_number")
        profile.location = request.form.get("location")
        profile.role = request.form.get("role")
        profile.additional_info = request.form.get("additional_info")

        # Profile picture handling
        file = request.files.get("profile_picture")
        if file and allowed_file(file.filename):
            filename = f"{user.id}_{int(datetime.now().timestamp())}{secure_filename(file.filename)}"
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            profile.profile_picture = filename
            
        db.session.add(profile)
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("supervisorprofile"))

    return render_template(
        "supervisor/editsupervisorprofile.html",
        full_name=user.name,
        email=user.email,
        institution=user.institution,  # Pass current institution
        institutions=institutions,     # Pass institutions list
        organisation_or_college=profile.organisation if profile else "",
        whatsapp_number=profile.whatsapp if profile else "",
        location=profile.location if profile else "",
        role=profile.role if profile else "",
        additional_info=profile.additional_info if profile else "",
        profile_picture=profile.profile_picture if profile else None
    )

# Remove duplicate code below


# ------------------ PROFILE ------------------
@app.route("/profile")
def profile():
    if "email" not in session:
        return redirect(url_for("signin"))

    user_type = session.get("user_type")
    
    if user_type == "1":
        return redirect(url_for("mentorprofile"))
    elif user_type == "2":
        return redirect(url_for("menteeprofile"))
    elif user_type == "0":
        return redirect(url_for("supervisorprofile"))
    elif user_type == "3":
        return redirect(url_for("institutionprofile"))

# --------- CHANGE PASSWORD ROUTE ---------
@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if "email" not in session:
        flash("Please login first!", "error")
        return redirect(url_for("signin"))
    
    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        
        # Get current user
        user = User.query.filter_by(email=session["email"]).first()
        
        if not user:
            flash("User not found!", "error")
            return redirect(url_for("change_password"))
        
        # Verify current password
        if not check_password_hash(user.password, current_password):
            flash("Current password is incorrect!", "error")
            return redirect(url_for("change_password"))
        
        # Check if new passwords match
        if new_password != confirm_password:
            flash("New passwords do not match!", "error")
            return redirect(url_for("change_password"))
        
        # Check if new password is same as current
        if check_password_hash(user.password, new_password):
            flash("New password must be different from current password!", "error")
            return redirect(url_for("change_password"))
        
        # Update password
        user.password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=8)
        db.session.commit()
        
        flash("✅ Password changed successfully!", "success")
        return redirect(url_for("profile"))
    
    return render_template("change_password.html")

#--------------route for all profiles----------------
@app.route("/mentor_profile")
def mentorprofile(): 
    if "email" in session and session.get("user_type") == "1":
        # Fetch current user
        user = User.query.filter_by(email=session["email"]).first()
        profile = MentorProfile.query.filter_by(user_id=user.id).first()

        # Fetch institution details to get its profile picture
        institution_details = None
        if user.institution_id:
            institution_details = Institution.query.filter_by(id=user.institution_id).first()
        elif user.institution:
            institution_details = Institution.query.filter_by(name=user.institution).first()
        
        institution_profile_picture = institution_details.profile_picture if institution_details else None

        return render_template(
            "mentor/mentorprofile.html",
            show_sidebar=False,
            full_name=user.name,
            email=user.email,
            institution=user.institution,
            profession=profile.profession if profile else "",
            organisation=profile.organisation if profile else "",
            whatsapp=profile.whatsapp if profile else "",
            location=profile.location if profile else "",
            education=profile.education if profile else "",
            language=profile.language if profile else "",
            availability=profile.availability if profile else "",
            connect_frequency=profile.connect_frequency if profile else "",
            preferred_communication=profile.preferred_communication if profile else "",
            other_social_link=profile.other_social_link if profile else "",
            why_mentor=profile.why_mentor if profile else "",
            additional_info=profile.additional_info if profile else "",
            years_of_experience=profile.years_of_experience if profile else "",
            skills=profile.skills if profile else "",
            linkedin_link=profile.linkedin_link if profile else "",
            github_link=profile.github_link if profile else "",
            portfolio_link=profile.portfolio_link if profile else "",
            mentorship_topics=profile.mentorship_topics if profile else "",
            mentorship_type_preference=profile.mentorship_type_preference if profile else "",
            mentorship_philosophy=profile.mentorship_philosophy if profile else "",
            mentorship_motto=profile.mentorship_motto if profile else "",
            profile_picture=profile.profile_picture if profile else None,
            institution_profile_picture=institution_profile_picture
        )
    return redirect(url_for("signin"))

@app.route("/mentee_profile")
def menteeprofile():
    if "email" in session and session.get("user_type") == "2":
        user = User.query.filter_by(email=session["email"]).first()
        profile = MenteeProfile.query.filter_by(user_id=user.id).first()

        dob_formatted = ""
        if profile and profile.dob:
            try:
                # Assume dob stored as yyyy-mm-dd (from HTML <input type="date">)
                dob_formatted = datetime.strptime(profile.dob, "%Y-%m-%d").strftime("%d-%m-%Y")
            except ValueError:
                dob_formatted = profile.dob   # fallback if already formatted

        # Fetch institution details to get its profile picture
        institution_details = None
        if user.institution_id:
            institution_details = Institution.query.filter_by(id=user.institution_id).first()
        elif user.institution:
            institution_details = Institution.query.filter_by(name=user.institution).first()
        
        institution_profile_picture = institution_details.profile_picture if institution_details else None

        # Determine if mobile and whatsapp are same
        same_as_whatsapp = "yes" if profile and profile.mobile_number == profile.whatsapp_number else ""

        return render_template(
            "mentee/menteeprofile.html",
            show_sidebar=False,
            full_name=user.name,
            email=user.email,
            institution=user.institution,
            dob=dob_formatted,
            school_college_name=profile.school_college_name if profile else "",
            mobile_number=profile.mobile_number if profile else "",
            mobile_country_code="+91",  # Default country code
            whatsapp_number=profile.whatsapp_number if profile else "",
            whatsapp_country_code="+91",  # Default country code
            same_as_whatsapp=same_as_whatsapp,
            govt_private=profile.govt_private if profile else "",
            stream=profile.stream if profile else "",
            class_year=profile.class_year if profile else "",
            favourite_subject=profile.favourite_subject if profile else "",
            goal=profile.goal if profile else "",
            parent_name=profile.parent_name if profile else "",
            parent_mobile=profile.parent_mobile if profile else "",
            parent_country_code="+91",  # Default country code
            comments=profile.comments if profile else "",
            terms_agreement=profile.terms_agreement if profile else "",
            profile_picture=profile.profile_picture if profile else None,
            institution_profile_picture=institution_profile_picture
        )
    return redirect(url_for("signin"))

@app.route("/supervisor_profile")
def supervisorprofile():
    # Ensure user is logged in and is a supervisor
    if "email" not in session or session.get("user_type") != "0":
        return redirect(url_for("signin"))

    # Fetch current user
    user = User.query.filter_by(email=session["email"]).first()
    if not user:
        return redirect(url_for("signin"))

    # Fetch supervisor profile
    profile = SupervisorProfile.query.filter_by(user_id=user.id).first()

    return render_template(
        "supervisor/supervisorprofile.html",
        show_sidebar=False,
        full_name=user.name,
        email=user.email,
        organisation_or_college=profile.organisation if profile else "",
        whatsapp_number=profile.whatsapp if profile else "",
        location=profile.location if profile else "",
        role=profile.role if profile else "",
        additional_info=profile.additional_info if profile else "",
        profile_picture=profile.profile_picture if profile else None
    )

# View Mentor Profile (for institution admin)
@app.route("/view_mentor_profile/<int:mentor_id>")
def view_mentor_profile(mentor_id):
    # Allow institution admins to view mentor profiles
    if "email" not in session or session.get("user_type") != "3":
        return redirect(url_for("signin"))
    
    user = User.query.get(mentor_id)
    if not user or user.user_type != "1":
        flash("Mentor not found!", "error")
        return redirect(url_for("institution_mentors"))
    
    profile = MentorProfile.query.filter_by(user_id=mentor_id).first()
    
    return render_template(
        "mentor/mentorprofile.html",
        show_sidebar=False,
        full_name=user.name,
        email=user.email,
        institution=user.institution,
        profession=profile.profession if profile else "",
        organisation=profile.organisation if profile else "",
        whatsapp=profile.whatsapp if profile else "",
        location=profile.location if profile else "",
        education=profile.education if profile else "",
        language=profile.language if profile else "",
        availability=profile.availability if profile else "",
        connect_frequency=profile.connect_frequency if profile else "",
        preferred_communication=profile.preferred_communication if profile else "",
        other_social_link=profile.other_social_link if profile else "",
        why_mentor=profile.why_mentor if profile else "",
        additional_info=profile.additional_info if profile else "",
        years_of_experience=profile.years_of_experience if profile else "",
        skills=profile.skills if profile else "",
        linkedin_link=profile.linkedin_link if profile else "",
        github_link=profile.github_link if profile else "",
        portfolio_link=profile.portfolio_link if profile else "",
        mentorship_topics=profile.mentorship_topics if profile else "",
        mentorship_type_preference=profile.mentorship_type_preference if profile else "",
        mentorship_philosophy=profile.mentorship_philosophy if profile else "",
        mentorship_motto=profile.mentorship_motto if profile else "",
        profile_picture=profile.profile_picture if profile else None
    )

# View Mentee Profile (for institution admin)
@app.route("/view_mentee_profile/<int:mentee_id>")
def view_mentee_profile(mentee_id):
    # Allow institution admins to view mentee profiles
    if "email" not in session or session.get("user_type") != "3":
        return redirect(url_for("signin"))
    
    user = User.query.get(mentee_id)
    if not user or user.user_type != "2":
        flash("Mentee not found!", "error")
        return redirect(url_for("institution_mentees"))
    
    profile = MenteeProfile.query.filter_by(user_id=mentee_id).first()
    
    dob_formatted = ""
    if profile and profile.dob:
        try:
            dob_formatted = datetime.strptime(profile.dob, "%Y-%m-%d").strftime("%d-%m-%Y")
        except ValueError:
            dob_formatted = profile.dob
    
    # Fetch institution details to get its profile picture
    institution_details = None
    if user.institution_id:
        institution_details = Institution.query.filter_by(id=user.institution_id).first()
    elif user.institution:
        institution_details = Institution.query.filter_by(name=user.institution).first()

    institution_profile_picture = institution_details.profile_picture if institution_details else None
    
    return render_template(
        "mentee/menteeprofile.html",
        show_sidebar=False,
        full_name=user.name,
        email=user.email,
        institution=user.institution,
        dob=dob_formatted,
        school_college_name=profile.school_college_name if profile else "",
        mobile_number=profile.mobile_number if profile else "",
        whatsapp_number=profile.whatsapp_number if profile else "",
        govt_private=profile.govt_private if profile else "",
        stream=profile.stream if profile else "",
        class_year=profile.class_year if profile else "",
        favourite_subject=profile.favourite_subject if profile else "",
        goal=profile.goal if profile else "",
        parent_name=profile.parent_name if profile else "",
        parent_mobile=profile.parent_mobile if profile else "",
        comments=profile.comments if profile else "",
        terms_agreement=profile.terms_agreement if profile else "",
        profile_picture=profile.profile_picture if profile else None,
        institution_profile_picture=institution_profile_picture
    )
# ------------------ APPROVE/REJECT MENTORSHIP REQUESTS ------------------
@app.route("/supervisor_response", methods=["POST"])
def supervisor_response():
    if "email" not in session or session.get("user_type") != "0":
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    request_id = request.form.get("request_id")
    action = request.form.get("action")
    
    if not request_id or not action:
        flash("Invalid request!", "error")
        return redirect(url_for("supervisor_response"))
    
    # Fetch mentorship request
    mentorship_request = MentorshipRequest.query.get(int(request_id))
    if not mentorship_request:
        flash("Request not found!", "error")
        return redirect(url_for("supervisor_response"))
    
    # Update status based on action
    if action == "approve":
        mentorship_request.supervisor_status = "approved"
        mentorship_request.final_status = "approved"
        flash("Mentorship request approved!", "success")
        if mentorship_request.duration_months == 12:
            assigned_tasks = assign_master_tasks_to_mentorship(mentorship_request)
            if assigned_tasks:
                flash(f"Mentorship approved! {len(assigned_tasks)} tasks assigned.", "success")
            else:
                flash("Mentorship approved! But no tasks were assigned.", "warning")
        else:
            flash("Mentorship request approved!", "success")

    elif action == "reject":
        mentorship_request.supervisor_status = "rejected"
        mentorship_request.final_status = "rejected"
        flash("Mentorship request rejected!", "success")
    else:
        flash("Invalid action!", "error")
        return redirect(url_for("supervisor_response"))
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash("Something went wrong while updating the request.", "error")
        print("DB Commit Error:", e)
    
    return redirect(url_for("supervisordashboard"))

# ---------- Google Calendar Service Account Config ----------
CALENDAR_SERVICE_SCOPES = ["https://www.googleapis.com/auth/calendar"]
SERVICE_ACCOUNT_FILE = "service_account.json"
DELEGATED_EMAIL = "info@wazireducationsociety.com"  # Organization calendar email

def get_calendar_service():
    """Return Google Calendar API service using service account"""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=CALENDAR_SERVICE_SCOPES
    )
    delegated_creds = creds.with_subject(DELEGATED_EMAIL)
    service = build("calendar", "v3", credentials=delegated_creds)
    return service
 
#-------------------creat meeting request---------------------------------
@app.route("/mentee_create_meeting_request/<int:mentor_id>", methods=["GET"])
def mentee_create_meeting_request(mentor_id):
    if "email" not in session:
        return redirect(url_for("signin"))

    mentee = User.query.filter_by(email=session["email"]).first()
    mentor = User.query.get(mentor_id)
    # sendUpdates="all"


    if not mentor:
        flash("Mentor not found", "error")
        return redirect(url_for("mentors_list"))  # change to your actual route

    return render_template(
        "mentee/mentee_create_meeting_request.html",
        mentee=mentee,
        mentor=mentor
    )

@app.route("/create_meeting_ajax", methods=["POST"])
def create_meeting_ajax():
    if "email" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    title = data.get("title")
    date = data.get("date")
    start_time = data.get("start_time")
    duration = data.get("duration")  # duration in minutes
    mentor_id = data.get("mentor_id")

    if not all([title, date, start_time, duration, mentor_id]):
        return jsonify({"error": "Please fill all fields"}), 400

    mentee = User.query.filter_by(email=session["email"]).first()
    mentor = User.query.get(int(mentor_id))

    if not mentee or not mentor:
        return jsonify({"error": "Mentee or Mentor not found"}), 404

    # Calculate start and end datetime
    start_datetime = dt.datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
    
    # ✅ VALIDATION: Check if meeting date/time is in the past
    current_datetime = dt.datetime.now()
    if start_datetime <= current_datetime:
        return jsonify({"error": "Cannot create meeting for past or current date/time. Please select a future date and time."}), 400
    
    end_datetime = start_datetime + dt.timedelta(minutes=int(duration))

    start_str = start_datetime.isoformat()
    end_str = end_datetime.isoformat()

    service = get_calendar_service()
    event = {
        "summary": title,
        "description": f"Meeting created by {mentee.name} ({mentee.email})",
        "start": {"dateTime": start_str, "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": end_str, "timeZone": "Asia/Kolkata"},
        "attendees": [
            {"email": mentee.email},
            {"email": mentor.email}
        ],
        "conferenceData": {
            "createRequest": {
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
                "requestId": f"meet-{int(dt.datetime.utcnow().timestamp())}"
            }
        }
    }




    event = service.events().insert(
        calendarId="primary",
        body=event,
        conferenceDataVersion=1,
        sendUpdates="all"
    ).execute()

    meet_link = event.get("hangoutLink")
    gcal_event_id = event.get("id")

    # save in db 
    meeting = MeetingRequest(
            requester_id=mentee.id,
            requested_to_id=mentor.id,
            meeting_title=title,
            meeting_date=start_datetime.date(),
            meeting_time=start_datetime.time(),
            meeting_duration=int(duration),
            meet_link=meet_link,
            gcal_event_id=gcal_event_id,
            status="pending"
    )

    db.session.add(meeting)
    db.session.commit()



    return jsonify({
        "message": "Meeting Created ✅",
        "meet_link": event.get("hangoutLink"),
        "title": title,
        "start": start_str,
        "end": end_str,
        "mentee_email": mentee.email,
        "mentor_email": mentor.email
    })

@app.route("/debug_oauth")
def debug_oauth():
    """Debug route to check OAuth users in database"""
    if "email" not in session:
        return "Not logged in"
    
    users = User.query.all()
    
    html = "<h1>OAuth Debug Info</h1>"
    html += f"<p>Total users: {len(users)}</p>"
    html += "<table border='1' cellpadding='10'>"
    html += "<tr><th>ID</th><th>Name</th><th>Email</th><th>Google ID</th><th>OAuth Provider</th><th>User Type</th><th>Created At</th></tr>"
    
    for user in users:
        html += f"<tr>"
        html += f"<td>{user.id}</td>"
        html += f"<td>{user.name}</td>"
        html += f"<td>{user.email}</td>"
        html += f"<td>{user.google_id or 'N/A'}</td>"
        html += f"<td>{user.oauth_provider or 'N/A'}</td>"
        html += f"<td>{user.user_type or 'Not selected'}</td>"
        html += f"<td>{user.oauth_created_at or 'N/A'}</td>"
        html += f"</tr>"
    
    html += "</table>"
    html += "<p><a href='/'>Back to home</a></p>"
    
    return html


def debug_profile():
    if "email" not in session:
        return "Not logged in"
    
    user = User.query.filter_by(email=session["email"]).first()
    if not user:
        return "User not found"
    
    user_type = session.get('user_type')
    profile_complete = check_profile_complete(user.id, user_type)
    
    return f"""
    <h1>Profile Debug Info</h1>
    <p>User: {user.name} ({user.email})</p>
    <p>User Type: {user_type}</p>
    <p>Profile Complete: {profile_complete}</p>
    <p>Should Show Popup: {user_type in ['1', '2'] and not profile_complete}</p>
    <a href="/">Back to home</a>
    """

@app.route("/test_create_profile")
def test_create_profile():
    if "email" not in session:
        return "Not logged in"
    
    user = User.query.filter_by(email=session["email"]).first()
    if not user:
        return "User not found"
    
    user_type = session.get('user_type')
    
    if user_type == "1":
        # Create a basic mentor profile
        profile = MentorProfile.query.filter_by(user_id=user.id).first()
        if not profile:
            profile = MentorProfile(user_id=user.id, profession="Test Profession")
            db.session.add(profile)
            db.session.commit()
            return "Mentor profile created! Profile should now be complete."
        else:
            return "Mentor profile already exists"
    
    elif user_type == "2":
        # Create a basic mentee profile
        profile = MenteeProfile.query.filter_by(user_id=user.id).first()
        if not profile:
            profile = MenteeProfile(user_id=user.id, school_college_name="Test School")
            db.session.add(profile)
            db.session.commit()
            return "Mentee profile created! Profile should now be complete."
        else:
            return "Mentee profile already exists"
    
    return "Not a mentor or mentee"

# ------------------ LOGOUT ------------------
@app.route("/logout")
def logout():
    session.clear()   
    flash("You have been logged out!", "info")
    return redirect(url_for("signin"))


@app.route("/view_mastertask_data")
def view_mastertask_data():
    """View all MasterTask data in a structured format"""
    if "email" not in session:
        return redirect(url_for("signin"))

    # Fetch all meetings ordered by meeting number
    meetings = MasterTask.query.order_by(MasterTask.meeting_number).all()
    
    # Get unique values for filters
    months = sorted({meeting.month for meeting in meetings})
    phases = sorted({meeting.journey_phase for meeting in meetings})
    
    return render_template(
        "view_mastertask_data.html",
        meetings=meetings,
        months=months,
        phases=phases,
        last_updated=datetime.now().strftime("%d-%m-%Y %H:%M")
    )



def create_sample_institutions():
    """Create sample institutions for testing"""
    institutions = [
        {"name": "Delhi University", "city": "Delhi", "country": "India"},
        {"name": "IIT Delhi", "city": "Delhi", "country": "India"},
        {"name": "Amity University", "city": "Noida", "country": "India"},
        {"name": "Other"}
    ]
    
    for inst_data in institutions:
        existing = Institution.query.filter_by(name=inst_data["name"]).first()
        if not existing:
            institution = Institution(
                name=inst_data["name"],
                city=inst_data.get("city", ""),
                country=inst_data.get("country", "")
            )
            db.session.add(institution)
    
    db.session.commit()

if __name__ == "__main__":
    if PRODUCTION:
        # Production mode - don't use debug, use a proper WSGI server
        app.run(debug=False, host="0.0.0.0", port=5000)
    else:
        # Development mode
        app.run(debug=True)
