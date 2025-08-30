from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
import sqlalchemy

app = Flask(__name__)
app.secret_key = "1234"
app.permanent_session_lifetime = timedelta(days=10)

# Temporary in-memory "database"
users = {}

@app.route("/")
def home():
    return render_template("index.html")

# ------------------ SIGNUP ------------------
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
            return " Passwords do not match!"

        # Check if user already exists
        if email in users:
            return " User already exists! Please sign in."

        # Save user in "database"
        users[email] = {
            "name": name,
            "email": email,
            "password": password,
            "user_type": user_type
        }

        # Store in session
        session["email"] = email
        session["user_type"] = user_type

        # Redirect based on role
        if user_type == "mentor":
            return redirect(url_for("mantordashboard"))
        else:
            return redirect(url_for("menteedashboard"))

    return render_template("signup.html")

# ------------------ SIGNIN ------------------
@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        session.permanent = True
        email = request.form["email"]
        password = request.form["password"]

        # Check if user exists
        if email not in users:
            return "User not found! Please sign up first."

        # Check password
        if users[email]["password"] != password:
            return "Incorrect password!"

        # Save session
        session["email"] = email
        session["user_type"] = users[email]["user_type"]

        # Redirect based on role
        if users[email]["user_type"] == "mentor":
            return redirect(url_for("mantordashboard"))
        else:
            return redirect(url_for("menteedashboard"))

    return render_template("signin.html")

# ------------------ DASHBOARDS ------------------
@app.route("/mantordashboard")
def mantordashboard():
    if "email" in session and session.get("user_type") == "mentor":
        return render_template("mantordashboard.html", user_email=session["email"])
    return redirect(url_for("signin"))

@app.route("/menteedashboard")
def menteedashboard():
    if "email" in session and session.get("user_type") == "mentee":
        return render_template("menteedashboard.html", user_email=session["email"])
    return redirect(url_for("signin"))

# ------------------ LOGOUT ------------------
@app.route("/logout")
def logout():
    session.pop("email",None)
    flash("you have been loged out!","info")
    return redirect(url_for("signin"))

if __name__ == "__main__":
    app.run(debug=True)






# from flask import Flask, redirect, url_for, render_template, request,session

# app = Flask(__name__)
# app.secret_key = "1234"

# @app.route("/")
# def home():
#     return render_template("index.html")

# @app.route("/signin", methods=["GET", "POST"])
# def signin():
#     if request.method == "POST":
#         email = request.form["email"]
#         session["email"]=email
#         return redirect(url_for("mantordashboard", user=email))
#     return render_template("signin.html")

# @app.route("/mantordashboard")
# def mantordashboard():
#     if "email" in session:
#         email = session["email"]
#         user = request.args.get("user")
#         return render_template("mantordashboard.html", user_email=user)
#     else:
#         return redirect(url_for("signin"))



# @app.route("/signup", methods=["GET", "POST"])
# def signup():
#     if request.method =="POST":
#         name = request.form["name"]
#         email = request.form["email"]
#         user_type = request.form["user-type"]
#         password = request.form["password"]
#         confirm_password = request.form["confirm-password"]

#         # Password check
#         if password != confirm_password:
#             return "Passwords do not match!"


#         # Redirect based on user type
#         if user_type == "mentor":
#             return redirect(url_for("mantordashboard", user=email))
#         elif user_type == "mentee":
#             return redirect(url_for("menteedashboard", user=email))
        
#     return render_template("signup.html")

   
# @app.route("/menteedashboard")
# def menteedashboard():
#         user = request.args.get("user")
#         return render_template("menteedashboard.html", user_email=user)

   
    
# if __name__ == "__main__":
#     app.run(debug=True)

