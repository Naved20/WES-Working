from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from sqlalchemy import cast, Integer
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy import or_
import os
import json 
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime as dt



app = Flask(__name__)
app.secret_key = "1234"
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


# ----------config---------- 
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # ONLY for local dev (http). Remove in production.
CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile",]
REDIRECT_URI = "http://127.0.0.1:8000/callback"



#--------------User_type Code------------------------
# -------------supervisor = "0"----------------------
# -------------mentor = "1"--------------------------
# -------------mantee = "2"--------------------------

app.config["SQLALCHEMY_DATABASE_URI"] ="sqlite:///mentors_connect.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
from flask_migrate import Migrate
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
    password = db.Column(db.String(200), nullable=False)   # length thoda bada
    user_type = db.Column(db.String(10), nullable=False)

    #connect form another table
    mentor_profile = db.relationship("MentorProfile", backref="user", uselist=False)

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

#------------next table mentee details-------------------
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

#------------next table supervisor details-------------------
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
    status = db.Column(db.String(20), default="pending")  # 'pending', 'approved', 'rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    requester = db.relationship("User", foreign_keys=[requester_id], backref="sent_meeting_requests")
    requested_to = db.relationship("User", foreign_keys=[requested_to_id], backref="received_meeting_requests")


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
    Check if user profile is complete
    Returns True if profile exists and has basic data, False if empty/not created
    """
    print(f"🔍 Checking profile completion for user_id: {user_id}, user_type: {user_type}")
    
    if user_type == "1":  # Mentor
        profile = MentorProfile.query.filter_by(user_id=user_id).first()
        print(f"📊 Mentor profile found: {profile is not None}")
        if profile:
            # Check if profile has at least some basic data filled
            has_basic_info = any([
                profile.profession, 
                profile.organisation, 
                profile.whatsapp,
                profile.location,
                profile.education,
                profile.years_of_experience
            ])
            print(f"✅ Mentor profile complete: {has_basic_info}")
            return has_basic_info
        print("❌ No mentor profile found")
        return False
    
    elif user_type == "2":  # Mentee
        profile = MenteeProfile.query.filter_by(user_id=user_id).first()
        print(f"📊 Mentee profile found: {profile is not None}")
        if profile:
            # Check if profile has at least some basic data filled
            has_basic_info = any([
                profile.dob,
                profile.school_college_name, 
                profile.mobile_number,
                profile.stream,
                profile.class_year,
                profile.goal
            ])
            print(f"✅ Mentee profile complete: {has_basic_info}")
            return has_basic_info
        print("❌ No mentee profile found")
        return False
    
    elif user_type == "0":  # Supervisor
        profile = SupervisorProfile.query.filter_by(user_id=user_id).first()
        print(f"📊 Supervisor profile found: {profile is not None}")
        if profile:
            has_basic_info = any([
                profile.organisation,
                profile.whatsapp,
                profile.location,
                profile.role
            ])
            print(f"✅ Supervisor profile complete: {has_basic_info}")
            return has_basic_info
        print("❌ No supervisor profile found")
        return False
    
    print(f"⚠️ Unknown user type: {user_type}")
    return True  # Default to True for unknown types (no popup)

#-------------HOME----------------
@app.route("/")
def home():
    return render_template("index.html")

#--------------SIGNUP----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        user_type = request.form["user-type"]
        password = request.form["password"]
        confirm_password = request.form["confirm-password"]

        # Password check
        if password != confirm_password:
            return "Passwords do not match!"

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return "User already exists! Please sign in."

        # Save user in "database"
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        new_user = User(name=name, email=email, password=hashed_password, user_type=user_type)
        db.session.add(new_user)
        db.session.commit()

        #store in session
        session["email"] = email
        session["user_type"] = user_type

        #render based on role
        if user_type == "1":
            return redirect(url_for("mentordashboard"))
        elif user_type == "2":
            return redirect(url_for("menteedashboard"))
        elif user_type == "0":
            return redirect(url_for("supervisordashboard"))

        # agar user_type galat aaya ho
        return redirect(url_for("signin"))

    # agar request GET ho to signup form dikhana
    return render_template("auth/signup.html")

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        user_type = request.form.get("user_type")

        # Basic validation
        if not name or not email or not password or not user_type:
            flash("All fields are required.", "error")
            return render_template("auth/signup.html")
        
        # Check for existing user
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return render_template("auth/signup.html")

        # Hash password
        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, password=hashed_password, user_type=user_type)
        db.session.add(new_user)
        db.session.commit()
        flash("Signup successful! Please sign in.", "success")
        return redirect(url_for("signin"))

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

        # Redirect based on role
        if user.user_type == "1":
            return redirect(url_for("mentordashboard"))
        elif user.user_type == "2":
            return redirect(url_for("menteedashboard"))
        elif user.user_type == "0":
            return redirect(url_for("supervisordashboard"))

        
        
        return redirect(url_for("home"))

   
    return render_template("auth/signin.html")

# ------------------ DASHBOARDS ------------------
@app.route("/mentordashboard", methods=["GET", "POST"])
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
                        "profile_complete": mentee_profile_complete  # Use the calculated value
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

#------------------------------------------------------------------------------------------------------------------- 
#------------------------------------------------------------------------------------------------------------------- 
#------------------------------------------------------------------------------------------------------------------- 


# ------------------ SUPERVISOR TASK MANAGEMENT ROUTES ------------------

@app.route("/supervisor_tasks")
def supervisor_tasks():
    if "email" not in session or session.get("user_type") != "0":
        return redirect(url_for("signin"))
    
    # Get all tasks data for supervisor overview
    try:
        # Get all personal tasks with mentor and mentee info
        personal_tasks = PersonalTask.query\
            .join(User, PersonalTask.mentee_id == User.id)\
            .join(User, PersonalTask.mentor_id == User.id)\
            .add_columns(
                PersonalTask.id,
                PersonalTask.title,
                PersonalTask.description,
                PersonalTask.due_date,
                PersonalTask.priority,
                PersonalTask.status,
                PersonalTask.progress,
                PersonalTask.created_date,
                PersonalTask.completed_date,
                User.name.label('mentee_name'),
                User.name.label('mentor_name')
            )\
            .all()

        # Get all mentee tasks with master task, mentor and mentee info
        mentee_tasks = MenteeTask.query\
            .join(MasterTask, MenteeTask.task_id == MasterTask.id)\
            .join(User, MenteeTask.mentee_id == User.id)\
            .join(User, MenteeTask.mentor_id == User.id)\
            .add_columns(
                MenteeTask.id,
                MasterTask.purpose_of_call.label('title'),
                MasterTask.mentee_focus.label('description'),
                MenteeTask.due_date,
                db.literal('medium').label('priority'),  # Default for master tasks
                MenteeTask.status,
                MenteeTask.progress,
                MenteeTask.assigned_date.label('created_date'),
                MenteeTask.completed_date,
                User.name.label('mentee_name'),
                User.name.label('mentor_name'),
                MasterTask.month,
                MenteeTask.meeting_number,
                db.literal('master').label('task_type')
            )\
            .all()

        # Combine all tasks
        all_tasks = []
        
        # Add personal tasks
        for task in personal_tasks:
            all_tasks.append({
                'id': task.id,
                'title': task.title,
                'description': task.description or 'No description',
                'due_date': task.due_date,
                'priority': task.priority,
                'status': task.status,
                'progress': task.progress or 0,
                'mentee_name': task.mentee_name,
                'mentor_name': task.mentor_name,
                'created_date': task.created_date,
                'completed_date': task.completed_date,
                'task_type': 'personal',
                'category': 'Mentor Assigned'
            })
        
        # Add mentee tasks (master tasks)
        for task in mentee_tasks:
            all_tasks.append({
                'id': task.id,
                'title': f"{task.title} - Month {task.month}",
                'description': task.description or 'No description',
                'due_date': task.due_date,
                'priority': task.priority,
                'status': task.status,
                'progress': task.progress or 0,
                'mentee_name': task.mentee_name,
                'mentor_name': task.mentor_name,
                'created_date': task.created_date,
                'completed_date': task.completed_date,
                'task_type': 'master',
                'category': 'Mentorship Program',
                'month': task.month,
                'meeting_number': task.meeting_number
            })

        # Calculate statistics
        total_tasks = len(all_tasks)
        completed_tasks = len([t for t in all_tasks if t['status'] == 'completed'])
        pending_tasks = len([t for t in all_tasks if t['status'] in ['pending', 'in-progress']])
        
        today = datetime.utcnow().date()
        overdue_tasks = len([t for t in all_tasks if t['due_date'] and t['due_date'].date() < today and t['status'] != 'completed'])

        # Get all mentors and mentees for filters
        all_mentors = User.query.filter_by(user_type='1').all()
        all_mentees = User.query.filter_by(user_type='2').all()

        # Get active mentors (those with assigned tasks)
        active_mentor_ids = set(task['mentor_name'] for task in all_tasks)
        active_mentors = [mentor for mentor in all_mentors if mentor.name in active_mentor_ids]

        # Get active mentees (those with assigned tasks)
        active_mentee_ids = set(task['mentee_name'] for task in all_tasks)
        active_mentees = [mentee for mentee in all_mentees if mentee.name in active_mentee_ids]

        return render_template(
            "supervisor/supervisor_tasks.html",
            show_sidebar=True,
            profile_complete=True,
            all_tasks=all_tasks,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            pending_tasks=pending_tasks,
            overdue_tasks=overdue_tasks,
            active_mentors=active_mentors,
            active_mentees=active_mentees,
            today=today
        )

    except Exception as e:
        print(f"Error in supervisor_tasks: {str(e)}")
        # Return empty data in case of error
        return render_template(
            "supervisor/supervisor_tasks.html",
            show_sidebar=True,
            profile_complete=True,
            all_tasks=[],
            total_tasks=0,
            completed_tasks=0,
            pending_tasks=0,
            overdue_tasks=0,
            active_mentors=[],
            active_mentees=[],
            today=datetime.utcnow().date()
        )

@app.route("/get_supervisor_task_details/<int:task_id>")
def get_supervisor_task_details(task_id):
    if "email" not in session or session.get("user_type") != "0":
        return jsonify({"success": False, "message": "Unauthorized"})
    
    try:
        # Try to find task in personal tasks first
        personal_task = PersonalTask.query\
            .join(User, PersonalTask.mentee_id == User.id)\
            .join(User, PersonalTask.mentor_id == User.id)\
            .filter(PersonalTask.id == task_id)\
            .first()
        
        if personal_task:
            task_data = {
                "id": personal_task.id,
                "type": "personal",
                "title": personal_task.title,
                "description": personal_task.description,
                "due_date": personal_task.due_date.strftime('%Y-%m-%d') if personal_task.due_date else None,
                "priority": personal_task.priority,
                "status": personal_task.status,
                "progress": personal_task.progress or 0,
                "mentee_name": personal_task.mentee.name if personal_task.mentee else "Unknown",
                "mentor_name": personal_task.mentor.name if personal_task.mentor else "Unknown",
                "created_date": personal_task.created_date.strftime('%Y-%m-%d') if personal_task.created_date else None,
                "completed_date": personal_task.completed_date.strftime('%Y-%m-%d') if personal_task.completed_date else None,
                "category": "Mentor Assigned"
            }
            return jsonify({"success": True, "task": task_data})
        
        # If not found in personal tasks, try mentee tasks
        mentee_task = MenteeTask.query\
            .join(MasterTask, MenteeTask.task_id == MasterTask.id)\
            .join(User, MenteeTask.mentee_id == User.id)\
            .join(User, MenteeTask.mentor_id == User.id)\
            .filter(MenteeTask.id == task_id)\
            .first()
        
        if mentee_task:
            task_data = {
                "id": mentee_task.id,
                "type": "master",
                "title": mentee_task.master_task.purpose_of_call,
                "description": mentee_task.master_task.mentee_focus,
                "due_date": mentee_task.due_date.strftime('%Y-%m-%d') if mentee_task.due_date else None,
                "priority": "medium",
                "status": mentee_task.status,
                "progress": mentee_task.progress or 0,
                "mentee_name": mentee_task.mentee.name if mentee_task.mentee else "Unknown",
                "mentor_name": mentee_task.mentor.name if mentee_task.mentor else "Unknown",
                "created_date": mentee_task.assigned_date.strftime('%Y-%m-%d') if mentee_task.assigned_date else None,
                "completed_date": mentee_task.completed_date.strftime('%Y-%m-%d') if mentee_task.completed_date else None,
                "category": "Mentorship Program",
                "month": mentee_task.month,
                "meeting_number": mentee_task.meeting_number,
                "mentor_focus": mentee_task.master_task.mentor_focus,
                "program_actions": mentee_task.master_task.program_incharge_actions
            }
            return jsonify({"success": True, "task": task_data})
        
        return jsonify({"success": False, "message": "Task not found"})
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route("/get_supervisor_analytics")
def get_supervisor_analytics():
    if "email" not in session or session.get("user_type") != "0":
        return jsonify({"success": False, "message": "Unauthorized"})
    
    try:
        # Get all tasks for analytics
        personal_tasks = PersonalTask.query.all()
        mentee_tasks = MenteeTask.query.all()
        
        all_tasks = list(personal_tasks) + list(mentee_tasks)
        
        # Calculate analytics
        total_tasks = len(all_tasks)
        completed_tasks = len([t for t in all_tasks if t.status == 'completed'])
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Get active mentors count
        active_mentors = User.query.filter_by(user_type='1').count()
        
        # Get active mentees count  
        active_mentees = User.query.filter_by(user_type='2').count()
        
        # Calculate overdue tasks
        today = datetime.utcnow().date()
        overdue_tasks = len([t for t in all_tasks if t.due_date and t.due_date.date() < today and t.status != 'completed'])
        
        analytics_data = {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": round(completion_rate, 1),
            "active_mentors": active_mentors,
            "active_mentees": active_mentees,
            "overdue_tasks": overdue_tasks,
            "pending_tasks": total_tasks - completed_tasks - overdue_tasks
        }
        
        return jsonify({"success": True, "analytics": analytics_data})
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    
# More optimized version of supervisor_tasks route
@app.route("/supervisor_tasks_optimized")
def supervisor_tasks_optimized():
    if "email" not in session or session.get("user_type") != "0":
        return redirect(url_for("signin"))
    
    try:
        # Get personal tasks with joins in single query
        personal_tasks_query = db.session.query(
            PersonalTask.id,
            PersonalTask.title,
            PersonalTask.description,
            PersonalTask.due_date,
            PersonalTask.priority,
            PersonalTask.status,
            PersonalTask.progress,
            PersonalTask.created_date,
            PersonalTask.completed_date,
            User.name.label('mentee_name'),
            User.name.label('mentor_name')
        ).join(User, PersonalTask.mentee_id == User.id)\
         .join(User, PersonalTask.mentor_id == User.id)\
         .all()

        # Convert to list of dicts
        personal_tasks = []
        for task in personal_tasks_query:
            personal_tasks.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'due_date': task.due_date,
                'priority': task.priority,
                'status': task.status,
                'progress': task.progress,
                'mentee_name': task.mentee_name,
                'mentor_name': task.mentor_name,
                'created_date': task.created_date,
                'completed_date': task.completed_date,
                'task_type': 'personal',
                'category': 'Mentor Assigned'
            })

        # Similar optimization for mentee tasks...
        # ... (rest of the optimized code)

    except Exception as e:
        print(f"Error: {str(e)}")
        # Return error page or empty data


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
        return dict(current_user_profile_pic=profile_pic)
    return dict(current_user_profile_pic=None)

# ------------------ editmentorprofile ------------------
@app.route("/editmentorprofile", methods=["GET", "POST"])
def editmentorprofile():
    if "email" not in session or session.get("user_type") != "1":
        return redirect(url_for("signin"))

    # Current user
    user = User.query.filter_by(email=session["email"]).first()
    profile = MentorProfile.query.filter_by(user_id=user.id).first()

    if request.method == "POST":
        # Create profile if not exists
        if not profile:
            profile = MentorProfile(user_id=user.id)


        # Save form data
        profile.profession = request.form.get("profession")
        profile.organisation = request.form.get("organisation_or_college")
        profile.whatsapp = request.form.get("whatsapp_number")
        profile.location = request.form.get("location")
        profile.education = request.form.get("education")
        profile.language = request.form.get("language")
        profile.availability = request.form.get("availability_month")
        profile.connect_frequency = request.form.get("connect_frequency")
        profile.preferred_communication = request.form.get("preferred_communication")
        profile.other_social_link = request.form.get("other_social_link")
        profile.why_mentor = request.form.get("mentor_reason")
        profile.years_of_experience = request.form.get("experience")  # new field
        profile.additional_info = request.form.get("additional_info")  # optional

        # Handle profile picture upload
        file = request.files.get("profile_picture")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Save file to upload folder
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            #store filename in db
            profile.profile_picture = filename

        db.session.add(profile)
        db.session.commit()

        flash("Profile updated successfully!", "success")
        # Redirect to mentor profile page with data
        return redirect(url_for("mentorprofile"))

    # GET request – pre-fill form with existing data
    return render_template(
        "mentor/editmentorprofile.html",
        full_name=user.name,
        email=user.email,
        profession=profile.profession if profile else "",
        organisation_or_college=profile.organisation if profile else "",
        whatsapp_number=profile.whatsapp if profile else "",
        location=profile.location if profile else "",
        education=profile.education if profile else "",
        language=profile.language if profile else "",
        availability_month=profile.availability if profile else "",
        connect_frequency=profile.connect_frequency if profile else "",
        preferred_communication=profile.preferred_communication if profile else "",
        other_social_link=profile.other_social_link if profile else "",
        mentor_reason=profile.why_mentor if profile else "",
        additional_info=profile.additional_info if profile else "",
        experience=profile.years_of_experience if profile else "",
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

    if request.method == "POST":
        # Create profile if not exists
        if not profile:
            profile = MenteeProfile(user_id=user.id)

        # Save form data
        profile.dob = request.form.get("dob")
        profile.school_college_name = request.form.get("school_college_name")
        profile.mobile_number = request.form.get("mobile_number")
        profile.whatsapp_number = request.form.get("whatsapp_number")
        profile.govt_private = request.form.get("govt_private")
        profile.stream = request.form.get("stream")
        profile.class_year = request.form.get("class_year")
        profile.favourite_subject = request.form.get("favourite_subject")
        profile.goal = request.form.get("goal")
        profile.parent_name = request.form.get("parent_name")
        profile.parent_mobile = request.form.get("parent_mobile")
        profile.comments = request.form.get("comments")
        profile.terms_agreement = request.form.get("terms_agreement")

        # Handle profile picture upload
        file = request.files.get("profile_picture")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Save file to upload folder
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            # Store filename in db
            profile.profile_picture = filename

        db.session.add(profile)
        db.session.commit()

        flash("Mentee profile updated successfully!", "success")
        # Redirect to mentee profile page
        return redirect(url_for("menteeprofile"))

    # GET request – pre-fill form with existing data
    return render_template(
        "mentee/editmenteeprofile.html",
        full_name=user.name,
        email=user.email,
        dob=profile.dob if profile else "",
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
        profile_picture=profile.profile_picture if profile else None
    )

#----------------edit supervisor profile-------------------
@app.route("/edit_supervisor_profile", methods=["GET", "POST"])
def editsupervisorprofile():
    if "email" not in session or session.get("user_type") != "0":  
        return redirect(url_for("signin"))

    user = User.query.filter_by(email=session["email"]).first()
    profile = SupervisorProfile.query.filter_by(user_id=user.id).first()

    if request.method == "POST":
        if not profile:
            profile = SupervisorProfile(user_id=user.id)
            db.session.add(profile)

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
        organisation_or_college=profile.organisation if profile else "",
        whatsapp_number=profile.whatsapp if profile else "",
        location=profile.location if profile else "",
        role=profile.role if profile else "",
        additional_info=profile.additional_info if profile else "",
        profile_picture=profile.profile_picture if profile else None
    )

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

#--------------route for all profiles----------------
@app.route("/mentor_profile")
def mentorprofile(): 
    if "email" in session and session.get("user_type") == "1":
        # Fetch current user
        user = User.query.filter_by(email=session["email"]).first()
        profile = MentorProfile.query.filter_by(user_id=user.id).first()

        return render_template(
            "mentor/mentorprofile.html",
            show_sidebar=False,
        full_name=user.name,
        email=user.email,
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

        return render_template(
            "mentee/menteeprofile.html",
            show_sidebar=False,
            full_name=user.name,
            email=user.email,
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
            profile_picture=profile.profile_picture if profile else None
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
SCOPES = ["https://www.googleapis.com/auth/calendar"]
SERVICE_ACCOUNT_FILE = "service_account.json"
DELEGATED_EMAIL = "info@wazireducationsociety.com"  # Organization calendar email

def get_calendar_service():
    """Return Google Calendar API service using service account"""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
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

@app.route("/debug_profile")
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





if __name__ == "__main__":
    app.run(debug=True)




