# Chat Feature UI Documentation

## Overview
A comprehensive, user-friendly chat interface has been implemented for the Mentor Connect application. The chat system supports role-based messaging between different user types with appropriate access controls.

## Chat Architecture

### User Roles & Permissions

#### 1. **Mentees** (user_type = "2")
- Can chat with: **Mentors** and **Supervisors**
- Cannot chat with: Other mentees or institutions
- Use case: Seek guidance, ask questions, schedule meetings

#### 2. **Mentors** (user_type = "1")
- Can chat with: **Mentees** and **Supervisors**
- Cannot chat with: Other mentors or institutions
- Use case: Provide guidance, support mentees, coordinate with supervisors

#### 3. **Supervisors** (user_type = "0")
- Can chat with: **Mentees**, **Mentors**, and **Institutions**
- Cannot chat with: Other supervisors
- Use case: Oversee mentorships, coordinate programs, communicate with institutions

#### 4. **Institutions** (user_type = "3")
- Can chat with: **Supervisors only**
- Cannot chat with: Mentees, mentors, or other institutions
- Use case: Administrative communication, program coordination

## UI Components

### 1. **Main Chat Page** (`templates/chat.html`)
The primary interface for active conversations.

**Features:**
- **Left Sidebar (Conversations List)**
  - Search conversations by name or preview text
  - Display recent conversations with unread message count
  - Show user type badge (Mentor, Mentee, Supervisor, Institution)
  - Last message preview and timestamp
  - Active conversation highlighting
  - "New Chat" button to start conversations

- **Main Chat Area**
  - Chat header with contact info and status
  - Action buttons: Call, Video Call, More Options
  - Message display area with:
    - Received messages (left-aligned, white background)
    - Sent messages (right-aligned, blue background)
    - Typing indicators (animated dots)
    - Message timestamps
  - Message input area with:
    - Text input field with auto-resize
    - Attachment button
    - Emoji button
    - Send button
  - Support for Shift+Enter for multi-line messages

**Styling:**
- Clean, modern design using Tailwind CSS
- Gradient avatars for visual distinction
- Smooth transitions and hover effects
- Responsive layout for mobile and desktop

### 2. **New Chat Page** (`templates/new_chat.html`)
Interface for initiating new conversations.

**Features:**
- **Chat Type Selection Cards**
  - Browse Mentors (Blue)
  - Browse Mentees (Purple)
  - Browse Supervisors (Green)
  - Browse Institutions (Orange)
  - Each card shows available count and quick action button

- **Recent Contacts Section**
  - Quick access to frequently contacted users
  - Shows last chat timestamp
  - One-click access to resume conversations

**Use Case:**
- Users click "New Chat" button from main chat page
- Select the type of person they want to chat with
- Browse available contacts

### 3. **Contact Browser** (`templates/chat_contacts.html`)
Detailed contact selection interface.

**Features:**
- **Search & Filter**
  - Search by name or email
  - Filter by user type (Mentors, Mentees, Supervisors, Institutions)
  - Real-time filtering with no results message

- **Contact Cards**
  - User avatar with initials
  - Name and email
  - User type badge
  - Brief bio/description
  - Location
  - Online status indicator (🟢 Active, 🟡 Away, 🔴 Offline)
  - "Start Chat" button

- **Responsive Grid**
  - 1 column on mobile
  - 2 columns on tablet
  - 3 columns on desktop

## Navigation Integration

### Sidebar Menu Updates
The "Messages" link has been added to the sidebar for all user types:

```
Supervisors:
- Dashboard
- All Mentors
- All Mentees
- All Institutions
- All Requests
- All Meetings
- All Calendar
- All Tasks
- Create Account
- Manage Accounts
- Messages ← NEW

Mentors:
- Dashboard
- Find Mentee
- Mentoring Request
- My Mentees
- My Meetings
- My Calendar
- My Task
- Messages ← NEW

Mentees:
- Dashboard
- Find Mentor
- My Mentors
- My Meeting
- My Calendar
- My Task
- Messages ← NEW

Institutions:
- Institute Dashboard
- Institute Mentors
- Institute Mentees
- Institute Mentorships
- Institute Calendar
- Institute Task
- Messages ← NEW
```

## File Structure

```
templates/
├── chat.html                 # Main chat interface
├── new_chat.html            # New chat selection page
├── chat_contacts.html       # Contact browser
└── base2.html               # Updated with chat navigation links
```

## Key Features

### 1. **Real-time Messaging**
- Message display with timestamps
- Typing indicators
- Read/unread status (ready for backend integration)
- Message history scrolling

### 2. **User Experience**
- Smooth animations and transitions
- Responsive design (mobile, tablet, desktop)
- Intuitive navigation
- Quick access to recent contacts
- Search functionality

### 3. **Visual Design**
- Gradient avatars for user identification
- Color-coded user type badges
- Status indicators (online/away/offline)
- Clean, modern interface using Tailwind CSS
- Consistent with existing application design

### 4. **Accessibility**
- Semantic HTML structure
- Proper button and link elements
- Clear visual hierarchy
- Readable font sizes and colors
- Keyboard navigation support

## Backend Integration Points

The following endpoints need to be created in `app.py`:

### 1. **Chat Routes**
```python
@app.route('/chat')
def chat():
    # Display main chat interface
    # Load user's conversations
    # Pass current user info to template

@app.route('/new-chat')
def new_chat():
    # Display new chat selection page

@app.route('/chat-contacts')
def chat_contacts():
    # Display contact browser
    # Filter based on user type permissions
```

### 2. **API Endpoints** (for AJAX/fetch calls)
```python
@app.route('/api/conversations')
def get_conversations():
    # Return list of user's conversations
    # Include last message, timestamp, unread count

@app.route('/api/messages/<conversation_id>')
def get_messages(conversation_id):
    # Return messages for a conversation
    # Paginate for performance

@app.route('/api/send-message', methods=['POST'])
def send_message():
    # Save message to database
    # Return confirmation

@app.route('/api/contacts')
def get_contacts():
    # Return available contacts based on user type
    # Support filtering and searching

@app.route('/api/start-conversation', methods=['POST'])
def start_conversation():
    # Create new conversation
    # Return conversation ID
```

### 3. **Database Models** (to be added to `app.py`)
```python
class Conversation(db.Model):
    __tablename__ = "conversations"
    id = db.Column(db.Integer, primary_key=True)
    participant1_id = db.Column(db.Integer, db.ForeignKey("signup_details.id"))
    participant2_id = db.Column(db.Integer, db.ForeignKey("signup_details.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_message_at = db.Column(db.DateTime)

class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"))
    sender_id = db.Column(db.Integer, db.ForeignKey("signup_details.id"))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
```

## Usage Instructions

### For Users

1. **Access Chat**
   - Click "Messages" in the sidebar
   - View existing conversations

2. **Start New Chat**
   - Click "New Chat" button
   - Select contact type
   - Browse and select contact
   - Click "Start Chat"

3. **Send Message**
   - Type message in input field
   - Press Enter or click Send button
   - Use Shift+Enter for multi-line messages

4. **Search Conversations**
   - Use search bar in conversations list
   - Filter by name or message preview

### For Developers

1. **Customize Styling**
   - Edit Tailwind classes in HTML files
   - Modify colors in gradient avatars
   - Adjust responsive breakpoints

2. **Add Backend Logic**
   - Implement database models
   - Create API endpoints
   - Add message validation
   - Implement permission checks

3. **Enhance Features**
   - Add file sharing
   - Implement voice/video calls
   - Add message reactions
   - Create message search
   - Add typing indicators (real-time)

## Security Considerations

1. **Permission Validation**
   - Verify user can chat with recipient based on role
   - Prevent unauthorized conversations
   - Validate conversation access

2. **Message Validation**
   - Sanitize message content
   - Prevent XSS attacks
   - Validate message length

3. **Authentication**
   - Require login for chat access
   - Validate session tokens
   - Implement rate limiting

## Future Enhancements

1. **Real-time Features**
   - WebSocket integration for live messaging
   - Real-time typing indicators
   - Online status updates
   - Message read receipts

2. **Advanced Features**
   - File/image sharing
   - Voice messages
   - Video call integration
   - Message search
   - Message reactions/emojis
   - Group chats

3. **Notifications**
   - Push notifications
   - Email notifications
   - In-app notification badge
   - Sound alerts

4. **Analytics**
   - Message statistics
   - User engagement metrics
   - Response time tracking

## Testing Checklist

- [ ] Chat page loads correctly
- [ ] Conversations list displays properly
- [ ] Search functionality works
- [ ] New chat button opens new chat page
- [ ] Contact browser filters work
- [ ] Message input accepts text
- [ ] Send button functionality (ready for backend)
- [ ] Responsive design on mobile
- [ ] Responsive design on tablet
- [ ] Responsive design on desktop
- [ ] Navigation links work for all user types
- [ ] Typing indicators animate
- [ ] Message timestamps display
- [ ] User avatars show correctly
- [ ] Status indicators display

## Support

For questions or issues with the chat UI, refer to this documentation or contact the development team.
