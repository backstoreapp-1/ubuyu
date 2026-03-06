"""WebSocket event handlers for real-time messaging and notifications"""
from flask_socketio import emit, join_room, leave_room, rooms
from flask_login import current_user
from flask import request
from models import db, Message, Notification, User

# Dictionary to track online users and their admin status
connected_users = {}

def register_socket_handlers(socketio):
    """Register all socket event handlers"""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle user connection"""
        if current_user.is_authenticated:
            user_id = current_user.id
            connected_users[request.sid] = {
                'user_id': user_id,
                'role': current_user.role,
                'username': current_user.username
            }
            
            # Join user room for targeted messaging
            join_room(f'user_{user_id}')
            
            # If admin, join admin room
            if current_user.role == 'admin':
                join_room('admin_room')
            
            print(f"✅ User {current_user.username} (ID: {user_id}) connected - SID: {request.sid}")
        else:
            return False

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle user disconnection"""
        if request.sid in connected_users:
            user_data = connected_users.pop(request.sid)
            print(f"❌ User {user_data['username']} (ID: {user_data['user_id']}) disconnected")

    @socketio.on('join_admin_support')
    def handle_join_admin_support():
        """Join the admin support room"""
        if current_user.is_authenticated:
            room = f'support_chat'
            join_room(room)
            emit('status', {
                'msg': f'{current_user.full_name} joined support chat',
                'user_id': current_user.id,
                'username': current_user.username
            }, to=room)
            print(f"👤 {current_user.username} joined admin support room")

    @socketio.on('send_message')
    def handle_send_message(data):
        """Handle incoming message from customer or admin"""
        if not current_user.is_authenticated:
            emit('error', {'msg': 'Not authenticated'})
            return False
        
        receiver_id = data.get('receiver_id')
        content = data.get('content', '').strip()
        message_type = data.get('type', 'support')  # 'support', 'private'
        
        if not receiver_id or not content:
            emit('error', {'msg': 'Invalid message'})
            return False
        
        if len(content) > 5000:
            emit('error', {'msg': 'Message too long'})
            return False
        
        try:
            # Save message to database
            message = Message(
                sender_id=current_user.id,
                receiver_id=receiver_id,
                content=content
            )
            
            db.session.add(message)
            
            # Create notification for receiver
            sender_name = current_user.full_name or current_user.username
            notification = Notification(
                user_id=receiver_id,
                type='message',
                title=f'New message from {sender_name}',
                content=content[:100] + '...' if len(content) > 100 else content,
                related_id=message.id
            )
            
            db.session.add(notification)
            db.session.commit()
            
            # Emit to receiver's personal room
            message_data = {
                'id': message.id,
                'sender_id': message.sender_id,
                'sender_name': sender_name,
                'receiver_id': message.receiver_id,
                'content': message.content,
                'timestamp': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'type': message_type
            }
            
            # Send to receiver
            emit('new_message', message_data, to=f'user_{receiver_id}')
            
            # Send confirmation to sender
            emit('message_sent', {
                'id': message.id,
                'status': 'sent',
                'timestamp': message.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
            
            print(f"💬 Message from {current_user.username} to user {receiver_id}: {content[:50]}...")
            
        except Exception as e:
            print(f"❌ Error saving message: {str(e)}")
            emit('error', {'msg': 'Failed to save message'})
            return False

    @socketio.on('admin_send_reply')
    def handle_admin_reply(data):
        """Handle admin reply to customer message"""
        if not current_user.is_authenticated or current_user.role != 'admin':
            emit('error', {'msg': 'Unauthorized'})
            return False
        
        customer_id = data.get('customer_id')
        content = data.get('content', '').strip()
        
        if not customer_id or not content:
            emit('error', {'msg': 'Invalid reply'})
            return False
        
        try:
            # Save reply to database
            message = Message(
                sender_id=current_user.id,
                receiver_id=customer_id,
                content=content
            )
            
            db.session.add(message)
            
            # Create notification for customer
            notification = Notification(
                user_id=customer_id,
                type='message',
                title='Reply from UBUYU Support',
                content=content[:100] + '...' if len(content) > 100 else content,
                related_id=message.id
            )
            
            db.session.add(notification)
            db.session.commit()
            
            # Emit to customer's room
            reply_data = {
                'id': message.id,
                'sender_id': message.sender_id,
                'sender_name': 'UBUYU Support',
                'receiver_id': message.receiver_id,
                'content': message.content,
                'timestamp': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_admin_reply': True
            }
            
            emit('new_message', reply_data, to=f'user_{customer_id}')
            
            # Broadcast to all admin
            emit('message_replied', {
                'customer_id': customer_id,
                'message_id': message.id,
                'timestamp': message.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }, to='admin_room')
            
            print(f"✉️ Admin reply to customer {customer_id}")
            
        except Exception as e:
            print(f"❌ Error saving admin reply: {str(e)}")
            emit('error', {'msg': 'Failed to save reply'})
            return False

    @socketio.on('mark_as_read')
    def handle_mark_as_read(data):
        """Mark message as read"""
        if not current_user.is_authenticated:
            return False
        
        message_id = data.get('message_id')
        
        try:
            message = Message.query.get(message_id)
            if message and message.receiver_id == current_user.id:
                message.is_read = True
                db.session.commit()
                
                emit('message_read', {'message_id': message_id}, to=f'user_{message.sender_id}')
        except Exception as e:
            print(f"❌ Error marking message as read: {str(e)}")

    @socketio.on('typing')
    def handle_typing(data):
        """Notify that user is typing"""
        if not current_user.is_authenticated:
            return False
        
        receiver_id = data.get('receiver_id')
        
        if receiver_id:
            emit('user_typing', {
                'sender_id': current_user.id,
                'sender_name': current_user.full_name or current_user.username
            }, to=f'user_{receiver_id}')

    @socketio.on('stop_typing')
    def handle_stop_typing(data):
        """Notify that user stopped typing"""
        if not current_user.is_authenticated:
            return False
        
        receiver_id = data.get('receiver_id')
        
        if receiver_id:
            emit('user_stopped_typing', {
                'sender_id': current_user.id
            }, to=f'user_{receiver_id}')

    @socketio.on_error_default
    def default_error_handler(e):
        """Handle errors"""
        print(f'⚠️ Error: {str(e)}')
        emit('error', {'msg': str(e)})
