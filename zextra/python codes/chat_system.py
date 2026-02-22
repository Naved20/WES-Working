# ============================================================
# CHAT SYSTEM - Models and Routes
# ============================================================
# This module contains all chat-related models and API routes
# for the mentorship platform with role-based access control

from flask import jsonify, request, session
from datetime import datetime
from functools import wraps
from app import db, app, current_user

# ============================================================
# CHAT MODELS
# ============================================================

class ChatConversation(db.Model):
    """
    Represents a conversation between two users.
    Can be 1-to-1 or group conversations.
    """
    __tablename__ = "chat_conversations"
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Conversation type: 'direct' (1-to-1) or 'group'
    conversation_type = db.Column(db.String(20), default="direct")
    
    # For direct conversations: participant IDs
    participant1_id = db.Column(db.Integer, db.ForeignKey("signup_details.id"), nullable=True)
    participant2_id = db.Column(db.Integer, db.ForeignKey("signup_details.id"), nullable=True)
    
    # For group conversations: group name
    group_name = db.Column(db.String(200), nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    participant1 = db.relationship("User", foreign_keys=[participant1_id], backref="conversations_as_p1")
    participant2 = db.relationship("User", foreign_keys=[participant2_id], backref="conversations_as_p2")
    messages = db.relationship("ChatMessage", backref="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ChatConversation {self.id}>"


class ChatMessage(db.Model):
    """
    Represents a single message in a conversation.
    """
    __tablename__ = "chat_messages"
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("chat_conversations.id"), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("signup_details.id"), nullable=False)
    
    # Message content
    content = db.Column(db.Text, nullable=False)
    
    # Message metadata
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sender = db.relationship("User", backref="sent_messages")
    
    def __repr__(self):
        return f"<ChatMessage {self.id}>"


class ChatParticipant(db.Model):
    """
    Tracks participants in group conversations.
    For direct conversations, use ChatConversation.participant1/2
    """
    __tablename__ = "chat_participants"
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("chat_conversations.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("signup_details.id"), nullable=False)
    
    # When user joined the conversation
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = db.relationship("ChatConversation", backref="participants")
    user = db.relationship("User", backref="chat_participations")
    
    def __repr__(self):
        return f"<ChatParticipant {self.id}>"


# ============================================================
# ACCESS CONTROL HELPERS
# ============================================================

def check_chat_access(user_id, other_user_id, user_type):
    """
    Check if a user can chat with another user based on roles.
    
    Rules:
    - Mentee (2) can chat with: assigned mentor (1), supervisor (0)
    - Mentor (1) can chat with: assigned mentees (2), supervisor (0)
    - Supervisor (0) can chat with: any mentor (1), any mentee (2)
    - Institution (3) can chat with: supervisors (0)
    
    Returns: (allowed: bool, reason: str)
    """
    from app import User, MentorshipRequest
    
    other_user = User.query.get(other_user_id)
    if not other_user:
        return False, "User not found"
    
    other_type = other_user.user_type
    
    # Mentee (2) rules
    if user_type == "2":
        if other_type == "0":  # Can chat with supervisor
            return True, "Mentee can chat with supervisor"
        elif other_type == "1":  # Can chat with assigned mentor only
            # Check if there's an approved mentorship
            mentorship = MentorshipRequest.query.filter_by(
                mentee_id=user_id,
                mentor_id=other_user_id,
                final_status="approved"
            ).first()
            if mentorship:
                return True, "Mentee can chat with assigned mentor"
            return False, "Not assigned to this mentor"
        return False, "Mentee cannot chat with this user type"
    
    # Mentor (1) rules
    elif user_type == "1":
        if other_type == "0":  # Can chat with supervisor
            return True, "Mentor can chat with supervisor"
        elif other_type == "2":  # Can chat with assigned mentees only
            # Check if there's an approved mentorship
            mentorship = MentorshipRequest.query.filter_by(
                mentee_id=other_user_id,
                mentor_id=user_id,
                final_status="approved"
            ).first()
            if mentorship:
                return True, "Mentor can chat with assigned mentee"
            return False, "Not assigned to this mentee"
        return False, "Mentor cannot chat with this user type"
    
    # Supervisor (0) rules
    elif user_type == "0":
        if other_type in ["1", "2"]:  # Can chat with any mentor or mentee
            return True, "Supervisor can chat with any mentor or mentee"
        return False, "Supervisor cannot chat with this user type"
    
    # Institution (3) rules
    elif user_type == "3":
        if other_type == "0":  # Can chat with supervisors
            return True, "Institution can chat with supervisor"
        return False, "Institution cannot chat with this user type"
    
    return False, "Invalid user type"


def get_or_create_conversation(user_id, other_user_id):
    """
    Get existing conversation or create a new one between two users.
    """
    # Check if conversation already exists
    conversation = ChatConversation.query.filter(
        db.or_(
            db.and_(
                ChatConversation.participant1_id == user_id,
                ChatConversation.participant2_id == other_user_id
            ),
            db.and_(
                ChatConversation.participant1_id == other_user_id,
                ChatConversation.participant2_id == user_id
            )
        ),
        ChatConversation.conversation_type == "direct"
    ).first()
    
    if conversation:
        return conversation
    
    # Create new conversation
    conversation = ChatConversation(
        conversation_type="direct",
        participant1_id=min(user_id, other_user_id),
        participant2_id=max(user_id, other_user_id)
    )
    db.session.add(conversation)
    db.session.commit()
    return conversation


# ============================================================
# CHAT ROUTES
# ============================================================

@app.route("/api/chat/conversations", methods=["GET"])
def get_conversations():
    """
    Get all conversations for the current user.
    """
    if "email" not in session or "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    user_id = session.get("user_id")
    user_type = session.get("user_type")
    
    try:
        # Get all conversations where user is a participant
        conversations = ChatConversation.query.filter(
            db.or_(
                ChatConversation.participant1_id == user_id,
                ChatConversation.participant2_id == user_id
            ),
            ChatConversation.conversation_type == "direct"
        ).order_by(ChatConversation.updated_at.desc()).all()
        
        result = []
        for conv in conversations:
            # Get the other participant
            other_user_id = conv.participant2_id if conv.participant1_id == user_id else conv.participant1_id
            other_user = User.query.get(other_user_id)
            
            # Get last message
            last_message = ChatMessage.query.filter_by(
                conversation_id=conv.id
            ).order_by(ChatMessage.created_at.desc()).first()
            
            # Count unread messages
            unread_count = ChatMessage.query.filter_by(
                conversation_id=conv.id,
                is_read=False
            ).filter(ChatMessage.sender_id != user_id).count()
            
            result.append({
                "id": conv.id,
                "other_user_id": other_user_id,
                "other_user_name": other_user.name,
                "other_user_type": other_user.user_type,
                "last_message": last_message.content if last_message else None,
                "last_message_time": last_message.created_at.isoformat() if last_message else None,
                "unread_count": unread_count,
                "updated_at": conv.updated_at.isoformat()
            })
        
        return jsonify({"success": True, "conversations": result})
    
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/chat/start/<int:other_user_id>", methods=["POST"])
def start_conversation(other_user_id):
    """
    Start or get a conversation with another user.
    Checks access control before allowing.
    """
    if "email" not in session or "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    user_id = session.get("user_id")
    user_type = session.get("user_type")
    
    try:
        # Check access control
        allowed, reason = check_chat_access(user_id, other_user_id, user_type)
        if not allowed:
            return jsonify({"success": False, "message": reason}), 403
        
        # Get or create conversation
        conversation = get_or_create_conversation(user_id, other_user_id)
        
        return jsonify({
            "success": True,
            "conversation_id": conversation.id,
            "message": "Conversation started"
        })
    
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/chat/messages/<int:conversation_id>", methods=["GET"])
def get_messages(conversation_id):
    """
    Get all messages in a conversation.
    Includes pagination support.
    """
    if "email" not in session or "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    user_id = session.get("user_id")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    
    try:
        conversation = ChatConversation.query.get_or_404(conversation_id)
        
        # Check if user is a participant
        if not (conversation.participant1_id == user_id or conversation.participant2_id == user_id):
            return jsonify({"success": False, "message": "Access denied"}), 403
        
        # Get messages with pagination
        messages_query = ChatMessage.query.filter_by(
            conversation_id=conversation_id
        ).order_by(ChatMessage.created_at.asc())
        
        total = messages_query.count()
        messages = messages_query.paginate(page=page, per_page=per_page).items
        
        result = []
        for msg in messages:
            result.append({
                "id": msg.id,
                "sender_id": msg.sender_id,
                "sender_name": msg.sender.name,
                "content": msg.content,
                "is_read": msg.is_read,
                "created_at": msg.created_at.isoformat()
            })
        
        return jsonify({
            "success": True,
            "messages": result,
            "total": total,
            "page": page,
            "per_page": per_page
        })
    
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/chat/send", methods=["POST"])
def send_message():
    """
    Send a message in a conversation.
    """
    if "email" not in session or "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    user_id = session.get("user_id")
    data = request.get_json()
    
    conversation_id = data.get("conversation_id")
    content = data.get("content", "").strip()
    
    if not content:
        return jsonify({"success": False, "message": "Message cannot be empty"}), 400
    
    try:
        conversation = ChatConversation.query.get_or_404(conversation_id)
        
        # Check if user is a participant
        if not (conversation.participant1_id == user_id or conversation.participant2_id == user_id):
            return jsonify({"success": False, "message": "Access denied"}), 403
        
        # Create message
        message = ChatMessage(
            conversation_id=conversation_id,
            sender_id=user_id,
            content=content
        )
        db.session.add(message)
        
        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message_id": message.id,
            "created_at": message.created_at.isoformat()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/chat/mark-read/<int:conversation_id>", methods=["POST"])
def mark_messages_read(conversation_id):
    """
    Mark all messages in a conversation as read.
    """
    if "email" not in session or "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    user_id = session.get("user_id")
    
    try:
        conversation = ChatConversation.query.get_or_404(conversation_id)
        
        # Check if user is a participant
        if not (conversation.participant1_id == user_id or conversation.participant2_id == user_id):
            return jsonify({"success": False, "message": "Access denied"}), 403
        
        # Mark all unread messages from other user as read
        ChatMessage.query.filter(
            ChatMessage.conversation_id == conversation_id,
            ChatMessage.sender_id != user_id,
            ChatMessage.is_read == False
        ).update({
            ChatMessage.is_read: True,
            ChatMessage.read_at: datetime.utcnow()
        })
        
        db.session.commit()
        
        return jsonify({"success": True, "message": "Messages marked as read"})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/chat/allowed-contacts", methods=["GET"])
def get_allowed_contacts():
    """
    Get list of users the current user can chat with based on their role.
    """
    if "email" not in session or "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    user_id = session.get("user_id")
    user_type = session.get("user_type")
    
    try:
        from app import User, MentorshipRequest, MenteeProfile, MentorProfile
        
        allowed_contacts = []
        
        if user_type == "2":  # Mentee
            # Get assigned mentor
            mentorship = MentorshipRequest.query.filter_by(
                mentee_id=user_id,
                final_status="approved"
            ).first()
            
            if mentorship:
                mentor = User.query.get(mentorship.mentor_id)
                if mentor:
                    allowed_contacts.append({
                        "id": mentor.id,
                        "name": mentor.name,
                        "type": "1",
                        "role": "My Mentor"
                    })
            
            # Get supervisors
            supervisors = User.query.filter_by(user_type="0").all()
            for supervisor in supervisors:
                allowed_contacts.append({
                    "id": supervisor.id,
                    "name": supervisor.name,
                    "type": "0",
                    "role": "Supervisor"
                })
        
        elif user_type == "1":  # Mentor
            # Get assigned mentees
            mentorships = MentorshipRequest.query.filter_by(
                mentor_id=user_id,
                final_status="approved"
            ).all()
            
            for mentorship in mentorships:
                mentee = User.query.get(mentorship.mentee_id)
                if mentee:
                    allowed_contacts.append({
                        "id": mentee.id,
                        "name": mentee.name,
                        "type": "2",
                        "role": "My Mentee"
                    })
            
            # Get supervisors
            supervisors = User.query.filter_by(user_type="0").all()
            for supervisor in supervisors:
                allowed_contacts.append({
                    "id": supervisor.id,
                    "name": supervisor.name,
                    "type": "0",
                    "role": "Supervisor"
                })
        
        elif user_type == "0":  # Supervisor
            # Can chat with any mentor or mentee
            mentors = User.query.filter_by(user_type="1").all()
            for mentor in mentors:
                allowed_contacts.append({
                    "id": mentor.id,
                    "name": mentor.name,
                    "type": "1",
                    "role": "Mentor"
                })
            
            mentees = User.query.filter_by(user_type="2").all()
            for mentee in mentees:
                allowed_contacts.append({
                    "id": mentee.id,
                    "name": mentee.name,
                    "type": "2",
                    "role": "Mentee"
                })
        
        elif user_type == "3":  # Institution
            # Can chat with supervisors
            supervisors = User.query.filter_by(user_type="0").all()
            for supervisor in supervisors:
                allowed_contacts.append({
                    "id": supervisor.id,
                    "name": supervisor.name,
                    "type": "0",
                    "role": "Supervisor"
                })
        
        return jsonify({
            "success": True,
            "contacts": allowed_contacts
        })
    
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/chat")
def chat_page():
    """
    Render the chat page.
    """
    if "email" not in session or "user_id" not in session:
        return redirect(url_for("signin"))
    
    return render_template("chat.html")
