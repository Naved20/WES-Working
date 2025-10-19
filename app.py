from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from sqlalchemy import cast, Integer
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from functools import wraps
from sqlalchemy import or_
from datetime import datetime
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
REDIRECT_URI = "http://127.0.0.1:5000/callback"



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

#--------------USER MODEL----------------
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



# Context processor to make profile_complete available in all templates
@app.context_processor
def inject_profile_complete():
    profile_complete = True  # Default to True (no popup)
    
    if "email" in session and session.get("user_type") in ["1", "2"]:
        user = User.query.filter_by(email=session["email"]).first()
        if user:
            profile_complete = check_profile_complete(user.id, session.get("user_type"))
            print(f"🔍 Context Processor - User: {user.email}, Type: {session.get('user_type')}, Profile Complete: {profile_complete}")
        else:
            print(f"❌ Context Processor - User not found for email: {session['email']}")
    else:
        print(f"ℹ️ Context Processor - Not a mentor/mentee or not logged in. User type: {session.get('user_type')}")
    
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
    return render_template("signup.html")

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        user_type = request.form.get("user_type")

        # Basic validation
        if not name or not email or not password or not user_type:
            flash("All fields are required.", "error")
            return render_template("signup.html")
        
        # Check for existing user
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return render_template("signup.html")

        # Hash password
        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, password=hashed_password, user_type=user_type)
        db.session.add(new_user)
        db.session.commit()
        flash("Signup successful! Please sign in.", "success")
        return redirect(url_for("signin"))

    return render_template("signup.html")

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

   
    return render_template("signin.html")

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
        "mentordashboard.html",
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
        "mentor_mentorship_request.html",
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
            "menteedashboard.html",
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
        "supervisordashboard.html",
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
        "supervisor_find_mentor.html",
        all_mentors=mentors,
        professions=options["professions"],
        locations=options["locations"],
        educations=options["educations"],
        experiences=options["experiences"],
        show_sidebar=True
        )
    else:  # default mentor

        return render_template(
        "mentee_find_mentors.html",
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
            "supervisor_find_mentee.html",
            all_mentees=filtered_mentees,
            streams=streams,
            schools=schools,
            goals=goals,
            active_section="mentees",
            show_sidebar=True
        )
    else:  # default mentor
        return render_template(
            "mentor_find_mentees.html",
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
        "mentee_my_mentors.html",
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
                        "profile_complete": mentee_profile.profile_complete
                    }
                })

    return render_template(
        "mentor_my_mentees.html",
        my_mentees=my_mentees_data,
        show_sidebar=True,
        profile_complete=profile_complete  # ADD THIS LINE
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
        "supervisor_find_mentor.html",
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
        "supervisor_find_mentee.html",
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
        "supervisor_request.html",
        all_requests=pending_mentorship_requests,
        mentor_requests=mentor_requests,
        mentee_requests=mentee_requests,
        active_section="requests",
        show_sidebar=True
    )

@app.route("/mentee calendar")
def mentee_calendar():
    if "email" not in session or session.get("user_type") != "2":
        return redirect(url_for("signin"))
    return render_template(
        "mentee_calendar.html",
        show_sidebar=True
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
        "mentee_meeting_details.html",
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
        "mentor_meeting_details.html",
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
        "supervisor_meeting_details.html",
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
        "editmentorprofile.html",
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
        "editmenteeprofile.html",
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
        "editsupervisorprofile.html",
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
            "mentorprofile.html",
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
            "menteeprofile.html",
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
        "supervisorprofile.html",
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
        return redirect(url_for("supervisordashboard"))
    
    # Fetch mentorship request
    mentorship_request = MentorshipRequest.query.get(int(request_id))
    if not mentorship_request:
        flash("Request not found!", "error")
        return redirect(url_for("supervisordashboard"))
    
    # Update status based on action
    if action == "approve":
        mentorship_request.supervisor_status = "approved"
        mentorship_request.final_status = "approved"
        flash("Mentorship request approved!", "success")
    elif action == "reject":
        mentorship_request.supervisor_status = "rejected"
        mentorship_request.final_status = "rejected"
        flash("Mentorship request rejected!", "success")
    else:
        flash("Invalid action!", "error")
        return redirect(url_for("supervisordashboard"))
    
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
        "mentee_create_meeting_request.html",
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


if __name__ == "__main__":
    app.run(debug=True)










