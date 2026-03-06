from flask import Blueprint, render_template, request, jsonify
from models import db, Product, Vendor, User, Review
from sqlalchemy import or_, and_

products_bp = Blueprint('products', __name__)

@products_bp.route('/')
@products_bp.route('/catalog')
def catalog():
    """Product catalog"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', None)
    search = request.args.get('search', '').strip()
    sort = request.args.get('sort', 'latest')
    min_price = request.args.get('min_price', 0, type=float)
    max_price = request.args.get('max_price', 100000, type=float)
    vendor_id = request.args.get('vendor', None, type=int)
    
    # Build query
    query = Product.query
    
    if search:
        query = query.filter(or_(
            Product.name.ilike(f'%{search}%'),
            Product.description.ilike(f'%{search}%')
        ))
    
    if category:
        query = query.filter_by(category=category)
    
    if vendor_id:
        query = query.filter_by(vendor_id=vendor_id)
    
    query = query.filter(and_(
        Product.price >= min_price,
        Product.price <= max_price
    ))
    
    # Sorting
    if sort == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_high':
        query = query.order_by(Product.price.desc())
    elif sort == 'rating':
        query = query.order_by(Product.rating.desc())
    else:  # latest
        query = query.order_by(Product.created_at.desc())
    
    products = query.paginate(page=page, per_page=12)
    
    return render_template('products/catalog.html', 
                         products=products,
                         search=search,
                         category=category,
                         sort=sort)

@products_bp.route('/<int:product_id>')
def detail(product_id):
    """Product detail page"""
    product = Product.query.get_or_404(product_id)
    vendor = Vendor.query.get(product.vendor_id)
    related = Product.query.filter(
        and_(
            Product.category == product.category,
            Product.id != product.id,
            Product.vendor_id == product.vendor_id
        )
    ).limit(6).all()
    
    reviews = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).all()
    
    return render_template('products/detail.html', 
                         product=product,
                         vendor=vendor,
                         related=related,
                         reviews=reviews)

@products_bp.route('/vendor/<int:vendor_id>')
def vendor_store(vendor_id):
    """Vendor store page"""
    vendor = Vendor.query.get_or_404(vendor_id)
    page = request.args.get('page', 1, type=int)
    
    products = Product.query.filter_by(vendor_id=vendor_id).paginate(page=page, per_page=12)
    
    return render_template('products/vendor_store.html',
                         vendor=vendor,
                         products=products)

@products_bp.route('/api/featured')
def api_featured():
    """Get featured products as JSON"""
    featured = Product.query.filter_by(is_featured=True).limit(8).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'image': p.image,
        'rating': p.rating
    } for p in featured])

@products_bp.route('/api/trending')
def api_trending():
    """Get trending products as JSON"""
    trending = Product.query.order_by(Product.rating.desc()).limit(8).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'image': p.image,
        'rating': p.rating
    } for p in trending])

@products_bp.route('/api/search')
def api_search():
    """Search products"""
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify([])
    
    products = Product.query.filter(or_(
        Product.name.ilike(f'%{q}%'),
        Product.description.ilike(f'%{q}%')
    )).limit(10).all()
    
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'image': p.image
    } for p in products])

@products_bp.route('/api/<int:product_id>')
def api_product(product_id):
    """Return basic product info"""
    p = Product.query.get_or_404(product_id)
    return jsonify({
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'image': p.image,
        'vendor': p.vendor.store_name if p.vendor else None
    })
