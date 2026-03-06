from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import current_user, logout_user, login_required
from models import db, Product, Vendor, User, Notification

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Landing page"""
    featured = Product.query.filter_by(is_featured=True).limit(8).all()
    trending = Product.query.order_by(Product.rating.desc()).limit(8).all()
    
    return render_template('index.html', 
                         featured=featured,
                         trending=trending)

@main_bp.route('/dashboard')
def dashboard():
    """Dynamic dashboard based on role"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    if current_user.role == 'vendor':
        return redirect(url_for('vendor.dashboard'))
    elif current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    else:
        return redirect(url_for('main.index'))

@main_bp.route('/profile')
def profile():
    """User profile"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    return render_template('profile.html', user=current_user)

@main_bp.route('/notifications')
def notifications():
    """User notifications"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    page = request.args.get('page', 1, type=int)
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
        Notification.created_at.desc()
    ).paginate(page=page, per_page=20)
    
    return render_template('notifications.html', notifications=notifications)

@main_bp.route('/api/notifications/unread')
def api_unread_notifications():
    """Get unread notification count"""
    from flask import jsonify
    if not current_user.is_authenticated:
        return jsonify({'unread': 0})
    
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'unread': count})

@main_bp.route('/api/notifications')
@login_required
def api_notifications():
    """Return recent notifications for logged in user"""
    notes = Notification.query.filter_by(user_id=current_user.id).order_by(
        Notification.created_at.desc()
    ).limit(20).all()
    return jsonify([{
        'id': n.id,
        'title': n.title,
        'content': n.content,
        'is_read': n.is_read,
        'created_at': n.created_at.strftime('%b %d, %Y %I:%M %p')
    } for n in notes])

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page"""
    if request.method == 'POST':
        # Handle contact form
        pass
    
    return render_template('contact.html')

@main_bp.route('/become-vendor')
def become_vendor():
    """Vendor signup"""
    if current_user.is_authenticated and current_user.role == 'vendor':
        return redirect(url_for('vendor.dashboard'))
    
    return render_template('become_vendor.html')

@main_bp.route('/become-vendor', methods=['POST'])
def register_vendor():
    """Register as vendor"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    if current_user.role != 'customer':
        return redirect(url_for('main.become_vendor'))
    
    store_name = request.form.get('store_name', '').strip()
    description = request.form.get('description', '').strip()
    
    if not store_name:
        return render_template('become_vendor.html', error='Store name is required')
    
    # Check if already vendor
    existing = Vendor.query.filter_by(user_id=current_user.id).first()
    if existing:
        return render_template('become_vendor.html', error='You are already a vendor')
    
    store_slug = store_name.lower().replace(' ', '-')
    
    vendor = Vendor(
        user_id=current_user.id,
        store_name=store_name,
        store_slug=store_slug,
        description=description,
        is_approved=False
    )
    
    current_user.role = 'vendor'
    db.session.add(vendor)
    db.session.commit()
    
    return render_template('vendor_pending.html')

@main_bp.route('/support')
@login_required
def support():
    """Customer support chat"""
    return render_template('customer/support.html')
