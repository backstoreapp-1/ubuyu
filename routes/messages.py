from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Message, Notification, User

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/inbox')
@login_required
def inbox():
    """Message inbox"""
    page = request.args.get('page', 1, type=int)
    
    messages = Message.query.filter(
        (Message.receiver_id == current_user.id) |
        (Message.sender_id == current_user.id)
    ).order_by(Message.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('messages/inbox.html', messages=messages)

@messages_bp.route('/conversation/<int:user_id>')
@login_required
def conversation(user_id):
    """Conversation with a user"""
    other_user = User.query.get_or_404(user_id)
    
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at.asc()).all()
    
    # Mark as read
    for msg in messages:
        if msg.receiver_id == current_user.id:
            msg.is_read = True
    db.session.commit()
    
    return render_template('messages/conversation.html', 
                         conversation_user=other_user,
                         messages=messages)

@messages_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    """Send a message"""
    receiver_id = request.json.get('receiver_id')
    content = request.json.get('content', '').strip()
    order_id = request.json.get('order_id')
    
    if not receiver_id or not content:
        return jsonify({'error': 'Missing fields'}), 400
    
    if len(content) > 5000:
        return jsonify({'error': 'Message too long'}), 400
    
    receiver = User.query.get_or_404(receiver_id)
    
    message = Message(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        order_id=order_id,
        content=content
    )
    
    db.session.add(message)
    
    # Create notification for receiver
    notification = Notification(
        user_id=receiver_id,
        type='message',
        title='New message from ' + current_user.full_name,
        content=content[:100] + '...' if len(content) > 100 else content,
        related_id=message.id
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({
        'id': message.id,
        'sender_id': message.sender_id,
        'receiver_id': message.receiver_id,
        'content': message.content,
        'created_at': message.created_at.isoformat()
    })

@messages_bp.route('/api/unread')
@login_required
def api_unread():
    """Get count of unread messages"""
    count = Message.query.filter(
        Message.receiver_id == current_user.id,
        Message.is_read == False
    ).count()
    
    return jsonify({'unread': count})

@messages_bp.route('/mark-read/<int:message_id>', methods=['POST'])
@login_required
def mark_read(message_id):
    """Mark message as read"""
    message = Message.query.get_or_404(message_id)
    
    if message.receiver_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    message.is_read = True
    db.session.commit()
    
    return jsonify({'status': 'ok'})
