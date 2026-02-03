# JSON Serialization Error Fix - Supervisor Find Mentor

## Problem
When accessing the Supervisor Find Mentor page, the application crashed with:
```
TypeError: Object of type MentorProfile is not JSON serializable
```

## Root Cause
The template was trying to use Jinja2's `tojson` filter on a SQLAlchemy model object:
```html
data-mentor-data="{{ mentor | tojson | escape }}"
```

SQLAlchemy model objects cannot be directly serialized to JSON because they contain:
- Database relationships
- Lazy-loaded attributes
- Custom Python objects
- Non-JSON-serializable types

## Solution Implemented

### Approach: Data Attributes Instead of JSON Serialization

Instead of trying to serialize the entire model object, we now store each mentor field as individual HTML data attributes:

```html
<button class="view-profile-btn" 
  data-mentor-id="{{ mentor.id }}"
  data-name="{{ mentor.user.name }}"
  data-email="{{ mentor.user.email }}"
  data-profession="{{ mentor.profession }}"
  ...
  data-criminal-certificate="{{ mentor.criminal_certificate }}">
  View Profile
</button>
```

### JavaScript Implementation

The JavaScript event listener reads these data attributes and reconstructs the mentor object:

```javascript
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.view-profile-btn').forEach(button => {
    button.addEventListener('click', function() {
      const mentor = {
        id: this.getAttribute('data-mentor-id'),
        user: {
          name: this.getAttribute('data-name'),
          email: this.getAttribute('data-email')
        },
        profession: this.getAttribute('data-profession'),
        // ... etc
      };
      openProfileModal(mentor);
    });
  });
});
```

## Benefits

✅ **No JSON Serialization Issues** - Each field is stored as a simple string attribute
✅ **Works with SQLAlchemy Models** - No need to convert models to dictionaries
✅ **Clean HTML** - Data attributes are standard HTML5 practice
✅ **Efficient** - No JSON parsing overhead
✅ **Maintainable** - Easy to add/remove fields

## Files Modified

1. **templates/supervisor/supervisor_find_mentor.html**
   - Removed `data-mentor-data="{{ mentor | tojson | escape }}"`
   - Added individual data attributes for each mentor field
   - Updated JavaScript to read from data attributes

2. **app.py**
   - No changes needed (mentors are passed as model objects)

## Technical Details

### Why This Works

HTML data attributes are always strings, so:
- `{{ mentor.name }}` → `"John O'Brien"` (string)
- `{{ mentor.years_of_experience }}` → `"10"` (string)
- `{{ mentor.profile_picture }}` → `"image.jpg"` (string)

No JSON serialization is needed - Jinja2 automatically converts values to strings.

### Attribute Naming Convention

Data attributes use kebab-case (hyphens) following HTML conventions:
- `data-mentor-id` (not `data-mentorId`)
- `data-profile-picture` (not `data-profilePicture`)
- `data-mentorship-topics` (not `data-mentorshipTopics`)

JavaScript converts these to camelCase when building the object:
```javascript
const mentor = {
  mentorId: this.getAttribute('data-mentor-id'),  // ✅ Converted to camelCase
  profilePicture: this.getAttribute('data-profile-picture'),
  mentorshipTopics: this.getAttribute('data-mentorship-topics')
};
```

## Testing

The fix has been verified to:
- ✅ Load the Supervisor Find Mentor page without errors
- ✅ Display all mentor cards correctly
- ✅ Handle all mentor fields (including special characters)
- ✅ Open profile modal when View Profile button is clicked
- ✅ Display all mentor information in the modal

## Result

The Supervisor Find Mentor page now loads successfully and all View Profile buttons work correctly with no JSON serialization errors.
