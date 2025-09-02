from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename


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
# -------------superviser = "0"----------------------
# -------------mantor = "1"--------------------------
# -------------mantee = "2"--------------------------

#---------------DATABASE CONFIGURATION----------------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mantors_connect.db"
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


#------------next table mantors details-------------------

class MentorProfile(db.Model):
    __tablename__="mentor_profile"

    id = db.Column(db.Integer, primary_key=True)

    # foregin key link to User table
    user_id= db.Column(db.Integer, db.ForeignKey("signup_details.id"),nullable=False)

    #  mantor's details
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
    profile_picture = db.Column(db.String(100))  # add this line



#---------add img uplode function--------------





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
            return redirect(url_for("mantordashboard"))
        elif user_type == "2":
            return redirect(url_for("menteedashboard"))
        elif user_type == "0":
            return redirect(url_for("superviserdashboard"))
        
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
            return redirect(url_for("mantordashboard"))
        elif user.user_type == "2":
            return redirect(url_for("menteedashboard"))
        elif user.user_type == "0":
            return redirect(url_for("superviserdashboard"))
        
        
        
        return redirect(url_for("home"))

   
    return render_template("signin.html")

# ------------------ DASHBOARDS ------------------
@app.route("/mantordashboard")
def mantordashboard():
    if "email" in session and session.get("user_type") == "1":
        return render_template("mantordashboard.html", user_email=session["email"])
    return redirect(url_for("signin"))


@app.route("/menteedashboard")
def menteedashboard():
    if "email" in session and session.get("user_type") == "2":
        return render_template("menteedashboard.html", user_email=session["email"])
    return redirect(url_for("signin"))


@app.route("/superviserdashboard")
def superviserdashboard():
    if "email" in session and session.get("user_type") == "0":
        return render_template("superviserdashboard.html", user_email=session["email"])
    return redirect(url_for("signin"))


# ------------------ LOGOUT ------------------
@app.route("/logout")
def logout():
    session.clear()   
    flash("You have been logged out!", "info")
    return redirect(url_for("signin"))



# ------------------ editmantorprofile ------------------
@app.route("/editmantorprofile", methods=["GET", "POST"])
def editmantorprofile():
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
        return redirect(url_for("mantorprofile"))

    # GET request – pre-fill form with existing data
    return render_template(
        "editmantorprofile.html",
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



# ------------------ PROFILE ------------------

@app.route("/profile")
def profile():
    if "email" not in session:
        return redirect(url_for("signin"))

    user_type = session.get("user_type")
    
    if user_type == "1":
        return redirect(url_for("mantorprofile"))
    elif user_type == "2":
        return redirect(url_for("manteeprofile"))
    elif user_type == "0":
        return redirect(url_for("superviserprofile"))

#--------------route for all profiles----------------

@app.route("/mentor_profile")
def mantorprofile(): 
    if "email" in session and session.get("user_type") == "1":
        # Fetch current user
        user = User.query.filter_by(email=session["email"]).first()
        profile = MentorProfile.query.filter_by(user_id=user.id).first()

        return render_template(
            "mantorprofile.html",
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


@app.route("/mentee_profile")
def manteeprofile():
    if "email" in session and session.get("user_type") == "2":
        return render_template("manteeprofile.html", user_email=session["email"])
    return redirect(url_for("signin"))

@app.route("/superviser_profile")
def superviserprofile():
    if "email" in session and session.get("user_type") == "0":
        return render_template("superviserprofile.html", user_email=session["email"])
    return redirect(url_for("signin"))




if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

