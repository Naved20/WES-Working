import random
from faker import Faker
from werkzeug.security import generate_password_hash
from app import db, app, User, MentorProfile, MenteeProfile

# Create multiple Faker instances for different regions
fake_indian = Faker("en_IN")
fake_european = Faker("en_GB")  # For European names
fake_american = Faker("en_US")  # For American/international names

NUM_MENTORS = 100
NUM_MENTEES = 100
COMMON_PASSWORD = "Info@123"

# Expanded profession lists with medical and various fields
MEDICAL_PROFESSIONS = [
    "Doctor", "Surgeon", "Physician", "Pediatrician", "Cardiologist", 
    "Neurologist", "Psychiatrist", "Dentist", "Pharmacist", "Nurse",
    "Medical Researcher", "Healthcare Administrator", "Physiotherapist",
    "Radiologist", "Pathologist"
]

ENGINEERING_PROFESSIONS = [
    "Software Engineer", "Mechanical Engineer", "Civil Engineer", 
    "Electrical Engineer", "Chemical Engineer", "Aerospace Engineer",
    "Biomedical Engineer", "Environmental Engineer", "Data Scientist",
    "AI/ML Engineer"
]

BUSINESS_PROFESSIONS = [
    "Entrepreneur", "Business Consultant", "Marketing Manager",
    "Financial Analyst", "HR Manager", "Project Manager",
    "Sales Director", "Operations Manager", "Product Manager"
]

CREATIVE_PROFESSIONS = [
    "Graphic Designer", "UI/UX Designer", "Architect", "Artist",
    "Content Writer", "Video Editor", "Photographer", "Musician"
]

EDUCATION_PROFESSIONS = [
    "Professor", "Teacher", "Education Consultant", "Researcher",
    "Academic Coordinator", "School Principal", "Career Counselor"
]

OTHER_PROFESSIONS = [
    "Lawyer", "Scientist", "Government Officer", "Social Worker",
    "Environmentalist", "Journalist", "Chef", "Sports Coach"
]

ALL_PROFESSIONS = MEDICAL_PROFESSIONS + ENGINEERING_PROFESSIONS + BUSINESS_PROFESSIONS + CREATIVE_PROFESSIONS + EDUCATION_PROFESSIONS + OTHER_PROFESSIONS

# Enhanced locations with European focus and worldwide coverage
EUROPEAN_LOCATIONS = [
    "London", "Berlin", "Paris", "Madrid", "Rome", "Amsterdam",
    "Brussels", "Vienna", "Prague", "Warsaw", "Stockholm", "Oslo",
    "Copenhagen", "Helsinki", "Dublin", "Lisbon", "Athens", "Budapest",
    "Munich", "Milan", "Barcelona", "Zurich", "Geneva", "Lyon",
    "Edinburgh", "Manchester", "Hamburg", "Frankfurt", "Cologne",
    "Rotterdam", "Antwerp", "Luxembourg", "Bratislava", "Ljubljana"
]

WORLDWIDE_LOCATIONS = [
    "New York", "Los Angeles", "Toronto", "Sydney", "Melbourne",
    "Tokyo", "Singapore", "Hong Kong", "Dubai", "Abu Dhabi",
    "Mumbai", "Delhi", "Bangalore", "Shanghai", "Seoul",
    "Sao Paulo", "Mexico City", "Cairo", "Johannesburg", "Bangkok"
]

# Combine with European locations having more weight
LOCATIONS = EUROPEAN_LOCATIONS + WORLDWIDE_LOCATIONS

# Industry sectors
INDUSTRY_SECTORS = [
    "Healthcare", "IT", "Education", "Finance", "Manufacturing", 
    "Real Estate", "Entertainment", "Government", "Non-Profit",
    "Research & Development", "Consulting", "Retail", "Hospitality"
]

# Education backgrounds
EDUCATION_BACKGROUNDS = [
    "B.Tech", "M.Tech", "MBA", "PhD", "MBBS", "MD", "B.Sc", "M.Sc",
    "B.Com", "M.Com", "BA", "MA", "LLB", "LLM", "B.Arch", "M.Arch"
]

# Languages
LANGUAGES = ["English", "Hindi", "Spanish", "French", "German", "Japanese", 
            "Chinese", "Arabic", "Portuguese", "Russian", "Italian"]

# Streams for mentees
STREAMS = [
    "Science", "Commerce", "Arts", "Engineering", "Medical", 
    "Law", "Architecture", "Design", "Management", "Humanities"
]

def get_random_name():
    """Return random name from different regions"""
    return random.choice([
        fake_indian.name(),
        fake_european.name(),
        fake_american.name()
    ])

def get_random_profession():
    """Return random profession with weighted probability for medical fields"""
    # Give slightly higher weight to medical professions
    weights = [2] * len(MEDICAL_PROFESSIONS) + [1] * (len(ALL_PROFESSIONS) - len(MEDICAL_PROFESSIONS))
    return random.choices(ALL_PROFESSIONS, weights=weights)[0]

def get_random_skills(profession):
    """Generate relevant skills based on profession"""
    skill_sets = {
        "medical": ["Patient Care", "Medical Diagnosis", "Clinical Research", "Healthcare Management", "Emergency Response"],
        "engineering": ["Programming", "Problem Solving", "Data Analysis", "Project Management", "Technical Design"],
        "business": ["Strategic Planning", "Financial Analysis", "Marketing", "Leadership", "Negotiation"],
        "creative": ["Design Thinking", "Creativity", "Visual Communication", "Storytelling", "Brand Development"],
        "education": ["Teaching", "Curriculum Development", "Student Counseling", "Educational Technology", "Assessment"],
        "other": ["Communication", "Research", "Analysis", "Planning", "Coordination"]
    }
    
    if any(med in profession for med in MEDICAL_PROFESSIONS):
        base_skills = skill_sets["medical"]
    elif any(eng in profession for eng in ENGINEERING_PROFESSIONS):
        base_skills = skill_sets["engineering"]
    elif any(bus in profession for bus in BUSINESS_PROFESSIONS):
        base_skills = skill_sets["business"]
    elif any(cre in profession for cre in CREATIVE_PROFESSIONS):
        base_skills = skill_sets["creative"]
    elif any(edu in profession for edu in EDUCATION_PROFESSIONS):
        base_skills = skill_sets["education"]
    else:
        base_skills = skill_sets["other"]
    
    return ", ".join(random.sample(base_skills, 3) + fake_indian.words(nb=2))

with app.app_context():
    # DON'T clear existing data - only add new data
    print("✅ Starting dummy data generation...")

    # ---------------- ADD MENTORS ----------------
    for i in range(NUM_MENTORS):
        name = get_random_name()
        email = f"mentor0{i}@example.com"
        hashed_pw = generate_password_hash(COMMON_PASSWORD)

        # Create user
        user = User(name=name, email=email, password=hashed_pw, user_type="1")
        db.session.add(user)
        db.session.flush()

        profession = get_random_profession()
        skills = get_random_skills(profession)

        # Create mentor profile
        mentor = MentorProfile(
            user_id=user.id,
            profession=profession,
            skills=skills,
            role=profession,  # Use profession as role
            industry_sector=random.choice(INDUSTRY_SECTORS),
            organisation=fake_indian.company(),
            years_of_experience=str(random.randint(1, 30)),
            whatsapp=fake_indian.phone_number(),
            location=random.choice(LOCATIONS),  # Now uses worldwide locations with European focus
            education=random.choice(EDUCATION_BACKGROUNDS),
            language=", ".join(random.sample(LANGUAGES, random.randint(1, 3))),
            linkedin_link=f"https://linkedin.com/in/{name.replace(' ', '').lower()}",
            github_link=f"https://github.com/{name.split()[0].lower()}",
            portfolio_link=f"https://portfolio-{name.split()[0].lower()}.com",
            mentorship_topics=", ".join(random.sample([
                "Career Guidance", "Skill Development", "Industry Insights", 
                "Interview Preparation", "Leadership", "Research Methodology",
                "Clinical Practice", "Technology Trends", "Business Strategy"
            ], 3)),
            mentorship_type_preference=random.choice(["School Students", "College Students", "Working Professionals", "Women", "All"]),
            preferred_communication=random.choice(["Online", "Offline", "Hybrid"]),
            availability=random.choice(["Weekdays", "Weekends", "Flexible"]),
            connect_frequency=random.choice(["Weekly", "Bi-weekly", "Monthly"]),
            preferred_duration=random.choice(["1 month", "3 months", "6 months", "1 year"]),
            why_mentor=fake_indian.text(80),
            mentorship_philosophy=fake_indian.text(50),
            mentorship_motto=fake_indian.sentence(),
            additional_info=fake_indian.text(40),
            status="approved"
        )

        db.session.add(mentor)

    print(f"👨‍🏫 {NUM_MENTORS} mentors added successfully!")

    # ---------------- ADD MENTEES ----------------
    for i in range(NUM_MENTEES):
        name = get_random_name()
        email = f"mentee0{i}@example.com"
        hashed_pw = generate_password_hash(COMMON_PASSWORD)

        # Create user
        user = User(name=name, email=email, password=hashed_pw, user_type="2")
        db.session.add(user)
        db.session.flush()

        stream = random.choice(STREAMS)
        
        # Create mentee profile
        mentee = MenteeProfile(
            user_id=user.id,
            dob=str(fake_indian.date_of_birth(minimum_age=16, maximum_age=25)),
            school_college_name=random.choice([
                "IIT Delhi", "IIT Bombay", "AIIMS Delhi", "Harvard University", 
                "Stanford University", "MIT", "University of Oxford", "Cambridge University",
                "NIT Bhopal", "RGPV", "LNCT", "Delhi University", "Mumbai University"
            ]),
            mobile_number=fake_indian.phone_number(),
            whatsapp_number=fake_indian.phone_number(),
            govt_private=random.choice(["Government", "Private", "Semi-Government"]),
            stream=stream,
            class_year=random.choice(["1st Year", "2nd Year", "3rd Year", "Final Year", "Postgraduate"]),
            favourite_subject=random.choice([
                "Mathematics", "Physics", "Chemistry", "Biology", "Computer Science", 
                "Economics", "Psychology", "Literature", "History", "Business Studies"
            ]),
            goal=random.choice([
                "Become a Doctor", "Become an Engineer", "Crack UPSC", "Start my own business",
                "Work in a top tech company", "Become a Researcher", "Study Abroad",
                "Become a Lawyer", "Work in Healthcare", "Become an Entrepreneur"
            ]),
            parent_name=get_random_name(),
            parent_mobile=fake_indian.phone_number(),
            comments=fake_indian.sentence(),
            terms_agreement="Yes",
            status="approved"
        )

        db.session.add(mentee)

    db.session.commit()
    print(f"🎓 {NUM_MENTEES} mentees added successfully!")

    print("\n🎉 Dummy data generation completed successfully!")
    print(f"🔑 All users' password: {COMMON_PASSWORD}")
    print(f"🌍 Locations include: European cities (London, Paris, Berlin, etc.) and worldwide locations")
    print(f"👥 Names from: Indian, European, American regions")
    print(f"🏢 Industries: {', '.join(random.sample(INDUSTRY_SECTORS, 5))}...")