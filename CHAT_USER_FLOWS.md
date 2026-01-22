# Chat Feature - User Flows & Scenarios

## User Flow Diagrams

### Flow 1: Accessing Chat from Dashboard

```
User Dashboard
    ↓
Click "Messages" in Sidebar
    ↓
Main Chat Page (chat.html)
    ├─ View existing conversations
    ├─ Search conversations
    └─ Click on conversation to view messages
```

### Flow 2: Starting a New Chat

```
Main Chat Page
    ↓
Click "New Chat" Button
    ↓
New Chat Selection Page (new_chat.html)
    ├─ Browse Mentors
    ├─ Browse Mentees
    ├─ Browse Supervisors
    ├─ Browse Institutions
    └─ View Recent Contacts
        ↓
    Click "Browse [Type]" or Recent Contact
        ↓
    Contact Browser (chat_contacts.html)
        ├─ Search contacts
        ├─ Filter by type
        └─ View contact details
            ↓
        Click "Start Chat"
            ↓
        Main Chat Page (with new conversation)
```

### Flow 3: Sending a Message

```
Main Chat Page
    ↓
Type message in input field
    ↓
Press Enter or Click Send Button
    ↓
Message appears in chat (right-aligned, blue)
    ↓
Message saved to database
    ↓
Recipient receives notification
    ↓
Recipient sees message in chat (left-aligned, white)
```

### Flow 4: Searching Conversations

```
Main Chat Page
    ↓
Click search bar in conversations list
    ↓
Type search term (name or message preview)
    ↓
Conversations filtered in real-time
    ↓
Click on matching conversation
    ↓
View conversation messages
```

---

## Role-Based Scenarios

### Scenario 1: Mentee Initiating Chat with Mentor

**Mentee's Perspective:**
```
Mentee Dashboard
    ↓
Click "Messages"
    ↓
Main Chat Page
    ├─ View existing mentor conversations
    └─ Click "New Chat"
        ↓
    New Chat Page
        ↓
    Click "Browse Mentors"
        ↓
    Contact Browser
        ├─ See list of available mentors
        ├─ Search by name
        └─ Click "Start Chat" on desired mentor
            ↓
        Main Chat Page (new conversation with mentor)
            ↓
        Type message: "Hi, I'd like to discuss my career goals"
            ↓
        Press Enter to send
```

**Mentor's Perspective:**
```
Mentor Dashboard
    ↓
Click "Messages"
    ↓
Main Chat Page
    ├─ See new conversation from mentee
    ├─ Unread badge shows "1"
    └─ Click on conversation
        ↓
    View message from mentee
        ↓
    Type response: "Of course! Let's schedule a meeting"
        ↓
    Press Enter to send
```

### Scenario 2: Supervisor Coordinating with Mentor and Mentee

**Supervisor's Perspective:**
```
Supervisor Dashboard
    ↓
Click "Messages"
    ↓
Main Chat Page
    ├─ See conversations with:
    │  ├─ Mentee (John)
    │  ├─ Mentor (Sarah)
    │  └─ Institution Admin (Emma)
    │
    ├─ Click on Mentee conversation
    │  ├─ View mentee's progress
    │  └─ Send guidance
    │
    ├─ Click on Mentor conversation
    │  ├─ Discuss mentee's development
    │  └─ Coordinate support
    │
    └─ Click on Institution conversation
       ├─ Discuss program updates
       └─ Share reports
```

### Scenario 3: Institution Admin Communicating with Supervisor

**Institution Admin's Perspective:**
```
Institution Dashboard
    ↓
Click "Messages"
    ↓
Main Chat Page
    ├─ See conversations with supervisors only
    ├─ Cannot see mentee or mentor conversations
    └─ Click on supervisor conversation
        ↓
    View program coordination messages
        ↓
    Send: "Please provide monthly report"
        ↓
    Supervisor receives message
```

**Supervisor's Perspective:**
```
Supervisor Dashboard
    ↓
Click "Messages"
    ↓
Main Chat Page
    ├─ See message from Institution Admin
    ├─ Unread badge shows "1"
    └─ Click on Institution conversation
        ↓
    View request for monthly report
        ↓
    Type response: "Report attached"
        ↓
    Send message
```

---

## Detailed UI Interactions

### Main Chat Page Interactions

#### Conversation Selection
```
User sees list of conversations:
├─ John Doe (Mentor) - "That sounds great!..." - 2:30 PM - [2 unread]
├─ Sarah Miller (Supervisor) - "Thanks for your guidance!" - Yesterday
└─ Robert Park (Mentee) - "You: Can we schedule..." - 3 days ago

User clicks on John Doe conversation:
├─ Conversation highlights (blue background)
├─ Chat area updates to show John's messages
├─ Message input becomes active
└─ Unread badge disappears
```

#### Search Functionality
```
User clicks search bar
    ↓
User types "John"
    ↓
Conversations filter in real-time:
├─ John Doe (Mentor) - visible
├─ Sarah Miller (Supervisor) - hidden
└─ Robert Park (Mentee) - hidden

User clicks on John Doe
    ↓
Chat area updates
```

#### New Chat Button
```
User clicks "New Chat" button
    ↓
Navigates to new_chat.html
    ↓
User sees 4 cards:
├─ Chat with Mentors (Blue)
├─ Chat with Mentees (Purple)
├─ Chat with Supervisors (Green)
└─ Chat with Institutions (Orange)

User clicks "Browse Mentors"
    ↓
Navigates to chat_contacts.html
    ↓
Filtered to show mentors only
```

### Contact Browser Interactions

#### Search and Filter
```
User sees search bar and filter dropdown
    ↓
User types "John" in search
    ↓
Contacts filter in real-time:
├─ John Doe (Mentor) - visible
├─ Jane Smith (Mentor) - hidden
└─ Other contacts - hidden

User changes filter to "All Types"
    ↓
All contacts reappear

User types "Sarah"
    ↓
Only Sarah Miller (Supervisor) shows
```

#### Contact Card Interaction
```
User sees contact card:
├─ Avatar: "JD"
├─ Name: "John Doe"
├─ Email: "john.doe@example.com"
├─ Badge: "Mentor"
├─ Bio: "Senior Software Engineer..."
├─ Location: "📍 New York, USA"
├─ Status: "🟢 Active now"
└─ Button: "Start Chat"

User clicks "Start Chat"
    ↓
New conversation created
    ↓
Navigates to main chat page
    ↓
Chat area shows empty (no messages yet)
    ↓
User can type first message
```

### Message Input Interactions

#### Typing Message
```
User clicks message input field
    ↓
Cursor appears in input
    ↓
User types: "Hi John, how are you?"
    ↓
Input field auto-resizes if needed
    ↓
User can press:
├─ Enter → Send message
├─ Shift+Enter → New line
└─ Escape → Cancel (optional)
```

#### Sending Message
```
User types message
    ↓
User presses Enter or clicks Send button
    ↓
Message appears in chat:
├─ Right-aligned
├─ Blue background
├─ White text
├─ Timestamp: "2:45 PM"
└─ Sender: "ME"

Input field clears
    ↓
User can type next message
```

#### Attachment/Emoji (UI Ready, Backend Pending)
```
User clicks Attachment button
    ↓
File picker opens (backend to implement)

User clicks Emoji button
    ↓
Emoji picker opens (backend to implement)
```

---

## Permission-Based Access

### Mentee Access Control

**Mentee CAN:**
```
✅ View "Messages" in sidebar
✅ Access main chat page
✅ View conversations with mentors
✅ View conversations with supervisors
✅ Start new chat with mentors
✅ Start new chat with supervisors
✅ Send messages to mentors
✅ Send messages to supervisors
✅ Search conversations
✅ View contact browser filtered to mentors/supervisors
```

**Mentee CANNOT:**
```
❌ Chat with other mentees
❌ Chat with institutions
❌ See mentor-to-mentor conversations
❌ See supervisor-to-supervisor conversations
❌ See institution conversations
❌ Access other users' conversations
```

### Mentor Access Control

**Mentor CAN:**
```
✅ View "Messages" in sidebar
✅ Access main chat page
✅ View conversations with mentees
✅ View conversations with supervisors
✅ Start new chat with mentees
✅ Start new chat with supervisors
✅ Send messages to mentees
✅ Send messages to supervisors
✅ Search conversations
✅ View contact browser filtered to mentees/supervisors
```

**Mentor CANNOT:**
```
❌ Chat with other mentors
❌ Chat with institutions
❌ See mentee-to-mentee conversations
❌ See supervisor-to-supervisor conversations
❌ See institution conversations
❌ Access other users' conversations
```

### Supervisor Access Control

**Supervisor CAN:**
```
✅ View "Messages" in sidebar
✅ Access main chat page
✅ View conversations with mentees
✅ View conversations with mentors
✅ View conversations with institutions
✅ Start new chat with mentees
✅ Start new chat with mentors
✅ Start new chat with institutions
✅ Send messages to all types
✅ Search conversations
✅ View contact browser with all types
```

**Supervisor CANNOT:**
```
❌ Chat with other supervisors
❌ See supervisor-to-supervisor conversations
❌ Access other users' conversations
```

### Institution Access Control

**Institution CAN:**
```
✅ View "Messages" in sidebar
✅ Access main chat page
✅ View conversations with supervisors
✅ Start new chat with supervisors
✅ Send messages to supervisors
✅ Search conversations
✅ View contact browser filtered to supervisors
```

**Institution CANNOT:**
```
❌ Chat with mentees
❌ Chat with mentors
❌ Chat with other institutions
❌ See mentee conversations
❌ See mentor conversations
❌ See other institution conversations
❌ Access other users' conversations
```

---

## Error Scenarios

### Scenario 1: User Tries to Chat with Unauthorized Person

```
Mentee tries to access chat with another mentee
    ↓
System checks permissions
    ↓
Permission denied
    ↓
Show error message: "You cannot chat with other mentees"
    ↓
Redirect to main chat page
```

### Scenario 2: Conversation Not Found

```
User clicks on conversation link
    ↓
Conversation ID not found in database
    ↓
Show error message: "Conversation not found"
    ↓
Redirect to main chat page
```

### Scenario 3: Message Send Fails

```
User sends message
    ↓
Network error occurs
    ↓
Show error message: "Failed to send message. Please try again."
    ↓
Message stays in input field
    ↓
User can retry
```

---

## Success Scenarios

### Scenario 1: First Message Exchange

```
Mentee starts new chat with mentor
    ↓
Mentee sends: "Hi, I'd like guidance on my career"
    ✅ Message sent successfully
    ✅ Message appears in chat
    ✅ Timestamp shows
    ✅ Mentor receives notification
    ↓
Mentor opens chat
    ✅ Sees mentee's message
    ✅ Unread badge shows
    ↓
Mentor sends: "Of course! Let's discuss your goals"
    ✅ Message sent successfully
    ✅ Message appears in chat
    ✅ Mentee receives notification
    ↓
Conversation established ✅
```

### Scenario 2: Multi-Party Coordination

```
Supervisor receives message from mentee
    ✅ Reads message
    ✅ Responds to mentee
    ↓
Supervisor sends message to mentor
    ✅ Discusses mentee's progress
    ✅ Coordinates support
    ↓
Supervisor sends message to institution
    ✅ Reports on program status
    ✅ Requests resources
    ↓
All parties informed ✅
```

---

## Performance Scenarios

### Scenario 1: Large Conversation History

```
User opens conversation with 1000+ messages
    ↓
System loads first 50 messages
    ✅ Page loads quickly
    ↓
User scrolls up
    ↓
System loads next 50 messages
    ✅ Smooth pagination
    ↓
User can view entire history
```

### Scenario 2: Many Conversations

```
User has 100+ conversations
    ↓
System loads first 20 conversations
    ✅ Page loads quickly
    ↓
User searches for specific conversation
    ✅ Real-time filtering
    ✅ Results appear instantly
    ↓
User can find conversation easily
```

---

## Mobile Scenarios

### Scenario 1: Mobile Chat Access

```
User opens app on mobile
    ↓
Sidebar collapses to hamburger menu
    ↓
User clicks hamburger menu
    ↓
Sidebar slides in from left
    ↓
User clicks "Messages"
    ↓
Main chat page displays
    ├─ Conversations list: full width
    ├─ Chat area: full width
    └─ Responsive layout
    ↓
User can chat normally
```

### Scenario 2: Mobile Message Input

```
User opens chat on mobile
    ↓
Message input appears at bottom
    ↓
User taps input field
    ↓
Mobile keyboard appears
    ↓
Input field auto-resizes
    ↓
User types message
    ↓
User taps Send button
    ✅ Message sent
```

---

## Accessibility Scenarios

### Scenario 1: Keyboard Navigation

```
User navigates with keyboard only
    ↓
Tab through conversations
    ↓
Enter to select conversation
    ↓
Tab to message input
    ↓
Type message
    ↓
Enter to send
    ✅ Full keyboard support
```

### Scenario 2: Screen Reader

```
Screen reader user opens chat
    ↓
Hears: "Messages page"
    ↓
Hears: "Conversations list"
    ↓
Hears: "John Doe, Mentor, 2 unread messages"
    ↓
Hears: "Chat area"
    ↓
Hears: "Message from John: That sounds great"
    ✅ Full screen reader support
```

---

## Summary

The chat feature provides:
- ✅ Intuitive user flows
- ✅ Role-based access control
- ✅ Responsive design
- ✅ Real-time interactions
- ✅ Error handling
- ✅ Performance optimization
- ✅ Accessibility support
- ✅ Mobile support

All flows are designed with the user experience in mind and ready for backend implementation.
