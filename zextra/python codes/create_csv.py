import csv

# Create the CSV data
csv_data = [
    ["full_name", "email", "profile_picture", "profession", "other_profession", "skills", "role", "industry_sector", "other_industry_sector", "organisation", "years_of_experience", "institution", "other_institution_name", "whatsapp_country_code", "whatsapp", "country", "other_country", "city", "language", "other_language", "highest_qualification", "degree_name", "field_of_study", "university_name", "graduation_year", "academic_status", "certifications", "research_work", "linkedin_link", "github_link", "portfolio_link", "other_social_link", "mentorship_topics", "mentorship_type_preference", "preferred_communication", "availability", "connect_frequency", "preferred_duration", "why_mentor", "mentorship_philosophy", "mentorship_motto", "additional_info", "criminal_certificate"],
    ["Rahul Sharma", "rahul@example.com", "rahul_profile.jpg", "Software Engineer", "", "Python, Django, React, AWS", "Senior Software Engineer", "Technology", "", "Tech Solutions Inc.", "6-10", "Self", "", "+91", "9876543210", "India", "", "Mumbai", "Hindi, English", "", "Master's", "M.Tech", "Computer Science", "IIT Bombay", "2015", "Completed", "AWS Certified, PMP", "Machine Learning Algorithms", "https://linkedin.com/in/rahulsharma", "https://github.com/rahulsharma", "https://rahulportfolio.com", "", "Career Guidance, Programming", "College Students, Early Professionals", "Online", "Weekends", "Monthly", "3 months", "To give back to community", "Student-centered approach", "Empower through guidance", "Experienced in mentoring juniors", "criminal_cert_rahul.pdf"]
]

# Write to CSV file
with open('mentors_data.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows(csv_data)

print("CSV file 'mentors_data.csv' created successfully!")