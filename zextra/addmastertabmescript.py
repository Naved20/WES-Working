# create_mastertask_data.py
from app import db, MasterTask, app
from datetime import datetime

def add_mentorship_journey_data():
    mentorship_data = [
        {
            'meeting_number': 1,
            'month': '1',
            'journey_phase': 'Getting to Know Each Other',
            'purpose_of_call': 'Ice-breaking, set comfort level',
            'mentor_focus': 'Build rapport, understand background\n\n1.Share your work and family situation',
            'mentee_focus': 'Share life story, interests, dreams\n\n1. Share your family situation, school status, hobbies, interests\n2. What\'s something you enjoy doing outside of school/work?\n3. Who has influenced you most in your life so far?',
            'program_incharge_actions': 'Ensure mentor & mentee profiles are exchanged, added in the whatsapp group',
            'meeting_plan_overview': 'This meeting will be for getting to know each other, and the purpose of the call will be to break the ice and set a comfort level between the mentor and mentee. The mentor will be focusing on building rapport, understanding the mentee\'s background, and sharing about their own work and family to connect better. The mentee will be focusing on sharing their life story, interests, and dreams in detail — including their family situation, school status, hobbies, and interests. The mentee will also be sharing what they enjoy doing outside of school or work, and who has influenced them the most in their life so far. The program in-charge will be ensuring that mentor and mentee profiles are exchanged and that both are added to the official WhatsApp group before the meeting.'
        },
        {
            'meeting_number': 2,
            'month': '1',
            'journey_phase': 'Mentor Storytelling',
            'purpose_of_call': 'Inspiration through storytelling',
            'mentor_focus': 'Share own career struggles & lessons\n\n1. Have you ever faced a big setback, and how did you deal with it?\n2. If you could redo or change one decision in your career, what would it be?\n3. What small habit helped you succeed the most?',
            'mentee_focus': 'Reflect on personal challenges\n\n1. Have you ever felt unmotivated?\n2. Is there a thing that you really wanted to happen in your life, but it didn\'t?',
            'program_incharge_actions': 'Collect short mentor reflection',
            'meeting_plan_overview': 'This meeting will be focusing on inspiration through storytelling. The mentor will be sharing their own career struggles and lessons — including times they faced setbacks, what they might change if they could redo a decision, and which small habits helped them succeed. The mentee will be reflecting on personal challenges, such as moments when they felt unmotivated or when something they deeply wanted did not happen. The program in-charge will be collecting short mentor reflections after the call.'
        },
        {
            'meeting_number': 3,
            'month': '2',
            'journey_phase': 'Academic Baseline',
            'purpose_of_call': 'Initial academic assessment',
            'mentor_focus': 'Ask about academic standing & challenges\n\n1. Which subjects do you feel confident in, and which feel harder?\n2. How do you usually prepare for exams or assignments?\n3. Do you have someone supporting your studies at home?',
            'mentee_focus': 'Discuss current studies & issues\n\n1. Do you find any subjects in school difficult? If yes, ask for any tips for improving?\n2. How do you manage when you have too many assignments?\n3. What\'s the best way to ask for help from teachers?',
            'program_incharge_actions': 'Collect mentee\'s report card/marksheet',
            'meeting_plan_overview': 'This meeting will be focusing on understanding the mentee\'s academic baseline. The mentor will be asking about the mentee\'s academic standing, confidence levels in different subjects, exam preparation styles, and available support at home. The mentee will be discussing their current studies, sharing which subjects feel difficult, and asking for tips to improve. The mentee will also be talking about how they manage multiple assignments and how they seek help from teachers. The program in-charge will be collecting the mentee\'s report card or marksheet.'
        },
        {
            'meeting_number': 4,
            'month': '2',
            'journey_phase': 'Dream Mapping',
            'purpose_of_call': 'Map initial aspirations',
            'mentor_focus': 'Explore career aspirations\nInquire from mentee:\n1. What is their dream future, how does it look like?\n2. Who are their role models and why?\n3. What careers have they thought about?',
            'mentee_focus': 'Express dream careers, role models\nThink about and share:\n1. What skills should you develop to reach my dream job?\n2. Ask mentor how did they discover their own career path?',
            'program_incharge_actions': 'Record mentee\'s career preference',
            'meeting_plan_overview': 'This meeting will be focusing on mapping the mentee\'s initial dreams and aspirations. The mentor will be exploring the mentee\'s dream future, their role models, and the careers they have thought about. The mentee will be expressing their dream careers and role models, thinking about what skills they should develop to reach their dream job, and asking how the mentor discovered their own career path. The program in-charge will be recording the mentee\'s career preferences shared during the session.'
        },
        {
            'meeting_number': 5,
            'month': '3',
            'journey_phase': 'Dream Prioritization',
            'purpose_of_call': 'Link studies with future',
            'mentor_focus': 'Align academic subjects with career paths\nInquire from mentee:\n1. Which subjects connect most with your dream careers?\n2. If you had to choose one dream to focus on now, which would it be?\n3. What do you think is realistic for the next 5 years?',
            'mentee_focus': 'Ask doubts about career entry\nDiscuss with your mentee:\n1. How do I prioritize? \n2. Can I combine more than one passion into my future career?\n3. Which steps should I take now to prepare?',
            'program_incharge_actions': 'Make sure that mentee fills the career info sheet based on mentor guidance.',
            'meeting_plan_overview': 'This meeting will be focusing on linking studies with future goals. The mentor will be helping the mentee align academic subjects with career paths and discuss which subjects connect most with their dream careers, what feels realistic in the next five years, and how to focus on one goal. The mentee will be asking doubts about prioritizing dreams, combining passions, and planning practical next steps. The program in-charge will be ensuring the mentee fills the career information sheet based on mentor guidance.'
        },
        {
            'meeting_number': 6,
            'month': '3',
            'journey_phase': 'Goal Planning',
            'purpose_of_call': 'Goal-setting foundation',
            'mentor_focus': 'Help set 3 short-term academic goals\n1. What\'s one small goal you can achieve in the next 4 weeks?\n2. How will you know you\'ve succeeded?\n3. What are 2 more goals that can be achieved afterwards as a next step?',
            'mentee_focus': 'Set small learning targets\n\n1. How many goals should I focus on at one time?\n2. How do I stay motivated if I don\'t see results quickly?\n3. What should I do if I fail to reach a goal?\n4. Which steps exactly I need to take to reach my goal?',
            'program_incharge_actions': 'Approve mentee\'s monthly plan',
            'meeting_plan_overview': 'This meeting will be focusing on setting short-term academic goals. The mentor will be guiding the mentee to identify three achievable goals — discussing how to measure progress and maintain motivation. The mentee will be setting small learning targets, reflecting on how to stay consistent, manage failure, and take practical steps to reach each goal. The program in-charge will be approving the mentee\'s monthly plan after review.'
        },
        {
            'meeting_number': 7,
            'month': '4',
            'journey_phase': 'Pathways & Opportunities',
            'purpose_of_call': 'Introduce scholarships & exams',
            'mentor_focus': 'Explain higher education opportunities\n\n1. Have you thought about higher studies or scholarships?\n2. Do you know what exams are required for your career?\n3. Are finances a worry for your future?',
            'mentee_focus': 'Ask about financial concerns\n\n1. Ask about exams and scholarships and certificates needed for the chosen career\n2. How can I find or research for less known certificates or opportunities?',
            'program_incharge_actions': 'Share scholarship list with mentor',
            'meeting_plan_overview': 'This meeting will be focusing on introducing higher education opportunities, scholarships, and exams. The mentor will be explaining different pathways, required exams, and addressing financial concerns. The mentee will be asking questions about scholarships, certificates, and career-related qualifications. The program in-charge will be sharing a scholarship list and resources with the mentor before the call.'
        },
        {
            'meeting_number': 8,
            'month': '4',
            'journey_phase': 'English & Confidence',
            'purpose_of_call': 'Start soft skills journey',
            'mentor_focus': 'Suggest English & communication tasks\n1. Do you enjoy reading, writing, or speaking English more?\n2. What situations make you most nervous speaking English?\n3. Suggest daily practice activities to the mentee',
            'mentee_focus': 'Start daily English practice\n\n1. What\'s the easiest way to improve vocabulary?',
            'program_incharge_actions': 'Provide reading/writing log',
            'meeting_plan_overview': 'This meeting will be focusing on developing English and communication skills. The mentor will be suggesting daily reading, writing, and speaking activities, and identifying what situations make the mentee most nervous. The mentee will be starting regular English practice and working on improving vocabulary and confidence. The program in-charge will be providing a reading and writing log to both participants.'
        },
        {
            'meeting_number': 9,
            'month': '5',
            'journey_phase': 'Study Habits',
            'purpose_of_call': 'Productivity session',
            'mentor_focus': 'Guide on time management & study planning\n\n1. What does your typical study day look like?\n2. Do you find it easy to focus, or do you get distracted?\n3. Which time of day are you most productive?',
            'mentee_focus': 'Share daily routine\n\n1. How many hours should I ideally study daily?\n2. What\'s the best way to manage time with distractions?\n3. Ask your mentor for their own study routine from when they were a student',
            'program_incharge_actions': 'Collect routine tracker',
            'meeting_plan_overview': 'This meeting will be focusing on improving study habits and productivity. The mentor will be guiding the mentee on time management, focus, and planning study schedules. The mentee will be sharing their daily routine, discussing distractions, and asking for advice on managing time effectively. The program in-charge will be collecting the mentee\'s routine tracker for review.'
        },
        {
            'meeting_number': 10,
            'month': '5',
            'journey_phase': 'First Progress Review',
            'purpose_of_call': 'Check growth since last calls',
            'mentor_focus': 'Review progress of tasks and goals\n\n1. Which small goals were easier/harder than expected?\n2. How do you feel about your growth so far?',
            'mentee_focus': 'Present small improvement\n\n1. Do you think I\'m on track?\n2. What should I adjust in my approach?',
            'program_incharge_actions': 'Collect progress sheet',
            'meeting_plan_overview': 'This meeting will be focusing on reviewing progress since the previous sessions. The mentor will be evaluating which goals were easy or difficult and helping the mentee reflect on their growth. The mentee will be presenting small improvements and asking for feedback on their progress. The program in-charge will be collecting the progress sheet from both sides.'
        },
        {
            'meeting_number': 11,
            'month': '6',
            'journey_phase': 'New Skills',
            'purpose_of_call': 'Skill exposure session',
            'mentor_focus': 'Introduce practical skills (IT/coding, etc.)\n\n1. Have you ever tried coding, design, or another practical skill?\n2. What excites you more—technical skills or creative skills?',
            'mentee_focus': 'Try simple tasks, ask doubts\n\n1. Which skills will be most valuable for the future?\n2. Can I learn new skills for free online?',
            'program_incharge_actions': 'Share small project template',
            'meeting_plan_overview': 'This meeting will be focusing on exploring new and practical skills. The mentor will be introducing topics like coding, design, or creative skills and discussing what excites the mentee more. The mentee will be trying simple tasks, asking doubts, and identifying which new skills could benefit their future. The program in-charge will be sharing a small project template for practice.'
        },
        {
            'meeting_number': 12,
            'month': '6',
            'journey_phase': 'Career Deep Dive',
            'purpose_of_call': 'Build advanced clarity',
            'mentor_focus': 'Provide deeper career-specific guidance\n\n1. Which career paths interest you the most now?\n2. Share anything you know about this career with the mentee',
            'mentee_focus': 'Ask specific questions\n\n1. How does a working day in this career look like?\n2. What skills are absolutely necessary?',
            'program_incharge_actions': 'Provide resource kits (per career)',
            'meeting_plan_overview': 'This meeting will be focusing on deepening career clarity. The mentor will be guiding the mentee through specific career paths, sharing information about working days, roles, and required skills. The mentee will be asking focused questions to understand the field better. The program in-charge will be providing resource kits related to each career option.'
        },
        {
            'meeting_number': 13,
            'month': '7',
            'journey_phase': 'Midpoint Review',
            'purpose_of_call': 'Halfway checkpoint',
            'mentor_focus': 'Mid-program reflection\n\n1. How has this mentorship helped you so far?\n2. What\'s one thing you\'ve learned that surprised you?\n3. Where do you feel you need more support?',
            'mentee_focus': 'Share learning so far\n\n1. What progress do you think I have?\n2. What should I focus on in the next half of the program?',
            'program_incharge_actions': 'Prepare evaluation sheet',
            'meeting_plan_overview': 'This meeting will be focusing on reviewing the mentorship journey so far. The mentor will be helping the mentee reflect on what they have learned, what surprised them, and where they need more support. The mentee will be sharing their own reflections on progress and setting focus areas for the next half. The program in-charge will be preparing and collecting the evaluation sheet.'
        },
        {
            'meeting_number': 14,
            'month': '7',
            'journey_phase': 'Motivation & Resilience',
            'purpose_of_call': 'Build resilience',
            'mentor_focus': 'Share motivational stories of success\n\n1. Share a story of resilience (yours or someone else\'s) that has always inspired you?\n2. Share how you personally stay motivated during tough times\n3. Is it important sometimes to also fail in life?',
            'mentee_focus': 'Reflect on challenges\n\n1. Share a challenge from your life that maybe you even failed; and discuss with your mentor what you could have done better',
            'program_incharge_actions': 'Collect mentee reflections',
            'meeting_plan_overview': 'This meeting will be focusing on building resilience and motivation. The mentor will be sharing inspiring stories of success and explaining the importance of failure in growth. The mentee will be reflecting on their own challenges and discussing what could have been done better in past situations. The program in-charge will be collecting mentee reflections.'
        },
        {
            'meeting_number': 15,
            'month': '8',
            'journey_phase': 'Professional Exposure',
            'purpose_of_call': 'Exposure to real-world links',
            'mentor_focus': 'Mentor shares network/resources\n\n1. Explain how professional networking works\n2. Try to connect your mentee with someone from the field with this exact profession',
            'mentee_focus': 'Learn about professional world\n\n1. How do I approach professionals without being nervous?\n2. Can you share what workplaces expect from beginners?\n3. Ask what is networking and how to become better in it',
            'program_incharge_actions': 'Record external connections made',
            'meeting_plan_overview': 'This meeting will be focusing on exposure to the professional world. The mentor will be sharing their network and explaining how professional connections work, possibly introducing the mentee to someone from their field. The mentee will be learning how to approach professionals, what workplaces expect, and how to build networking skills. The program in-charge will be recording external connections made during or after the session.'
        },
        {
            'meeting_number': 16,
            'month': '8',
            'journey_phase': 'Project Assignment',
            'purpose_of_call': 'Hands-on growth',
            'mentor_focus': 'Assign project/presentation',
            'mentee_focus': 'Prepare & present project',
            'program_incharge_actions': 'Approve project themes',
            'meeting_plan_overview': 'This meeting will be focusing on assigning a practical project or presentation. The mentor will be helping select a project theme and setting expectations. The mentee will be preparing and presenting their project idea. The program in-charge will be approving final project themes.'
        },
        {
            'meeting_number': 17,
            'month': '9',
            'journey_phase': 'Project Review',
            'purpose_of_call': 'Ongoing evaluation',
            'mentor_focus': 'Review project progress',
            'mentee_focus': 'Show partial work',
            'program_incharge_actions': 'Monitor mentor-mentee project',
            'meeting_plan_overview': 'This meeting will be focusing on reviewing ongoing project progress. The mentor will be giving feedback and supporting improvements. The mentee will be showing partial work and sharing challenges. The program in-charge will be monitoring project status and coordination between mentor and mentee.'
        },
        {
            'meeting_number': 18,
            'month': '9',
            'journey_phase': 'Exam/Interview Preparation',
            'purpose_of_call': 'Exam/Interview readiness',
            'mentor_focus': 'Guide on exam/interview prep/competitive tests\n\n1. Share everything you do to prepare for an interview\n2. Share typical questions you have been asked during interviews (personal and technical)\n3. Share different details on what are the usual steps of an interview process',
            'mentee_focus': 'Ask doubts on interview of entrance exams\n\n1. What are common questions that are asked during an interview?\n2. Can you share common mistakes to avoid?',
            'program_incharge_actions': 'Provide sample exam papers',
            'meeting_plan_overview': 'This meeting will be focusing on preparing for exams or interviews. The mentor will be guiding the mentee through preparation methods, sharing common questions, mistakes to avoid, and steps in the process. The mentee will be asking practical doubts about interviews and entrance exams. The program in-charge will be providing sample exam papers or mock questions.'
        },
        {
            'meeting_number': 19,
            'month': '10',
            'journey_phase': 'Final Review',
            'purpose_of_call': 'Document growth',
            'mentor_focus': 'Review entire mentorship journey\n\n1. Looking back, what\'s the biggest change you see in yourself?\n2. What goals did you achieve that you\'re most proud of?\n3. What unfinished goals do you still want to work on?',
            'mentee_focus': 'Share highlights & struggles\n\n1. How do you think I\'ve grown since we started?\n2. What should I continue working on after the program?',
            'program_incharge_actions': 'Prepare impact report',
            'meeting_plan_overview': 'This meeting will be focusing on reflecting on the entire mentorship journey. The mentor will be reviewing the mentee\'s growth, achievements, and unfinished goals. The mentee will be sharing their highlights, struggles, and areas they want to keep improving. The program in-charge will be preparing the final impact report.'
        },
        {
            'meeting_number': 20,
            'month': '10',
            'journey_phase': 'Graduation Call',
            'purpose_of_call': 'Closure & future commitment',
            'mentor_focus': 'Celebrate achievements, close formally',
            'mentee_focus': 'Express gratitude, share next steps',
            'program_incharge_actions': 'Organize certificate/recognition',
            'meeting_plan_overview': 'This meeting will be focusing on celebrating the mentorship journey and formally closing the program. The mentor will be acknowledging the mentee\'s progress and sharing future guidance. The mentee will be expressing gratitude and outlining their next steps after the program. The program in-charge will be organizing certificates and recognition for completion.'
        }
    ]

    with app.app_context():
        # Clear existing data (optional)
        MasterTask.query.delete()
        
        # Add all meetings
        for meeting_data in mentorship_data:
            meeting = MasterTask(**meeting_data)
            db.session.add(meeting)
        
        db.session.commit()
        print(f'✅ Successfully added {len(mentorship_data)} mentorship meetings to MasterTask table!')

if __name__ == '__main__':
    add_mentorship_journey_data()