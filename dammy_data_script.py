import random
from faker import Faker
from werkzeug.security import generate_password_hash
from app import db, app, User, MentorProfile, MenteeProfile

fake = Faker("en_IN")

NUM_MENTORS = 100
NUM_MENTEES = 100
COMMON_PASSWORD = "Info@123"

with app.app_context():
    # Optional: Clear existing data
    db.drop_all()
    db.create_all()
    print("✅ Database reset successfully.")

    # ---------------- ADD MENTORS ----------------
    for i in range(NUM_MENTORS):
        name = fake.name()
        email = f"mentor{i}@example.com"
        hashed_pw = generate_password_hash(COMMON_PASSWORD)

        # Create user
        user = User(name=name, email=email, password=hashed_pw, user_type="1")
        db.session.add(user)
        db.session.flush()

        # Create mentor profile
        mentor = MentorProfile(
            user_id=user.id,
            profession=random.choice(["Engineer", "Teacher", "Developer", "Entrepreneur", "Designer"]),
            skills=", ".join(fake.words(nb=4)),
            role=random.choice(["Software Engineer", "Project Manager", "UI/UX Designer", "Educator"]),
            industry_sector=random.choice(["IT", "Education", "Design", "Business", "Healthcare"]),
            organisation=fake.company(),
            years_of_experience=str(random.randint(1, 20)),
            whatsapp=fake.phone_number(),
            location=random.choice(["Delhi", "Bhopal", "Mumbai", "Indore", "Pune"]),
            education=random.choice(["B.Tech", "M.Tech", "MBA", "PhD"]),
            language=", ".join(random.sample(["English", "Hindi", "Marathi", "Gujarati"], 2)),
            linkedin_link=f"https://linkedin.com/in/{name.replace(' ', '').lower()}",
            github_link=f"https://github.com/{name.split()[0].lower()}",
            portfolio_link=f"https://portfolio-{name.split()[0].lower()}.com",
            mentorship_topics=", ".join(random.sample(["Leadership", "Career Growth", "Coding", "Communication"], 3)),
            mentorship_type_preference=random.choice(["School Students", "College Students", "Women"]),
            preferred_communication=random.choice(["Online", "Offline", "Hybrid"]),
            availability=random.choice(["Weekdays", "Weekends"]),
            connect_frequency=random.choice(["Weekly", "Monthly"]),
            preferred_duration=random.choice(["1 month", "3 months", "6 months"]),
            why_mentor=fake.text(80),
            mentorship_philosophy=fake.text(50),
            mentorship_motto=fake.sentence(),
            additional_info=fake.text(40),
            status="approved"
        )

        db.session.add(mentor)

    print(f"👨‍🏫 {NUM_MENTORS} mentors added successfully!")

    # ---------------- ADD MENTEES ----------------
    for i in range(NUM_MENTEES):
        name = fake.name()
        email = f"mentee{i}@example.com"
        hashed_pw = generate_password_hash(COMMON_PASSWORD)

        # Create user
        user = User(name=name, email=email, password=hashed_pw, user_type="2")
        db.session.add(user)
        db.session.flush()

        # Create mentee profile
        mentee = MenteeProfile(
            user_id=user.id,
            dob=str(fake.date_of_birth(minimum_age=17, maximum_age=24)),
            school_college_name=random.choice(["IIT Delhi", "IIT Bombay", "NIT Bhopal", "RGPV", "LNCT"]),
            mobile_number=fake.phone_number(),
            whatsapp_number=fake.phone_number(),
            govt_private=random.choice(["Government", "Private"]),
            stream=random.choice(["Science", "Commerce", "Arts", "Engineering"]),
            class_year=random.choice(["1st Year", "2nd Year", "3rd Year", "Final Year"]),
            favourite_subject=random.choice(["Maths", "Physics", "Computer Science", "Economics"]),
            goal=random.choice([
                "Become a Data Scientist",
                "Get into IIT",
                "Crack UPSC",
                "Start my own business",
                "Work in a top tech company"
            ]),
            parent_name=fake.name(),
            parent_mobile=fake.phone_number(),
            comments=fake.sentence(),
            terms_agreement="Yes",
            status="approved"
        )

        db.session.add(mentee)

    db.session.commit()
    print(f"🎓 {NUM_MENTEES} mentees added successfully!")

    print("\n🎉 Dummy data generation completed successfully!")
    print(f"🔑 All users' password: {COMMON_PASSWORD}")