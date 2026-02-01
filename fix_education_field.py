"""
Script to fix education field for existing mentor profiles
This ensures backward compatibility and prevents profile completion issues
"""

from app import app, db, MentorProfile

def fix_education_field():
    """
    Update all mentor profiles with None or empty education field
    Set education based on new educational fields or default to "Not specified"
    """
    with app.app_context():
        print("🔧 Starting education field fix...")
        
        # Get all mentor profiles
        profiles = MentorProfile.query.all()
        updated_count = 0
        
        for profile in profiles:
            # Check if education field is None or empty
            if not profile.education or profile.education.strip() == "":
                # Try to build education from new fields
                if profile.highest_qualification or profile.degree_name or profile.field_of_study:
                    education_parts = []
                    if profile.degree_name:
                        education_parts.append(profile.degree_name)
                    if profile.field_of_study:
                        education_parts.append(f"in {profile.field_of_study}")
                    if profile.highest_qualification:
                        education_parts.append(f"({profile.highest_qualification})")
                    profile.education = " ".join(education_parts)
                    print(f"✅ Updated profile {profile.id}: {profile.education}")
                else:
                    # No educational info available, set default
                    profile.education = "Not specified"
                    print(f"✅ Updated profile {profile.id}: Not specified")
                
                updated_count += 1
        
        # Commit all changes
        try:
            db.session.commit()
            print(f"\n🎉 Successfully updated {updated_count} mentor profiles!")
            print(f"📊 Total profiles checked: {len(profiles)}")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error updating profiles: {e}")

if __name__ == "__main__":
    fix_education_field()
