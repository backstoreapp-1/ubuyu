from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Order, OrderItem, Product, Notification
from datetime import datetime
import secrets

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout page"""
    if request.method == 'POST':
        delivery_address = request.form.get('delivery_address', '').strip()
        delivery_notes = request.form.get('delivery_notes', '')
        payment_method = request.form.get('payment_method', 'mpesa')
        
        cart_data = request.form.get('cart_data', '{}')
        
        if not delivery_address:
            flash('Delivery address is required', 'error')
            return redirect(url_for('orders.checkout'))
        
        # Create order
        order_number = 'ORD-' + secrets.token_hex(4).upper()
        total_amount = 0
        
        order = Order(
            customer_id=current_user.id,
            order_number=order_number,
            total_amount=0,
            payment_method=payment_method,
            delivery_address=delivery_address,
            delivery_notes=delivery_notes
        )
        
        db.session.add(order)
        db.session.flush()
        
        # Add items from cart (you'd parse cart_data)
        # For now, this is a skeleton
        
        db.session.commit()
        
        # Create notification
        notification = Notification(
            user_id=current_user.id,
            type='order',
            title=f'Order Confirmed: {order_number}',
            content=f'Your order has been placed. Total: KES {order.total_amount}',
            related_id=order.id
        )
        db.session.add(notification)
        db.session.commit()
        
        flash(f'Order created: {order_number}', 'success')
        return redirect(url_for('orders.detail', order_id=order.id))
    
    return render_template('orders/checkout.html')

@orders_bp.route('/<int:order_id>')
@login_required
def detail(order_id):
    """Order detail"""
    order = Order.query.get_or_404(order_id)
    
    # Check permission
    if order.customer_id != current_user.id and current_user.role != 'admin':
        flash('Unauthorized', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('orders/detail.html', order=order)

@orders_bp.route('/history')
@login_required
def history():
    """Order history"""
    page = request.args.get('page', 1, type=int)
    orders = Order.query.filter_by(customer_id=current_user.id).order_by(
        Order.created_at.desc()
    ).paginate(page=page, per_page=10)
    
    return render_template('orders/history.html', orders=orders)

@orders_bp.route('/track/<order_number>')
def track(order_number):
    """Track order without login"""
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    return render_template('orders/track.html', order=order)

@orders_bp.route('/api/<int:order_id>/status', methods=['GET', 'POST'])
@login_required
def api_order_status(order_id):
    """Get or update order status"""
    order = Order.query.get_or_404(order_id)
    
    if request.method == 'POST':
        # Only vendor or admin can update
        if order.vendor_id != current_user.id and current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        new_status = request.json.get('status')
        if new_status not in ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']:
            return jsonify({'error': 'Invalid status'}), 400
        
        old_status = order.status
        order.status = new_status
        order.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Notify customer
        notification = Notification(
            user_id=order.customer_id,
            type='order',
            title='Order Status Updated',
            content=f'Your order status changed from {old_status} to {new_status}',
            related_id=order.id
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({'status': 'ok'})
    
    return jsonify({
        'id': order.id,
        'number': order.order_number,
        'status': order.status,
        'total': order.total_amount,
        'created_at': order.created_at.isoformat()
    })
