# Dummy Data - Quick Start Guide ✅

## What Was Created

✅ **100 Mentees** - Complete profiles with all details
✅ **100 Mentors** - Professional profiles with experience
✅ **100 Institution Admins** - Ready to manage institutions
✅ **105 Real Institutions** - Major universities and colleges worldwide
✅ **10% Indian Users** - Indian names and nationalities
✅ **90% Foreign Users** - International names and nationalities

---

## Login Credentials

### Format
```
Email: userID@xexample.com
Password: Info@123
```

### Examples

**Mentees:**
- mentee_1@xexample.com
- mentee_50@xexample.com
- mentee_100@xexample.com

**Mentors:**
- mentor_1@xexample.com
- mentor_50@xexample.com
- mentor_100@xexample.com

**Institution Admins:**
- institution_1@xexample.com
- institution_50@xexample.com
- institution_100@xexample.com

---

## Institutions Included

### By Country

| Country | Count | Examples |
|---------|-------|----------|
| Luxembourg | 5 | University of Luxembourg, Lycée de Garçons |
| USA | 15 | Harvard, Stanford, MIT, Yale, Princeton |
| UK | 10 | Oxford, Cambridge, Imperial College London |
| Germany | 5 | Heidelberg, TU Munich, Humboldt |
| France | 5 | Sorbonne, PSL, University of Lyon |
| Canada | 5 | Toronto, McGill, UBC |
| Australia | 5 | Melbourne, Sydney, ANU |
| Japan | 5 | Tokyo, Kyoto, Osaka |
| China | 5 | Tsinghua, Peking, Fudan |
| India | 5 | IIT Delhi, IIT Bombay, Delhi University |
| And 30+ more countries | 40+ | Various universities worldwide |

---

## User Distribution

### By Type
- Mentees: 100 (user_type = "2")
- Mentors: 100 (user_type = "1")
- Institution Admins: 100 (user_type = "3")

### By Nationality
- Indian: ~30 (10%)
- Foreign: ~270 (90%)

### By Gender (Names)
- Mix of male and female names
- Realistic international representation

---

## What Each User Has

### Mentee Profile Includes
- Full name
- Email address
- Date of birth
- Country
- Category (School Student, University Student, Professional, etc.)
- Contact information
- Educational details
- Career goals
- Mentorship expectations

### Mentor Profile Includes
- Full name
- Email address
- Professional role
- Industry sector
- Years of experience
- Skills
- Education level
- Mentorship topics
- Availability
- Communication preferences

### Institution Admin Profile Includes
- Full name
- Email address
- User type (Institution)
- Can manage institution

---

## Testing Scenarios

### Scenario 1: Mentee Login
```
1. Go to login page
2. Enter: mentee_1@xexample.com
3. Password: Info@123
4. Click Sign In
5. View available mentors
6. Search for mentors
7. Send mentorship request
```

### Scenario 2: Mentor Login
```
1. Go to login page
2. Enter: mentor_1@xexample.com
3. Password: Info@123
4. Click Sign In
5. View available mentees
6. Accept/reject requests
7. View mentee profiles
```

### Scenario 3: Institution Admin Login
```
1. Go to login page
2. Enter: institution_1@xexample.com
3. Password: Info@123
4. Click Sign In
5. View institution mentors
6. View institution mentees
7. Manage mentorships
```

---

## Database Stats

```
Total Users: 300 (new)
Total Institutions: 105
Total Mentee Profiles: 100
Total Mentor Profiles: 100
Total Institution Admins: 100
```

---

## File Information

### Script File
- **Name**: `generate_comprehensive_dummy_data.py`
- **Size**: ~50KB
- **Execution Time**: ~7 seconds
- **Status**: ✅ Already executed

### Data Locations
- **Database**: `instance/mentors_connect.db`
- **Users Table**: `signup_details`
- **Mentee Profiles**: `mentee_profile`
- **Mentor Profiles**: `mentor_profile`
- **Institutions**: `institutions`

---

## Quick Commands

### Verify Data
```bash
python -c "
from app import app, User
with app.app_context():
    print(f'Total Users: {User.query.count()}')
    print(f'Mentees: {User.query.filter_by(user_type=\"2\").count()}')
    print(f'Mentors: {User.query.filter_by(user_type=\"1\").count()}')
    print(f'Institutions: {User.query.filter_by(user_type=\"3\").count()}')
"
```

### Test Login
```bash
python -c "
from app import app, User
from werkzeug.security import check_password_hash
with app.app_context():
    user = User.query.filter_by(email='mentee_1@xexample.com').first()
    if user and check_password_hash(user.password, 'Info@123'):
        print('✅ Login works!')
    else:
        print('❌ Login failed')
"
```

---

## Features Ready to Test

✅ User login/logout
✅ Mentee dashboard
✅ Mentor dashboard
✅ Institution dashboard
✅ Find mentors (as mentee)
✅ Find mentees (as mentor)
✅ View profiles
✅ Send mentorship requests
✅ Accept/reject requests
✅ Chat feature
✅ Meeting scheduling
✅ Task management

---

## Common Issues & Solutions

### Issue: Can't login
**Solution**: Check email format is exactly `userID@xexample.com` and password is `Info@123`

### Issue: User not found
**Solution**: Verify user ID is between 1-100 (e.g., mentee_1, mentor_50, institution_100)

### Issue: Profile incomplete
**Solution**: All profiles are pre-populated, should be complete

### Issue: Institutions not showing
**Solution**: Check Institution.query.count() to verify institutions exist

---

## Sample Test Data

### Mentee Example
```
Email: mentee_1@xexample.com
Password: Info@123
Name: Anna Müller (or similar)
Type: Mentee
Country: Foreign (90% chance)
```

### Mentor Example
```
Email: mentor_1@xexample.com
Password: Info@123
Name: Sakura Walker (or similar)
Type: Mentor
Experience: 5-25 years
```

### Institution Example
```
Email: institution_1@xexample.com
Password: Info@123
Name: Brian Nakamura (or similar)
Type: Institution Admin
```

---

## Next Steps

1. ✅ Start the Flask app: `python app.py`
2. ✅ Open browser: `http://localhost:5000`
3. ✅ Login with sample credentials
4. ✅ Explore features
5. ✅ Test interactions
6. ✅ Verify data quality

---

## Support

For detailed information, see:
- `COMPREHENSIVE_DUMMY_DATA_REPORT.md` - Full report
- `generate_comprehensive_dummy_data.py` - Script source code
- `app.py` - Database models

---

**Status**: ✅ READY TO USE
**Data**: ✅ VERIFIED AND COMPLETE
**Testing**: ✅ READY TO BEGIN
