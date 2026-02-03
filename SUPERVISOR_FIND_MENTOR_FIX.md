# Supervisor Find Mentor - View Profile Button Fix

## Problem Identified

Some "View Profile" buttons on the Supervisor Find Mentor page were not working while others were functioning correctly. This was a **critical JavaScript bug** caused by improper data handling.

## Root Cause Analysis

### The Issue
The original implementation passed mentor data directly as inline string parameters in the `onclick` attribute:

```html
<button onclick="openProfileModal(
    '{{ mentor.user.name }}',
    '{{ mentor.profession }}',
    '{{ mentor.organisation }}',
    ...
    '{{ mentor.criminal_certificate }}'
)">
    View Profile
</button>
```

### Why This Failed

1. **Special Characters Breaking JavaScript**: When mentor data contained special characters like:
   - Single quotes (`'`) in names (e.g., "O'Brien")
   - Double quotes (`"`) in descriptions
   - Newlines or line breaks in text fields
   - Apostrophes in any field
   
   These characters would **break the JavaScript string parsing**, causing the function call to fail silently.

2. **Example of Failure**:
   ```html
   <!-- This breaks because of the apostrophe -->
   <button onclick="openProfileModal('John O'Brien', ...)">
   <!-- Parsed as: openProfileModal('John O'Brien', ...) 
        The apostrophe closes the string prematurely! -->
   ```

3. **Inconsistent Behavior**: 
   - Mentors with "clean" names (no special characters) → ✅ Button works
   - Mentors with special characters → ❌ Button fails silently
   - This created the appearance of random button failures

4. **No Error Messages**: The browser console showed no errors because the onclick handler simply failed to execute.

## Solution Implemented

### New Approach: Data Attributes + Event Listeners

Instead of passing data through onclick attributes, we now:

1. **Store mentor data in HTML data attributes** (JSON format):
   ```html
   <div class="mentor-card" 
        data-mentor-id="{{ mentor.id }}" 
        data-mentor-data="{{ mentor | tojson | escape }}">
   ```

2. **Use event listeners instead of inline onclick**:
   ```javascript
   document.addEventListener('DOMContentLoaded', function() {
     const viewProfileButtons = document.querySelectorAll('.view-profile-btn');
     
     viewProfileButtons.forEach(button => {
       button.addEventListener('click', function() {
         const mentorCard = this.closest('.mentor-card');
         const mentorDataJson = mentorCard.getAttribute('data-mentor-data');
         
         if (mentorDataJson) {
           try {
             const mentor = JSON.parse(mentorDataJson);
             openProfileModal(mentor);
           } catch (error) {
             console.error('Error parsing mentor data:', error);
             alert('Error loading mentor profile. Please try again.');
           }
         }
       });
     });
   });
   ```

3. **Updated openProfileModal function** to accept a mentor object:
   ```javascript
   function openProfileModal(mentor) {
     document.getElementById('modalName').innerText = mentor.user?.name || "Not specified";
     document.getElementById('modalEmail').innerText = mentor.user?.email || "Not specified";
     // ... etc
   }
   ```

## Benefits of This Fix

✅ **Handles Special Characters**: JSON encoding safely escapes all special characters
✅ **No String Parsing Issues**: Data is parsed as JSON, not as JavaScript code
✅ **Better Error Handling**: Try-catch block catches parsing errors
✅ **Cleaner Code**: Separates data from presentation logic
✅ **More Maintainable**: Easier to add/remove fields without modifying HTML
✅ **CSP Compliant**: No inline event handlers (better security)
✅ **Consistent Behavior**: All buttons work regardless of mentor data content

## Files Modified

- `templates/supervisor/supervisor_find_mentor.html`
  - Updated mentor card HTML to include data attributes
  - Replaced inline onclick with data-mentor-id attribute
  - Added DOMContentLoaded event listener for button initialization
  - Refactored openProfileModal() to accept mentor object instead of 37 individual parameters

## Testing Recommendations

Test with mentor profiles containing:
- ✅ Single quotes in names (e.g., "O'Brien", "D'Angelo")
- ✅ Double quotes in descriptions
- ✅ Apostrophes in any field
- ✅ Newlines in text areas
- ✅ Special characters (é, ñ, ü, etc.)
- ✅ Empty/null fields
- ✅ Very long text fields

All buttons should now work consistently regardless of data content.

## Technical Details

### Data Attribute Encoding
```html
data-mentor-data="{{ mentor | tojson | escape }}"
```
- `tojson`: Converts Python object to JSON string
- `escape`: HTML-escapes the JSON string for safe attribute storage

### JSON Parsing
```javascript
const mentor = JSON.parse(mentorDataJson);
```
- Safely parses JSON without executing code
- Handles all special characters correctly
- Throws error if JSON is malformed (caught by try-catch)

### Optional Chaining
```javascript
mentor.user?.name || "Not specified"
```
- Safely accesses nested properties
- Returns "Not specified" if property doesn't exist
- Prevents "Cannot read property of undefined" errors
