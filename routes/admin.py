import os
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, Vendor, Product, Order, ProductImage, Message, Notification
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin dashboard"""
    total_users = User.query.count()
    total_vendors = Vendor.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    pending_vendors = Vendor.query.filter_by(is_approved=False).count()
    
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_vendors=total_vendors,
                         total_products=total_products,
                         total_orders=total_orders,
                         pending_vendors=pending_vendors,
                         recent_orders=recent_orders)

@admin_bp.route('/users')
@admin_required
def users():
    """Manage users"""
    page = request.args.get('page', 1, type=int)
    role = request.args.get('role', None)
    
    query = User.query
    if role:
        query = query.filter_by(role=role)
    
    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('admin/users.html', users=users)

@admin_bp.route('/vendors')
@admin_required
def vendors():
    """Manage vendors"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    
    query = Vendor.query
    if status == 'pending':
        query = query.filter_by(is_approved=False)
    elif status == 'approved':
        query = query.filter_by(is_approved=True)
    
    vendors = query.order_by(Vendor.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('admin/vendors.html', vendors=vendors)

@admin_bp.route('/vendors/<int:vendor_id>/approve', methods=['POST'])
@admin_required
def approve_vendor(vendor_id):
    """Approve a vendor"""
    vendor = Vendor.query.get_or_404(vendor_id)
    vendor.is_approved = True
    db.session.commit()
    
    return jsonify({'status': 'approved'})

@admin_bp.route('/products')
@admin_required
def products():
    """Manage products"""
    page = request.args.get('page', 1, type=int)
    products = Product.query.order_by(Product.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('admin/products.html', products=products)

@admin_bp.route('/products/<int:product_id>/feature', methods=['POST'])
@admin_required
def feature_product(product_id):
    """Feature a product"""
    product = Product.query.get_or_404(product_id)
    product.is_featured = not product.is_featured
    db.session.commit()
    
    return jsonify({'featured': product.is_featured})

@admin_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@admin_required
def delete_product_admin(product_id):
    """Delete a product as admin"""
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'status': 'deleted'})


@admin_bp.route('/products/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    """Admin add product"""
    vendors = Vendor.query.filter_by(is_approved=True).all()
    if request.method == 'POST':
        vendor_id = request.form.get('vendor_id', type=int)
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'candy')
        price = request.form.get('price', 0, type=float)
        stock = request.form.get('stock', 0, type=int)
        
        if not (vendor_id and name and price > 0):
            flash('Please fill in required fields', 'error')
            return redirect(url_for('admin.add_product'))
        
        slug = name.lower().replace(' ', '-') + '-' + os.urandom(4).hex()
        product = Product(
            vendor_id=vendor_id,
            name=name,
            slug=slug,
            description=description,
            category=category,
            price=price,
            stock=stock
        )
        
        # handle primary image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                path = os.path.join(upload_dir, filename)
                file.save(path)
                product.image = filename
        
        db.session.add(product)
        db.session.flush()  # get id so we can add additional images
        
        # handle additional images
        if 'images' in request.files:
            files = request.files.getlist('images')
            for file in files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                    path = os.path.join(upload_dir, filename)
                    file.save(path)
                    img = ProductImage(product_id=product.id, image=filename)
                    db.session.add(img)
        
        db.session.commit()
        
        flash('Product added successfully', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/add_product.html', vendors=vendors)

@admin_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    vendors = Vendor.query.filter_by(is_approved=True).all()
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.vendor_id = request.form.get('vendor_id', product.vendor_id, type=int)
        product.name = request.form.get('name', product.name).strip()
        product.description = request.form.get('description', product.description).strip()
        product.category = request.form.get('category', product.category)
        product.price = request.form.get('price', product.price, type=float)
        product.stock = request.form.get('stock', product.stock, type=int)
        
        # primary image
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                file.save(os.path.join(upload_dir, filename))
                product.image = filename
        
        # additional images
        if 'images' in request.files:
            files = request.files.getlist('images')
            for file in files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                    file.save(os.path.join(upload_dir, filename))
                    img = ProductImage(product_id=product.id, image=filename)
                    db.session.add(img)
        
        db.session.commit()
        flash('Product updated', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/edit_product.html', product=product, vendors=vendors)
@admin_bp.route('/orders')
@admin_required
def orders():
    """View all orders"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', None)
    
    query = Order.query
    if status:
        query = query.filter_by(status=status)
    
    orders = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('admin/orders.html', orders=orders)

@admin_bp.route('/orders/<int:order_id>/approve', methods=['POST'])
@admin_required
def approve_order(order_id):
    """Approve an order"""
    order = Order.query.get_or_404(order_id)
    if order.status == 'pending':
        order.status = 'confirmed'
        db.session.commit()
        flash('Order approved successfully', 'success')
    else:
        flash('Order cannot be approved', 'error')
    return redirect(url_for('admin.orders'))

@admin_bp.route('/orders/<int:order_id>/confirm-payment', methods=['POST'])
@admin_required
def confirm_payment(order_id):
    """Confirm payment for an order"""
    order = Order.query.get_or_404(order_id)
    if order.payment_status == 'unpaid':
        order.payment_status = 'paid'
        db.session.commit()
        flash('Payment confirmed successfully', 'success')
    else:
        flash('Payment already confirmed', 'error')
    return redirect(url_for('admin.orders'))

@admin_bp.route('/orders/<int:order_id>/deliver', methods=['POST'])
@admin_required
def deliver_order(order_id):
    """Mark order as delivered"""
    order = Order.query.get_or_404(order_id)
    if order.status in ['confirmed', 'shipped']:
        order.status = 'delivered'
        db.session.commit()
        flash('Order marked as delivered', 'success')
    else:
        flash('Order cannot be marked as delivered', 'error')
    return redirect(url_for('admin.orders'))

@admin_bp.route('/orders/<int:order_id>/delete', methods=['POST'])
@admin_required
def delete_order(order_id):
    """Remove order (history)"""
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash('Order removed', 'success')
    return redirect(url_for('admin.orders'))

@admin_bp.route('/vendors/<int:vendor_id>/balance', methods=['GET', 'POST'])
@admin_required
def manage_vendor_balance(vendor_id):
    """Manage vendor account balance"""
    vendor = Vendor.query.get_or_404(vendor_id)
    admin_user = current_user
    
    if request.method == 'POST':
        action = request.form.get('action')
        amount = request.form.get('amount', type=float)
        
        if not amount or amount <= 0:
            flash('Invalid amount', 'error')
            return redirect(url_for('admin.manage_vendor_balance', vendor_id=vendor_id))
        
        if action == 'add':
            vendor.account_balance += amount
            flash(f'Added KES {amount:.2f} to {vendor.store_name} balance', 'success')
        elif action == 'subtract':
            if vendor.account_balance >= amount:
                vendor.account_balance -= amount
                flash(f'Subtracted KES {amount:.2f} from {vendor.store_name} balance', 'success')
            else:
                flash('Insufficient balance', 'error')
                return redirect(url_for('admin.manage_vendor_balance', vendor_id=vendor_id))
        elif action == 'transfer':
            # transfer from admin wallet to vendor
            if admin_user.wallet_balance >= amount:
                admin_user.wallet_balance -= amount
                vendor.account_balance += amount
                flash(f'Transferred KES {amount:.2f} from admin wallet to {vendor.store_name}', 'success')
            else:
                flash('Admin wallet has insufficient funds', 'error')
                return redirect(url_for('admin.manage_vendor_balance', vendor_id=vendor_id))
        
        db.session.commit()
        return redirect(url_for('admin.manage_vendor_balance', vendor_id=vendor_id))
    
    return render_template('admin/vendor_balance.html', vendor=vendor, admin=admin_user)

@admin_bp.route('/settings')
@admin_required
def settings():
    """Admin settings"""
    return render_template('admin/settings.html')

@admin_bp.route('/support')
@admin_required
def support_chats():
    """Admin support chat management"""
    page = request.args.get('page', 1, type=int)
    
    # Get all customers who have sent messages
    customers = db.session.query(User).join(
        Message, (Message.sender_id == User.id)
    ).filter(User.role == 'customer').distinct().all()
    
    # Get unread message count for admin
    unread_count = Message.query.filter(
        Message.receiver_id == current_user.id,
        Message.is_read == False
    ).count()
    
    return render_template('admin/support.html', 
                         customers=customers,
                         unread_count=unread_count)

@admin_bp.route('/support/<int:customer_id>')
@admin_required
def support_conversation(customer_id):
    """View conversation with a customer"""
    customer = User.query.get_or_404(customer_id)
    
    if customer.role != 'customer':
        flash('Invalid customer', 'error')
        return redirect(url_for('admin.support_chats'))
    
    # Get all messages between admin and customer
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == customer_id)) |
        ((Message.sender_id == customer_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at.asc()).all()
    
    # Mark messages as read
    for msg in messages:
        if msg.receiver_id == current_user.id and not msg.is_read:
            msg.is_read = True
    db.session.commit()
    
    return render_template('admin/support_conversation.html',
                         customer=customer,
                         messages=messages)
