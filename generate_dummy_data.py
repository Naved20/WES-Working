"""
Dummy Data Generation Script
Generates 200 mentees and 186 mentors with:
- 10% Indian names and nationalities
- 90% foreign names and nationalities
- Email format: userID@example.com
- Default password: Info@123
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, MenteeProfile, MentorProfile
from werkzeug.security import generate_password_hash

# Indian names and details
INDIAN_FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Arjun", "Rohan", "Priya", "Ananya", "Diya",
    "Neha", "Pooja", "Rajesh", "Amit", "Suresh", "Deepak", "Kavya", "Shreya"
]

INDIAN_LAST_NAMES = [
    "Sharma", "Patel", "Singh", "Kumar", "Gupta", "Verma", "Rao", "Nair",
    "Desai", "Iyer", "Reddy", "Bhat", "Menon", "Chopra", "Malhotra", "Saxena"
]

INDIAN_CITIES = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad"]
INDIAN_STATES = ["Maharashtra", "Delhi", "Karnataka", "Telangana", "Tamil Nadu", "West Bengal", "Gujarat"]

# Foreign names and details
FOREIGN_FIRST_NAMES = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
    "Thomas", "Charles", "Emma", "Olivia", "Ava", "Isabella", "Sophia", "Mia",
    "Charlotte", "Amelia", "Harper", "Evelyn", "Jean", "Marie", "Pierre", "Luc",
    "Hans", "Klaus", "Maria", "Anna", "Sofia", "Marco", "Giovanni", "Carlos",
    "Juan", "Miguel", "Yuki", "Hiroshi", "Kenji", "Sakura", "Yuki", "Akira"
]

FOREIGN_LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker",
    "Schulz", "Hoffmann", "Dupont", "Martin", "Bernard", "Thomas", "Robert", "Richard",
    "Petit", "Durand", "Lefevre", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel",
    "Garcia", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Sanchez",
    "Rossi", "Russo", "Ferrari", "Esposito", "Bianchi", "Colombo", "Rizzo", "Marino",
    "Greco", "Bruno", "Gallo", "Conti", "De Luca", "Mancini", "Costa", "Giordano",
    "Tanaka", "Suzuki", "Watanabe", "Nakamura", "Kobayashi", "Yamamoto", "Nakajima",
    "Ito", "Okada", "Hasegawa", "Mori", "Ishida", "Maeda", "Fujita", "Ogawa"
]

FOREIGN_COUNTRIES = [
    "USA", "UK", "Canada", "Australia", "Germany", "France", "Spain", "Italy",
    "Netherlands", "Belgium", "Switzerland", "Sweden", "Norway", "Denmark", "Finland",
    "Japan", "South Korea", "China", "Singapore", "Malaysia", "Thailand", "Vietnam",
    "Brazil", "Mexico", "Argentina", "Chile", "Colombia", "Peru", "New Zealand"
]

FOREIGN_CITIES = [
    "New York", "London", "Toronto", "Sydney", "Berlin", "Paris", "Madrid", "Rome",
    "Amsterdam", "Brussels", "Zurich", "Stockholm", "Oslo", "Copenhagen", "Helsinki",
    "Tokyo", "Seoul", "Shanghai", "Singapore", "Bangkok", "Ho Chi Minh City",
    "São Paulo", "Mexico City", "Buenos Aires", "Santiago", "Bogotá", "Lima", "Auckland"
]

# Education and professional data
STREAMS = ["Science", "Commerce", "Arts", "Engineering", "Medical", "Law", "Business"]
SCHOOLS = ["St. Xavier's School", "Delhi Public School", "Doon School", "Mayo College",
           "Cathedral School", "Modern School", "Loreto Convent", "Welham Girls School"]
BOARDS = ["CBSE", "ICSE", "IB", "State Board", "IGCSE"]
UNIVERSITIES = ["IIT Delhi", "Delhi University", "Mumbai University", "Stanford", "MIT",
                "Oxford", "Cambridge", "Harvard", "Yale", "Princeton", "Berkeley"]
INDUSTRIES = ["Technology", "Finance", "Healthcare", "Education", "Retail", "Manufacturing",
              "Consulting", "Media", "Energy", "Telecommunications"]
ROLES = ["Software Engineer", "Data Analyst", "Product Manager", "Business Analyst",
         "Marketing Manager", "Sales Executive", "HR Manager", "Finance Manager"]
SKILLS = ["Python", "Java", "JavaScript", "SQL", "Machine Learning", "Data Analysis",
          "Project Management", "Communication", "Leadership", "Problem Solving"]
GOALS = ["Career Advancement", "Skill Development", "Entrepreneurship", "Higher Education",
         "Work-Life Balance", "Industry Switch", "Leadership Development", "Technical Expertise"]

def generate_indian_user(user_id, user_type):
    """Generate an Indian user"""
    first_name = random.choice(INDIAN_FIRST_NAMES)
    last_name = random.choice(INDIAN_LAST_NAMES)
    name = f"{first_name} {last_name}"
    email = f"{user_id}@example.com"
    password = generate_password_hash("Info@123")
    
    user = User(
        name=name,
        email=email,
        password=password,
        user_type=user_type
    )
    return user

def generate_foreign_user(user_id, user_type):
    """Generate a foreign user"""
    first_name = random.choice(FOREIGN_FIRST_NAMES)
    last_name = random.choice(FOREIGN_LAST_NAMES)
    name = f"{first_name} {last_name}"
    email = f"{user_id}@example.com"
    password = generate_password_hash("Info@123")
    
    user = User(
        name=name,
        email=email,
        password=password,
        user_type=user_type
    )
    return user

def generate_mentee_profile(user):
    """Generate a mentee profile"""
    is_indian = random.random() < 0.1  # 10% Indian
    
    if is_indian:
        city = random.choice(INDIAN_CITIES)
        state = random.choice(INDIAN_STATES)
        country = "India"
    else:
        country = random.choice(FOREIGN_COUNTRIES)
        city = random.choice(FOREIGN_CITIES)
        state = city  # For foreign users, use city as state
    
    # Random date of birth (18-30 years old)
    dob = datetime.now() - timedelta(days=random.randint(365*18, 365*30))
    
    who_am_i_options = ["School Student", "University Student", "Young Professional", 
                        "Seeking Student Job/Internship", "Entrepreneur", "Freelancer", "Career Break"]
    who_am_i = random.choice(who_am_i_options)
    
    profile = MenteeProfile(
        user_id=user.id,
        who_am_i=who_am_i,
        dob=dob.strftime('%Y-%m-%d'),
        father_name=f"{random.choice(INDIAN_FIRST_NAMES if is_indian else FOREIGN_FIRST_NAMES)} {random.choice(INDIAN_LAST_NAMES if is_indian else FOREIGN_LAST_NAMES)}",
        address_line1=f"{random.randint(1, 999)} Main Street",
        city=city,
        state=state,
        country=country,
        postal_code=f"{random.randint(100000, 999999)}",
        school_college_name=random.choice(SCHOOLS),
        mobile_number=f"+{random.randint(1, 99)}{random.randint(1000000000, 9999999999)}",
        whatsapp_number=f"+{random.randint(1, 99)}{random.randint(1000000000, 9999999999)}",
        stream=random.choice(STREAMS),
        class_year=random.choice(["10", "11", "12", "1st Year", "2nd Year", "3rd Year", "4th Year"]),
        favourite_subject=random.choice(["Mathematics", "Physics", "Chemistry", "Biology", "English", "History"]),
        goal=random.choice(GOALS),
        parent_name=f"{random.choice(INDIAN_FIRST_NAMES if is_indian else FOREIGN_FIRST_NAMES)} {random.choice(INDIAN_LAST_NAMES if is_indian else FOREIGN_LAST_NAMES)}",
        parent_mobile=f"+{random.randint(1, 99)}{random.randint(1000000000, 9999999999)}",
        comments=f"Interested in {random.choice(GOALS).lower()}. Looking for guidance and mentorship.",
        mentorship_expectations="Seeking regular guidance and career advice",
        terms_agreement="Yes",
        status="active"
    )
    
    # Add category-specific fields
    if who_am_i == "School Student":
        profile.school_name = random.choice(SCHOOLS)
        profile.school_board = random.choice(BOARDS)
        profile.school_passing_year = str(random.randint(2024, 2026))
    elif who_am_i == "University Student":
        profile.institution_name = random.choice(UNIVERSITIES)
        profile.board_university = random.choice(UNIVERSITIES)
        profile.course_stream = random.choice(STREAMS)
        profile.education_level = random.choice(["Bachelor", "Master", "PhD"])
    elif who_am_i == "Young Professional":
        profile.current_role = random.choice(ROLES)
        profile.industry = random.choice(INDUSTRIES)
        profile.years_experience = str(random.randint(1, 10))
        profile.current_organization = f"{random.choice(['Tech', 'Global', 'Digital', 'Smart'])} Corp"
        profile.key_skills = ", ".join(random.sample(SKILLS, 3))
        profile.career_goal = random.choice(GOALS)
    elif who_am_i == "Seeking Student Job/Internship":
        profile.career_interest = random.choice(INDUSTRIES)
        profile.key_skills = ", ".join(random.sample(SKILLS, 3))
    elif who_am_i == "Entrepreneur":
        profile.startup_name = f"{random.choice(['Tech', 'Smart', 'Digital', 'Global'])} Startup"
        profile.startup_stage = random.choice(["Idea", "MVP", "Early Stage", "Growth"])
        profile.startup_industry = random.choice(INDUSTRIES)
        profile.team_size = str(random.randint(1, 50))
        profile.main_challenge = "Scaling and market expansion"
    elif who_am_i == "Freelancer":
        profile.freelance_skill = random.choice(SKILLS)
        profile.freelance_experience = str(random.randint(1, 10))
        profile.freelance_platforms = "Upwork, Fiverr, Freelancer"
    elif who_am_i == "Career Break":
        profile.last_role = random.choice(ROLES)
        profile.career_break_reason = "Personal reasons"
        profile.restart_field = random.choice(INDUSTRIES)
    
    return profile

def generate_mentor_profile(user):
    """Generate a mentor profile"""
    is_indian = random.random() < 0.1  # 10% Indian
    
    if is_indian:
        location = random.choice(INDIAN_CITIES)
    else:
        location = random.choice(FOREIGN_CITIES)
    
    profile = MentorProfile(
        user_id=user.id,
        profession=random.choice(ROLES),
        skills=", ".join(random.sample(SKILLS, 4)),
        role=random.choice(ROLES),
        industry_sector=random.choice(INDUSTRIES),
        organisation=f"{random.choice(['Tech', 'Global', 'Digital', 'Smart'])} Corp",
        years_of_experience=str(random.randint(5, 25)),
        whatsapp=f"+{random.randint(1, 99)}{random.randint(1000000000, 9999999999)}",
        location=location,
        education=random.choice(["Bachelor", "Master", "PhD"]),
        language="English, Hindi" if is_indian else "English",
        linkedin_link=f"https://linkedin.com/in/{user.name.lower().replace(' ', '')}",
        mentorship_topics=", ".join(random.sample(GOALS, 3)),
        mentorship_type_preference=random.choice(["School Students", "College Students", "Professionals", "All"]),
        preferred_communication=random.choice(["Online", "Offline", "Hybrid"]),
        availability=random.choice(["Weekdays", "Weekends", "Flexible"]),
        connect_frequency=random.choice(["Weekly", "Bi-weekly", "Monthly"]),
        preferred_duration=random.choice(["3 months", "6 months", "1 year", "Ongoing"]),
        why_mentor="To guide and support the next generation of professionals",
        mentorship_philosophy="Believe in personalized guidance and continuous learning",
        mentorship_motto="Empowering minds, shaping futures",
        additional_info="Experienced professional with passion for mentoring",
        status="active"
    )
    
    return profile

def generate_dummy_data():
    """Generate all dummy data"""
    print("🚀 Starting dummy data generation...")
    
    with app.app_context():
        # Clear existing data (optional - comment out if you want to keep existing data)
        # print("🗑️  Clearing existing data...")
        # User.query.delete()
        # db.session.commit()
        
        print("👥 Generating 200 mentees...")
        mentees = []
        for i in range(1, 201):
            user_id = f"mentee_{i}"
            if random.random() < 0.1:  # 10% Indian
                user = generate_indian_user(user_id, "2")
            else:
                user = generate_foreign_user(user_id, "2")
            
            db.session.add(user)
            db.session.flush()  # Get the user ID
            
            profile = generate_mentee_profile(user)
            db.session.add(profile)
            mentees.append(user)
            
            if i % 50 == 0:
                print(f"  ✓ Generated {i} mentees")
        
        print("👨‍🏫 Generating 186 mentors...")
        mentors = []
        for i in range(1, 187):
            user_id = f"mentor_{i}"
            if random.random() < 0.1:  # 10% Indian
                user = generate_indian_user(user_id, "1")
            else:
                user = generate_foreign_user(user_id, "1")
            
            db.session.add(user)
            db.session.flush()  # Get the user ID
            
            profile = generate_mentor_profile(user)
            db.session.add(profile)
            mentors.append(user)
            
            if i % 50 == 0:
                print(f"  ✓ Generated {i} mentors")
        
        print("💾 Committing to database...")
        db.session.commit()
        
        print("\n✅ Dummy data generation completed successfully!")
        print(f"📊 Summary:")
        print(f"   - Total Mentees: 200")
        print(f"   - Total Mentors: 186")
        print(f"   - Total Users: 386")
        print(f"   - Indian Users: ~39 (10%)")
        print(f"   - Foreign Users: ~347 (90%)")
        print(f"\n🔐 Default Credentials:")
        print(f"   - Email format: userID@example.com")
        print(f"   - Password: Info@123")
        print(f"\n📧 Sample Emails:")
        print(f"   - mentee_1@example.com")
        print(f"   - mentor_1@example.com")

if __name__ == "__main__":
    try:
        generate_dummy_data()
    except Exception as e:
        print(f"❌ Error generating dummy data: {str(e)}")
        import traceback
        traceback.print_exc()
