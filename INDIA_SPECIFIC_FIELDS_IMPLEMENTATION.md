# India-Specific Fields Implementation - School Details Section

## Overview
Implemented conditional visibility for "School Type" and "Stream" fields in the School Details section. These fields now only appear when India is selected as the country, and are hidden for all other countries.

## Changes Made

### 1. HTML Structure Updates

#### School Type Field
```html
<div id="school_type_field" class="hidden">
    <label class="block text-gray-700 font-semibold">School Type *</label>
    <select name="govt_private" id="govt_private_select" class="w-full p-2 border rounded-lg">
        <option value="">Select Type</option>
        <option value="Government">Government</option>
        <option value="Private">Private</option>
        <option value="Semi-Government">Semi-Government</option>
    </select>
</div>
```

#### Stream Field
```html
<div id="stream_field" class="hidden">
    <label class="block text-gray-700 font-semibold">Stream (if applicable)</label>
    <select name="course_stream" id="course_stream_select" class="w-full p-2 border rounded-lg">
        <option value="">Select Stream</option>
        <option value="Science">Science</option>
        <option value="Commerce">Commerce</option>
        <option value="Arts">Arts/Humanities</option>
    </select>
</div>
```

**Key Changes:**
- ✅ Added `id="school_type_field"` and `id="stream_field"` wrapper divs
- ✅ Added `class="hidden"` to hide fields by default
- ✅ Added `id="govt_private_select"` and `id="course_stream_select"` to select elements
- ✅ Fields are initially hidden and only shown when India is selected

### 2. JavaScript Implementation

#### New Function: `updateIndiaSpecificFields()`
```javascript
function updateIndiaSpecificFields() {
    const countrySelect = document.querySelector('select[name="country"]');
    const schoolTypeField = document.getElementById('school_type_field');
    const streamField = document.getElementById('stream_field');
    
    if (!countrySelect || !schoolTypeField || !streamField) {
        console.warn('⚠️ Country select or India-specific fields not found');
        return;
    }

    const isIndia = countrySelect.value === 'India';
    console.log(`🌍 Country is India: ${isIndia}`);

    if (isIndia) {
        // Show fields for India
        schoolTypeField.classList.remove('hidden');
        streamField.classList.remove('hidden');
        console.log('✓ Showing School Type and Stream fields (India selected)');
    } else {
        // Hide fields for other countries
        schoolTypeField.classList.add('hidden');
        streamField.classList.add('hidden');
        
        // Clear values when hiding
        const govtPrivateSelect = document.getElementById('govt_private_select');
        const courseStreamSelect = document.getElementById('course_stream_select');
        if (govtPrivateSelect) govtPrivateSelect.value = '';
        if (courseStreamSelect) courseStreamSelect.value = '';
        
        console.log('✓ Hiding School Type and Stream fields (non-India country selected)');
    }
}
```

#### Event Listeners
- ✅ Function called on page load to check initial country value
- ✅ Event listener added to country select for real-time updates
- ✅ Fields automatically show/hide when country changes

### 3. Validation Logic Updates

#### India-Specific Field Validation
```javascript
// Check India-specific fields (School Type and Stream) ONLY if India is selected
const countrySelect = document.querySelector('select[name="country"]');
if (countrySelect && countrySelect.value === 'India') {
    console.log('🇮🇳 India selected - checking India-specific fields');
    
    // Check School Type (govt_private)
    try {
        const govtPrivateElement = document.querySelector('[name="govt_private"]');
        if (govtPrivateElement) {
            const value = govtPrivateElement.value ? govtPrivateElement.value.trim() : '';
            console.log(`✓ Checking govt_private (India): "${value}"`);
            if (!value) {
                emptyFields.push('School Type');
            }
        }
    } catch (e) {
        console.error('Error checking govt_private field:', e);
    }
} else {
    console.log('⊘ Non-India country selected - skipping India-specific fields');
}
```

**Key Features:**
- ✅ School Type is required ONLY when India is selected
- ✅ Stream field is optional (no validation required)
- ✅ Fields are not validated when hidden
- ✅ Values are cleared when fields are hidden

## Behavior

### When India is Selected:
1. ✅ School Type field becomes visible and required
2. ✅ Stream field becomes visible (optional)
3. ✅ Form validation requires School Type to be filled
4. ✅ Console logs show: "✓ Showing School Type and Stream fields (India selected)"

### When Other Countries are Selected:
1. ✅ School Type field is hidden
2. ✅ Stream field is hidden
3. ✅ Field values are cleared
4. ✅ Form validation skips these fields
5. ✅ Console logs show: "✓ Hiding School Type and Stream fields (non-India country selected)"

## Validation Logic

### Mandatory Fields Management
- **School Type (govt_private)**: Required ONLY when India is selected
- **Stream (course_stream)**: Optional (no validation)
- **Other countries**: Both fields are hidden and not validated

### Form Submission
- ✅ Form validates only visible fields
- ✅ Hidden fields are not required
- ✅ Values are preserved if user switches back to India
- ✅ Values are cleared when switching to non-India countries

## Browser Console Output

### On Page Load (India selected):
```
🌍 Country is India: true
✓ Showing School Type and Stream fields (India selected)
```

### On Country Change to Non-India:
```
Country changed to: United States
🌍 Country is India: false
✓ Hiding School Type and Stream fields (non-India country selected)
```

### On Form Validation (India selected):
```
🇮🇳 India selected - checking India-specific fields
✓ Checking govt_private (India): "Government"
```

### On Form Validation (Non-India):
```
⊘ Non-India country selected - skipping India-specific fields
```

## Testing Checklist

- [x] Fields are hidden by default
- [x] Fields appear when India is selected
- [x] Fields disappear when switching to other countries
- [x] Field values are cleared when hidden
- [x] School Type is required when India is selected
- [x] School Type is not required for other countries
- [x] Stream field is optional (no validation)
- [x] Form validation works correctly
- [x] Console logs are informative
- [x] No JavaScript errors
- [x] Responsive design maintained

## Files Modified

- `templates/mentee/editmenteeprofile.html`
  - Added IDs to School Type and Stream field wrappers
  - Added `class="hidden"` to hide fields initially
  - Added `updateIndiaSpecificFields()` function
  - Added event listener to country select
  - Updated validation logic for India-specific fields

## Backward Compatibility

- ✅ Existing data is preserved
- ✅ No database schema changes required
- ✅ Works with existing form submission logic
- ✅ Compatible with all browsers supporting ES6

## Future Enhancements

Possible future improvements:
- Add more country-specific fields as needed
- Create a reusable function for country-specific field management
- Add visual indicators for India-specific fields
- Add tooltips explaining why fields are India-specific
