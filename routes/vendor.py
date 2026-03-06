from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Vendor, Product, Order, Notification, ProductImage
from functools import wraps
import os

vendor_bp = Blueprint('vendor', __name__)

def vendor_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'vendor':
            flash('Vendor access required', 'error')
            return redirect(url_for('main.index'))
        vendor = Vendor.query.filter_by(user_id=current_user.id).first()
        if not vendor or not vendor.is_approved:
            flash('Your vendor account is not approved yet', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@vendor_bp.route('/dashboard')
@vendor_required
def dashboard():
    """Vendor dashboard"""
    vendor = Vendor.query.filter_by(user_id=current_user.id).first_or_404()
    
    total_products = Product.query.filter_by(vendor_id=vendor.id).count()
    total_orders = Order.query.filter_by(vendor_id=vendor.id).count()
    pending_orders = Order.query.filter_by(vendor_id=vendor.id, status='pending').count()
    
    recent_orders = Order.query.filter_by(vendor_id=vendor.id).order_by(
        Order.created_at.desc()
    ).limit(10).all()
    
    return render_template('vendor/dashboard.html',
                         vendor=vendor,
                         total_products=total_products,
                         total_orders=total_orders,
                         pending_orders=pending_orders,
                         recent_orders=recent_orders)

@vendor_bp.route('/products')
@vendor_required
def products():
    """Manage vendor products"""
    vendor = Vendor.query.filter_by(user_id=current_user.id).first_or_404()
    page = request.args.get('page', 1, type=int)
    
    products = Product.query.filter_by(vendor_id=vendor.id).order_by(
        Product.created_at.desc()
    ).paginate(page=page, per_page=20)
    
    return render_template('vendor/products.html', products=products, vendor=vendor)

@vendor_bp.route('/products/add', methods=['GET', 'POST'])
@vendor_required
def add_product():
    """Add new product"""
    vendor = Vendor.query.filter_by(user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'candy')
        price = request.form.get('price', 0, type=float)
        cost_price = request.form.get('cost_price', 0, type=float)
        stock = request.form.get('stock', 0, type=int)
        
        if not name or price <= 0:
            flash('Please fill in all required fields', 'error')
            return redirect(url_for('vendor.add_product'))
        
        slug = name.lower().replace(' ', '-') + '-' + os.urandom(4).hex()
        
        product = Product(
            vendor_id=vendor.id,
            name=name,
            slug=slug,
            description=description,
            category=category,
            price=price,
            cost_price=cost_price,
            stock=stock
        )
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                filename = str(product.id) + '_' + filename if product.id else filename
                upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                file.save(os.path.join(upload_dir, filename))
                product.image = filename
        
        db.session.add(product)
        db.session.commit()
        
        flash('Product added successfully', 'success')
        return redirect(url_for('vendor.products'))
    
    return render_template('vendor/add_product.html')

@vendor_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@vendor_required
def edit_product(product_id):
    """Edit product"""
    vendor = Vendor.query.filter_by(user_id=current_user.id).first_or_404()
    product = Product.query.get_or_404(product_id)
    
    if product.vendor_id != vendor.id:
        flash('Unauthorized', 'error')
        return redirect(url_for('vendor.products'))
    
    if request.method == 'POST':
        product.name = request.form.get('name', '').strip() or product.name
        product.description = request.form.get('description', '').strip()
        product.category = request.form.get('category', product.category)
        product.price = request.form.get('price', product.price, type=float)
        product.cost_price = request.form.get('cost_price', product.cost_price, type=float)
        product.stock = request.form.get('stock', product.stock, type=int)
        # optional image change
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
        return redirect(url_for('vendor.products'))
    
    return render_template('vendor/edit_product.html', product=product)

@vendor_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@vendor_required
def delete_product(product_id):
    """Delete product"""
    vendor = Vendor.query.filter_by(user_id=current_user.id).first_or_404()
    product = Product.query.get_or_404(product_id)
    
    if product.vendor_id != vendor.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({'status': 'deleted'})

@vendor_bp.route('/orders')
@vendor_required
def orders():
    """Vendor orders"""
    vendor = Vendor.query.filter_by(user_id=current_user.id).first_or_404()
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', None)
    
    query = Order.query.filter_by(vendor_id=vendor.id)
    if status:
        query = query.filter_by(status=status)
    
    orders = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('vendor/orders.html', orders=orders)

@vendor_bp.route('/settings')
@vendor_required
def settings():
    """Vendor settings"""
    vendor = Vendor.query.filter_by(user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        vendor.store_name = request.form.get('store_name', vendor.store_name)
        vendor.description = request.form.get('description', vendor.description)
        db.session.commit()
        
        flash('Settings updated', 'success')
        return redirect(url_for('vendor.settings'))
    
    return render_template('vendor/settings.html', vendor=vendor)
