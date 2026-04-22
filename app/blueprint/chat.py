from datetime import datetime

from flask import Blueprint, jsonify, request, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.database import db
from app.model import User, Conversation, ChatMessage

bp_chat = Blueprint('chat', __name__, url_prefix='/chat')


@bp_chat.route('/conversation', methods=['POST'])
@jwt_required()
def get_or_create_conversation():
    """Get the user's open conversation, or create one if none exists."""
    user_id = int(get_jwt_identity())

    conversation = Conversation.query.filter_by(
        user_id=user_id, status='open'
    ).first()

    if not conversation:
        conversation = Conversation(
            user_id=user_id,
            status='open',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.session.add(conversation)
        db.session.commit()

    return jsonify({
        "status": "success",
        "conversation": conversation.to_dict()
    }), 200


@bp_chat.route('/conversation/<int:conversation_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(conversation_id):
    """Get messages for a conversation. Supports ?since= for incremental polling."""
    user_id = int(get_jwt_identity())
    conversation = Conversation.query.get(conversation_id)

    if not conversation:
        return jsonify({"status": "error", "message": "Conversation not found"}), 404

    # Allow access if the user owns the conversation or is any authenticated user (agent)
    since = request.args.get('since')
    query = ChatMessage.query.filter_by(conversation_id=conversation_id)

    if since:
        try:
            since_dt = datetime.fromisoformat(since)
            query = query.filter(ChatMessage.created_at > since_dt)
        except (ValueError, TypeError):
            pass

    messages = query.order_by(ChatMessage.created_at.asc()).all()

    return jsonify({
        "status": "success",
        "messages": [m.to_dict() for m in messages]
    }), 200


@bp_chat.route('/conversation/<int:conversation_id>/message', methods=['POST'])
@jwt_required()
def send_message(conversation_id):
    """Send a message in a conversation."""
    user_id = int(get_jwt_identity())
    conversation = Conversation.query.get(conversation_id)

    if not conversation:
        return jsonify({"status": "error", "message": "Conversation not found"}), 404

    data = request.get_json()
    if not data or not data.get('message'):
        return jsonify({"status": "error", "message": "Message text required"}), 400

    # Determine role: if sender is the conversation owner, they're the 'user'; otherwise 'agent'
    sender_role = 'user' if user_id == conversation.user_id else 'agent'

    msg = ChatMessage(
        conversation_id=conversation_id,
        sender_id=user_id,
        sender_role=sender_role,
        message=data['message'],
        created_at=datetime.utcnow(),
    )
    db.session.add(msg)
    conversation.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": msg.to_dict()
    }), 201


@bp_chat.route('/conversations', methods=['GET'])
@jwt_required()
def list_conversations():
    """List open conversations (for admin/agent view)."""
    conversations = Conversation.query.filter_by(
        status='open'
    ).order_by(Conversation.updated_at.desc()).all()

    result = []
    for conv in conversations:
        user = User.query.get(conv.user_id)
        last_msg = ChatMessage.query.filter_by(
            conversation_id=conv.id
        ).order_by(ChatMessage.created_at.desc()).first()

        result.append({
            **conv.to_dict(),
            'user_name': f"{user.name} {user.last_name}" if user else "Unknown",
            'last_message': last_msg.message[:50] if last_msg else None,
            'last_message_at': last_msg.created_at.isoformat() if last_msg else None,
        })

    return jsonify({
        "status": "success",
        "conversations": result
    }), 200


@bp_chat.route('/admin', methods=['GET'])
def admin_page():
    """Serve the agent chat admin interface."""
    return render_template('chat_admin.html')
