"""
Comprehensive Dummy Data Generation Script
Generates:
- 100 mentees (user_type="2")
- 100 mentors (user_type="1")
- 100 real institutions worldwide (including Luxembourg)
- 10% Indian names/nationalities
- 90% foreign names/nationalities
- Email format: userID@xexample.com
- Password: Info@123
"""

import sys
import os
from datetime import datetime, timedelta
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, MenteeProfile, MentorProfile, Institution
from werkzeug.security import generate_password_hash

# ==================== REAL INSTITUTIONS WORLDWIDE ====================

REAL_INSTITUTIONS = [
    # Luxembourg Institutions
    {"name": "University of Luxembourg", "city": "Luxembourg City", "country": "Luxembourg", "type": "university"},
    {"name": "Université du Luxembourg", "city": "Esch-sur-Alzette", "country": "Luxembourg", "type": "university"},
    {"name": "Lycée de Garçons", "city": "Luxembourg City", "country": "Luxembourg", "type": "college"},
    {"name": "Lycée Classique de Diekirch", "city": "Diekirch", "country": "Luxembourg", "type": "college"},
    {"name": "Lycée Technique de Differdange", "city": "Differdange", "country": "Luxembourg", "type": "college"},
    
    # USA Universities
    {"name": "Harvard University", "city": "Cambridge", "country": "USA", "type": "university"},
    {"name": "Stanford University", "city": "Stanford", "country": "USA", "type": "university"},
    {"name": "MIT", "city": "Cambridge", "country": "USA", "type": "university"},
    {"name": "Yale University", "city": "New Haven", "country": "USA", "type": "university"},
    {"name": "Princeton University", "city": "Princeton", "country": "USA", "type": "university"},
    {"name": "University of California, Berkeley", "city": "Berkeley", "country": "USA", "type": "university"},
    {"name": "University of Chicago", "city": "Chicago", "country": "USA", "type": "university"},
    {"name": "Columbia University", "city": "New York", "country": "USA", "type": "university"},
    {"name": "University of Pennsylvania", "city": "Philadelphia", "country": "USA", "type": "university"},
    {"name": "Northwestern University", "city": "Evanston", "country": "USA", "type": "university"},
    
    # UK Universities
    {"name": "University of Oxford", "city": "Oxford", "country": "UK", "type": "university"},
    {"name": "University of Cambridge", "city": "Cambridge", "country": "UK", "type": "university"},
    {"name": "Imperial College London", "city": "London", "country": "UK", "type": "university"},
    {"name": "University College London", "city": "London", "country": "UK", "type": "university"},
    {"name": "London School of Economics", "city": "London", "country": "UK", "type": "university"},
    {"name": "University of Manchester", "city": "Manchester", "country": "UK", "type": "university"},
    {"name": "University of Edinburgh", "city": "Edinburgh", "country": "UK", "type": "university"},
    {"name": "University of Bristol", "city": "Bristol", "country": "UK", "type": "university"},
    {"name": "University of Warwick", "city": "Coventry", "country": "UK", "type": "university"},
    {"name": "Durham University", "city": "Durham", "country": "UK", "type": "university"},
    
    # Canada Universities
    {"name": "University of Toronto", "city": "Toronto", "country": "Canada", "type": "university"},
    {"name": "McGill University", "city": "Montreal", "country": "Canada", "type": "university"},
    {"name": "University of British Columbia", "city": "Vancouver", "country": "Canada", "type": "university"},
    {"name": "McMaster University", "city": "Hamilton", "country": "Canada", "type": "university"},
    {"name": "University of Alberta", "city": "Edmonton", "country": "Canada", "type": "university"},
    
    # Australia Universities
    {"name": "University of Melbourne", "city": "Melbourne", "country": "Australia", "type": "university"},
    {"name": "University of Sydney", "city": "Sydney", "country": "Australia", "type": "university"},
    {"name": "Australian National University", "city": "Canberra", "country": "Australia", "type": "university"},
    {"name": "University of New South Wales", "city": "Sydney", "country": "Australia", "type": "university"},
    {"name": "University of Queensland", "city": "Brisbane", "country": "Australia", "type": "university"},
    
    # Germany Universities
    {"name": "Heidelberg University", "city": "Heidelberg", "country": "Germany", "type": "university"},
    {"name": "Technical University of Munich", "city": "Munich", "country": "Germany", "type": "university"},
    {"name": "Humboldt University of Berlin", "city": "Berlin", "country": "Germany", "type": "university"},
    {"name": "University of Bonn", "city": "Bonn", "country": "Germany", "type": "university"},
    {"name": "University of Hamburg", "city": "Hamburg", "country": "Germany", "type": "university"},
    
    # France Universities
    {"name": "Sorbonne University", "city": "Paris", "country": "France", "type": "university"},
    {"name": "PSL Research University", "city": "Paris", "country": "France", "type": "university"},
    {"name": "University of Lyon", "city": "Lyon", "country": "France", "type": "university"},
    {"name": "University of Marseille", "city": "Marseille", "country": "France", "type": "university"},
    {"name": "University of Toulouse", "city": "Toulouse", "country": "France", "type": "university"},
    
    # Switzerland Universities
    {"name": "ETH Zurich", "city": "Zurich", "country": "Switzerland", "type": "university"},
    {"name": "University of Zurich", "city": "Zurich", "country": "Switzerland", "type": "university"},
    {"name": "University of Geneva", "city": "Geneva", "country": "Switzerland", "type": "university"},
    {"name": "University of Bern", "city": "Bern", "country": "Switzerland", "type": "university"},
    {"name": "University of Lausanne", "city": "Lausanne", "country": "Switzerland", "type": "university"},
    
    # Netherlands Universities
    {"name": "University of Amsterdam", "city": "Amsterdam", "country": "Netherlands", "type": "university"},
    {"name": "University of Utrecht", "city": "Utrecht", "country": "Netherlands", "type": "university"},
    {"name": "Leiden University", "city": "Leiden", "country": "Netherlands", "type": "university"},
    {"name": "University of Groningen", "city": "Groningen", "country": "Netherlands", "type": "university"},
    {"name": "Erasmus University Rotterdam", "city": "Rotterdam", "country": "Netherlands", "type": "university"},
    
    # Belgium Universities
    {"name": "KU Leuven", "city": "Leuven", "country": "Belgium", "type": "university"},
    {"name": "Ghent University", "city": "Ghent", "country": "Belgium", "type": "university"},
    {"name": "Vrije Universiteit Brussel", "city": "Brussels", "country": "Belgium", "type": "university"},
    {"name": "University of Antwerp", "city": "Antwerp", "country": "Belgium", "type": "university"},
    {"name": "Université Libre de Bruxelles", "city": "Brussels", "country": "Belgium", "type": "university"},
    
    # Spain Universities
    {"name": "University of Barcelona", "city": "Barcelona", "country": "Spain", "type": "university"},
    {"name": "Autonomous University of Madrid", "city": "Madrid", "country": "Spain", "type": "university"},
    {"name": "University of Valencia", "city": "Valencia", "country": "Spain", "type": "university"},
    {"name": "University of Seville", "city": "Seville", "country": "Spain", "type": "university"},
    {"name": "Polytechnic University of Catalonia", "city": "Barcelona", "country": "Spain", "type": "university"},
    
    # Italy Universities
    {"name": "University of Bologna", "city": "Bologna", "country": "Italy", "type": "university"},
    {"name": "University of Milan", "city": "Milan", "country": "Italy", "type": "university"},
    {"name": "Sapienza University of Rome", "city": "Rome", "country": "Italy", "type": "university"},
    {"name": "University of Padua", "city": "Padua", "country": "Italy", "type": "university"},
    {"name": "University of Florence", "city": "Florence", "country": "Italy", "type": "university"},
    
    # Japan Universities
    {"name": "University of Tokyo", "city": "Tokyo", "country": "Japan", "type": "university"},
    {"name": "Kyoto University", "city": "Kyoto", "country": "Japan", "type": "university"},
    {"name": "Osaka University", "city": "Osaka", "country": "Japan", "type": "university"},
    {"name": "Tokyo Institute of Technology", "city": "Tokyo", "country": "Japan", "type": "university"},
    {"name": "Tohoku University", "city": "Sendai", "country": "Japan", "type": "university"},
    
    # China Universities
    {"name": "Tsinghua University", "city": "Beijing", "country": "China", "type": "university"},
    {"name": "Peking University", "city": "Beijing", "country": "China", "type": "university"},
    {"name": "Fudan University", "city": "Shanghai", "country": "China", "type": "university"},
    {"name": "Shanghai Jiao Tong University", "city": "Shanghai", "country": "China", "type": "university"},
    {"name": "Zhejiang University", "city": "Hangzhou", "country": "China", "type": "university"},
    
    # India Universities
    {"name": "Indian Institute of Technology Delhi", "city": "Delhi", "country": "India", "type": "university"},
    {"name": "Indian Institute of Technology Bombay", "city": "Mumbai", "country": "India", "type": "university"},
    {"name": "Delhi University", "city": "Delhi", "country": "India", "type": "university"},
    {"name": "Mumbai University", "city": "Mumbai", "country": "India", "type": "university"},
    {"name": "Bangalore University", "city": "Bangalore", "country": "India", "type": "university"},
    
    # Singapore Universities
    {"name": "National University of Singapore", "city": "Singapore", "country": "Singapore", "type": "university"},
    {"name": "Nanyang Technological University", "city": "Singapore", "country": "Singapore", "type": "university"},
    {"name": "Singapore Management University", "city": "Singapore", "country": "Singapore", "type": "university"},
    
    # South Korea Universities
    {"name": "Seoul National University", "city": "Seoul", "country": "South Korea", "type": "university"},
    {"name": "KAIST", "city": "Daejeon", "country": "South Korea", "type": "university"},
    {"name": "Yonsei University", "city": "Seoul", "country": "South Korea", "type": "university"},
    {"name": "Korea University", "city": "Seoul", "country": "South Korea", "type": "university"},
    
    # Brazil Universities
    {"name": "University of São Paulo", "city": "São Paulo", "country": "Brazil", "type": "university"},
    {"name": "Federal University of Rio de Janeiro", "city": "Rio de Janeiro", "country": "Brazil", "type": "university"},
    {"name": "Campinas State University", "city": "Campinas", "country": "Brazil", "type": "university"},
    
    # Mexico Universities
    {"name": "National Autonomous University of Mexico", "city": "Mexico City", "country": "Mexico", "type": "university"},
    {"name": "Monterrey Institute of Technology", "city": "Monterrey", "country": "Mexico", "type": "university"},
    
    # UAE Universities
    {"name": "United Arab Emirates University", "city": "Al Ain", "country": "UAE", "type": "university"},
    {"name": "American University of Sharjah", "city": "Sharjah", "country": "UAE", "type": "university"},
    
    # Additional European Universities
    {"name": "University of Vienna", "city": "Vienna", "country": "Austria", "type": "university"},
    {"name": "University of Copenhagen", "city": "Copenhagen", "country": "Denmark", "type": "university"},
    {"name": "University of Helsinki", "city": "Helsinki", "country": "Finland", "type": "university"},
    {"name": "University of Oslo", "city": "Oslo", "country": "Norway", "type": "university"},
    {"name": "University of Stockholm", "city": "Stockholm", "country": "Sweden", "type": "university"},
]

# Indian names and details
INDIAN_FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Arjun", "Rohan", "Priya", "Ananya", "Diya",
    "Neha", "Pooja", "Rajesh", "Amit", "Suresh", "Deepak", "Kavya", "Shreya",
    "Nikhil", "Akshay", "Varun", "Sanjay", "Anjali", "Divya", "Isha", "Riya"
]

INDIAN_LAST_NAMES = [
    "Sharma", "Patel", "Singh", "Kumar", "Gupta", "Verma", "Rao", "Nair",
    "Desai", "Iyer", "Reddy", "Bhat", "Menon", "Chopra", "Malhotra", "Saxena",
    "Joshi", "Mishra", "Pandey", "Tripathi", "Sinha", "Dutta", "Banerjee", "Ghosh"
]

# Foreign names
FOREIGN_FIRST_NAMES = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
    "Thomas", "Charles", "Emma", "Olivia", "Ava", "Isabella", "Sophia", "Mia",
    "Charlotte", "Amelia", "Harper", "Evelyn", "Jean", "Marie", "Pierre", "Luc",
    "Hans", "Klaus", "Maria", "Anna", "Sofia", "Marco", "Giovanni", "Carlos",
    "Juan", "Miguel", "Yuki", "Hiroshi", "Kenji", "Sakura", "Akira", "Lisa",
    "Sarah", "Jennifer", "Jessica", "Amanda", "Michelle", "Nicole", "Lauren", "Rachel",
    "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew",
    "Joshua", "Kenneth", "Kevin", "Brian", "George", "Edward", "Ronald", "Timothy"
]

FOREIGN_LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker",
    "Schulz", "Hoffmann", "Dupont", "Bernard", "Petit", "Durand", "Lefevre", "Moreau",
    "Rossi", "Russo", "Ferrari", "Esposito", "Bianchi", "Colombo", "Rizzo", "Marino",
    "Tanaka", "Suzuki", "Watanabe", "Nakamura", "Kobayashi", "Yamamoto", "Nakajima",
    "Ito", "Okada", "Hasegawa", "Mori", "Ishida", "Maeda", "Fujita", "Ogawa"
]

FOREIGN_COUNTRIES = [
    "USA", "UK", "Canada", "Australia", "Germany", "France", "Spain", "Italy",
    "Netherlands", "Belgium", "Switzerland", "Sweden", "Norway", "Denmark", "Finland",
    "Japan", "South Korea", "China", "Singapore", "Malaysia", "Thailand", "Vietnam",
    "Brazil", "Mexico", "Argentina", "Chile", "Colombia", "Peru", "New Zealand",
    "Austria", "Poland", "Czech Republic", "Portugal", "Greece", "Ireland", "UAE"
]

# Professional data
STREAMS = ["Science", "Commerce", "Arts", "Engineering", "Medical", "Law", "Business", "Technology"]
INDUSTRIES = ["Technology", "Finance", "Healthcare", "Education", "Retail", "Manufacturing",
              "Consulting", "Media", "Energy", "Telecommunications", "Real Estate", "Hospitality"]
ROLES = ["Software Engineer", "Data Analyst", "Product Manager", "Business Analyst",
         "Marketing Manager", "Sales Executive", "HR Manager", "Finance Manager",
         "Project Manager", "UX Designer", "DevOps Engineer", "QA Engineer"]
SKILLS = ["Python", "Java", "JavaScript", "SQL", "Machine Learning", "Data Analysis",
          "Project Management", "Communication", "Leadership", "Problem Solving",
          "Cloud Computing", "Agile", "Docker", "Kubernetes"]
GOALS = ["Career Advancement", "Skill Development", "Entrepreneurship", "Higher Education",
         "Work-Life Balance", "Industry Switch", "Leadership Development", "Technical Expertise"]

def generate_indian_user(user_id, user_type):
    """Generate an Indian user"""
    first_name = random.choice(INDIAN_FIRST_NAMES)
    last_name = random.choice(INDIAN_LAST_NAMES)
    name = f"{first_name} {last_name}"
    email = f"{user_id}@xexample.com"
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
    email = f"{user_id}@xexample.com"
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
        country = "India"
    else:
        country = random.choice(FOREIGN_COUNTRIES)
    
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
        city="City",
        state="State",
        country=country,
        postal_code=f"{random.randint(100000, 999999)}",
        school_college_name=random.choice(REAL_INSTITUTIONS)["name"],
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
        profile.school_name = random.choice(REAL_INSTITUTIONS)["name"]
        profile.school_board = "CBSE"
        profile.school_passing_year = str(random.randint(2024, 2026))
    elif who_am_i == "University Student":
        profile.institution_name = random.choice(REAL_INSTITUTIONS)["name"]
        profile.board_university = random.choice(REAL_INSTITUTIONS)["name"]
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
    
    profile = MentorProfile(
        user_id=user.id,
        profession=random.choice(ROLES),
        skills=", ".join(random.sample(SKILLS, 4)),
        role=random.choice(ROLES),
        industry_sector=random.choice(INDUSTRIES),
        organisation=f"{random.choice(['Tech', 'Global', 'Digital', 'Smart'])} Corp",
        years_of_experience=str(random.randint(5, 25)),
        whatsapp=f"+{random.randint(1, 99)}{random.randint(1000000000, 9999999999)}",
        location="City",
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
    print("🚀 Starting comprehensive dummy data generation...")
    
    with app.app_context():
        print("\n📚 Creating 100 Real Institutions...")
        institutions_created = 0
        for inst_data in REAL_INSTITUTIONS:
            existing = Institution.query.filter_by(name=inst_data["name"]).first()
            if not existing:
                institution = Institution(
                    name=inst_data["name"],
                    city=inst_data["city"],
                    country=inst_data["country"],
                    institution_type=inst_data["type"],
                    status="active"
                )
                db.session.add(institution)
                institutions_created += 1
        
        db.session.commit()
        print(f"✅ {institutions_created} institutions created/verified")
        
        print("\n👥 Generating 100 Mentees...")
        mentees = []
        for i in range(1, 101):
            user_id = f"mentee_{i}"
            if random.random() < 0.1:  # 10% Indian
                user = generate_indian_user(user_id, "2")
            else:
                user = generate_foreign_user(user_id, "2")
            
            db.session.add(user)
            db.session.flush()
            
            profile = generate_mentee_profile(user)
            db.session.add(profile)
            mentees.append(user)
            
            if i % 25 == 0:
                print(f"  ✓ Generated {i} mentees")
        
        print("\n👨‍🏫 Generating 100 Mentors...")
        mentors = []
        for i in range(1, 101):
            user_id = f"mentor_{i}"
            if random.random() < 0.1:  # 10% Indian
                user = generate_indian_user(user_id, "1")
            else:
                user = generate_foreign_user(user_id, "1")
            
            db.session.add(user)
            db.session.flush()
            
            profile = generate_mentor_profile(user)
            db.session.add(profile)
            mentors.append(user)
            
            if i % 25 == 0:
                print(f"  ✓ Generated {i} mentors")
        
        print("\n🏢 Generating 100 Institution Admins...")
        institutions_users = []
        for i in range(1, 101):
            user_id = f"institution_{i}"
            if random.random() < 0.1:  # 10% Indian
                user = generate_indian_user(user_id, "3")
            else:
                user = generate_foreign_user(user_id, "3")
            
            db.session.add(user)
            db.session.flush()
            institutions_users.append(user)
            
            if i % 25 == 0:
                print(f"  ✓ Generated {i} institution admins")
        
        print("\n💾 Committing all data to database...")
        db.session.commit()
        
        print("\n✅ Dummy data generation completed successfully!")
        print(f"\n📊 Summary:")
        print(f"   - Total Mentees: 100")
        print(f"   - Total Mentors: 100")
        print(f"   - Total Institution Admins: 100")
        print(f"   - Total Real Institutions: {institutions_created}")
        print(f"   - Total Users: 300")
        print(f"   - Indian Users: ~30 (10%)")
        print(f"   - Foreign Users: ~270 (90%)")
        print(f"\n🔐 Default Credentials:")
        print(f"   - Email format: userID@xexample.com")
        print(f"   - Password: Info@123")
        print(f"\n📧 Sample Emails:")
        print(f"   - mentee_1@xexample.com")
        print(f"   - mentor_1@xexample.com")
        print(f"   - institution_1@xexample.com")
        print(f"\n🌍 Institutions include:")
        print(f"   - 5 Luxembourg institutions")
        print(f"   - 15 USA universities")
        print(f"   - 10 UK universities")
        print(f"   - 5 Canada universities")
        print(f"   - 5 Australia universities")
        print(f"   - And 55+ more from around the world")

if __name__ == "__main__":
    try:
        generate_dummy_data()
    except Exception as e:
        print(f"❌ Error generating dummy data: {str(e)}")
        import traceback
        traceback.print_exc()
