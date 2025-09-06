from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
from datetime import datetime




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






#--------------User_type Code------------------------
# -------------supervisor = "0"----------------------
# -------------mentor = "1"--------------------------
# -------------mantee = "2"--------------------------

#---------------DATABASE CONFIGURATION----------------
    
uri = os.getenv("DATABASE_URL")

# Convert postgres:// → postgresql://
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = uri or "sqlite:///mentors_connect.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)

from flask_migrate import Migrate
migrate = Migrate(app, db)





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

    #  mentor's details
    profession = db.Column(db.String(100))
    organisation = db.Column(db.String(150))
    whatsapp = db.Column(db.String(20))
    location = db.Column(db.String(100))
    education = db.Column(db.String(150))
    language = db.Column(db.String(100))
    availability = db.Column(db.String(100))
    connect_frequency = db.Column(db.String(100))
    preferred_communication = db.Column(db.String(100))
    social_link = db.Column(db.String(200))
    why_mentor = db.Column(db.Text)
    additional_info = db.Column(db.Text)
    profile_picture = db.Column(db.String(100)) 
    status = db.Column(db.String(20), default="pending")  # Add this 





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
@app.route("/mentordashboard")
def mentordashboard():
    if "email" in session and session.get("user_type") == "1":
        # fetch current mentor
        user = User.query.filter_by(email=session["email"]).first()

        # fetch all mentees (approved ones only if needed)
        all_mentees = MenteeProfile.query.all()

        return render_template(
            "mentordashboard.html",
            user_email=session["email"],
            all_mentees=all_mentees
        )
    return redirect(url_for("signin"))



@app.route("/menteedashboard")
def menteedashboard():
    if "email" in session and session.get("user_type") == "2":
        # Fetch current mentee
        user = User.query.filter_by(email=session["email"]).first()

        # Mentors already registered (you can filter by approved status if needed)
        all_mentors = MentorProfile.query.filter_by().all()

        # Optionally, fetch mentors already assigned to this mentee
        # This depends if you have a "mentorship" table, for now we just show all mentors
        return render_template(
            "menteedashboard.html",
            user_email=session["email"],
            all_mentors=all_mentors
        )
    return redirect(url_for("signin"))



@app.route("/supervisordashboard")
def supervisordashboard():
    if "email" in session and session.get("user_type") == "0":
        # Fetch all mentors and mentees
        mentors = MentorProfile.query.all()
        mentees = MenteeProfile.query.all()

        # Fetch pending requests
        mentor_requests = MentorProfile.query.filter_by(status='pending').all()
        mentee_requests = MenteeProfile.query.filter_by(status='pending').all()

        return render_template(
            "supervisordashboard.html",
            user_email=session["email"],
            mentors=mentors,
            mentees=mentees,
            mentor_requests=mentor_requests,
            mentee_requests=mentee_requests
        )
    return redirect(url_for("signin"))







#------------------- PROFILE PICTURE AT TOP ------------------
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


# ------------------ LOGOUT ------------------
@app.route("/logout")
def logout():
    session.clear()   
    flash("You have been logged out!", "info")
    return redirect(url_for("signin"))



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
        profile.social_link = request.form.get("social_link")
        profile.why_mentor = request.form.get("mentor_reason")
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
        social_link=profile.social_link if profile else "",
        mentor_reason=profile.why_mentor if profile else "",
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
            social_link=profile.social_link if profile else "",
            mentor_reason=profile.why_mentor if profile else "",
            additional_info=profile.additional_info if profile else "",
            profile_picture=profile.profile_picture if profile else None
        )
    return redirect(url_for("signin"))


from datetime import datetime

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
        full_name=user.name,
        email=user.email,
        organisation_or_college=profile.organisation if profile else "",
        whatsapp_number=profile.whatsapp if profile else "",
        location=profile.location if profile else "",
        role=profile.role if profile else "",
        additional_info=profile.additional_info if profile else "",
        profile_picture=profile.profile_picture if profile else None
    )




if __name__ == "__main__":
    app.run(debug=True)

