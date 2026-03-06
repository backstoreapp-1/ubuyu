# Ubuyu Marketplace - Startup-Level African E-Commerce Platform

A complete, production-ready online marketplace for selling authentic African ubuyu (baobab fruit candies) with a modern, Netflix-inspired design.

## Features

### 🛍️ Customer Features
- **Browse & Shop**: Responsive product catalog with advanced filters
- **Search**: Real-time product search
- **Shopping Cart**: localStorage-based cart system
- **Checkout**: Multi-step checkout with delivery & payment options
- **Order Tracking**: Track orders in real-time
- **Reviews & Ratings**: Leave detailed product reviews
- **User Profiles**: Manage account and order history
- **Notifications**: Real-time order and message alerts
- **Chat**: Floating chat widget for customer support
- **WhatsApp Integration**: Direct WhatsApp ordering

### 🏪 Vendor Features
- **Vendor Dashboard**: Overview of sales, orders, and earnings
- **Product Management**: Add, edit, delete, and feature products
- **Order Management**: View and update order status
- **Earnings Tracking**: Monitor total sales and revenue
- **Store Management**: Customize vendor store details
- **Analytics**: View sales performance

### 👨‍💼 Admin Features
- **User Management**: Manage all users and roles
- **Vendor Approval**: Approve/reject vendor applications
- **Product Management**: Feature or remove products
- **Order Oversight**: View all orders and manage disputes
- **Analytics Dashboard**: Platform-wide statistics
- **Settings**: Configure platform settings

## Technology Stack

### Backend
- **Python 3.8+**
- **Flask 2.3.3** - Lightweight web framework
- **SQLAlchemy 2.0.21** - ORM for database
- **SQLite/MySQL** - Database (configurable)
- **Werkzeug** - Password hashing and security

### Frontend
- **HTML5**
- **CSS3** - Modern, responsive design with animations
- **Vanilla JavaScript** - No heavy dependencies
- **Local Storage** - Client-side cart persistence

### Design Theme
- **Primary Colors**: Red (#d32f2f), Orange (#f57c00), Yellow (#fbc02d), Brown (#8d6e63)
- **Inspiration**: Netflix design, food delivery apps, African street markets
- **Responsive**: Mobile-first, works on all devices

## Project Structure

```
marketplace/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── models.py             # SQLAlchemy database models
├── requirements.txt      # Python dependencies
│
├── routes/
│   ├── main.py          # Home, landing pages
│   ├── auth.py          # Authentication (login, register, logout)
│   ├── products.py      # Product catalog, search, filters
│   ├── orders.py        # Order management, checkout
│   ├── messages.py      # Private messaging system
│   ├── vendor.py        # Vendor dashboard & management
│   └── admin.py         # Admin panel
│
├── templates/
│   ├── base.html        # Base template with navigation
│   ├── index.html       # Landing page
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── products/
│   │   ├── catalog.html
│   │   ├── detail.html
│   │   └── vendor_store.html
│   ├── orders/
│   │   ├── checkout.html
│   │   ├── detail.html
│   │   ├── history.html
│   │   └── track.html
│   ├── vendor/
│   │   ├── dashboard.html
│   │   ├── products.html
│   │   ├── add_product.html
│   │   ├── orders.html
│   │   └── settings.html
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── users.html
│   │   ├── vendors.html
│   │   ├── products.html
│   │   └── orders.html
│   └── messages/
│       ├── inbox.html
│       └── conversation.html
│
├── static/
│   ├── css/
│   │   └── style.css    # Main stylesheet with animations
│   ├── js/
│   │   └── main.js      # JavaScript functionality
│   └── images/          # Product images
│
├── uploads/             # User-uploaded files
└── database/           # Database files
```

## Installation & Setup

### 1. Clone and Navigate
```bash
cd /home/shakes/Desktop/ubuyu/marketplace
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 5. Initialize Database
```bash
python app.py
```

### 6. Run the Application
```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

## Default Admin Account

After first run, create an admin account:
```bash
python
>>> from app import app, db
>>> from models import User
>>> with app.app_context():
...     admin = User(email='admin@ubuyu.local', username='admin', full_name='Admin', role='admin')
...     admin.set_password('admin123')
...     db.session.add(admin)
...     db.session.commit()
```

Then login at `/auth/login`.

## Database Models

### Users
- Email, username, password hash
- Full name, phone, avatar
- Role: customer, vendor, admin
- Timestamps for created/updated

### Vendors
- Store name, slug, description
- Logo and banner images
- Approval status
- Rating and total sales tracking

### Products
- Name, description, category
- Price, cost price, stock
- Images (primary + multiple)
- Featured flag
- Rating and review counts

### Orders
- Order number, customer reference
- Total amount, payment status
- Delivery address and notes
- Order items with quantities
- Status tracking

### Messages
- Private messages between users
- Read/unread status
- Order-related messages

### Notifications
- User notifications
- Types: order, message, payment
- Read/unread status

### Reviews
- Product ratings (1-5 stars)
- User reviews and titles
- Helpful count

## Key Features Explained

### 🎨 Modern UI/UX
- Vibrant African-inspired color scheme
- Smooth animations and transitions
- Mobile-responsive grid layouts
- Netflix-style product cards

### 🔒 Security
- Password hashing with Werkzeug
- Secure session management
- CSRF protection via Flask-WTF
- SQL injection prevention through ORM

### 💳 Payment Ready
- M-Pesa integration points
- PayPal integration points
- Cash on delivery option

### 📱 Mobile Optimized
- Responsive design works on all sizes
- Touch-friendly buttons
- Mobile navigation

### 🌍 Localization
- Kenyan shilling (KES) pricing
- WhatsApp integration for orders
- Support for local vendors

## Deployment

### Heroku/Render
```bash
# Create Procfile
web: gunicorn app:app

# Create runtime.txt
python-3.9.16

# Deploy
git push heroku main
```

### Using Environment Variables
```
FLASK_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host/db
```

## API Endpoints

### Public
- `GET /` - Home page
- `GET /products/catalog` - Product catalog
- `GET /products/<id>` - Product detail
- `GET /products/vendor/<id>` - Vendor store
- `POST /auth/register` - User registration
- `POST /auth/login` - User login

### Protected (Login Required)
- `GET /orders/checkout` - Checkout page
- `POST /orders/checkout` - Place order
- `GET /messages/inbox` - Messages inbox
- `POST /messages/send` - Send message
- `GET /profile` - User profile

### Vendor Only
- `GET /vendor/dashboard` - Vendor dashboard
- `POST /vendor/products/add` - Add product
- `POST /vendor/products/<id>/edit` - Edit product

### Admin Only
- `GET /admin/` - Admin dashboard
- `GET /admin/users` - Manage users
- `GET /admin/vendors` - Manage vendors
- `POST /admin/vendors/<id>/approve` - Approve vendor

## Future Enhancements

1. **Payment Gateway Integration**
   - Stripe/PayPal full integration
   - M-Pesa API integration

2. **Advanced Analytics**
   - Sales charts and graphs
   - Customer behavior analytics
   - Inventory forecasting

3. **Logistics Integration**
   - Shipping rate calculation
   - Delivery tracking integration
   - Logistics partner APIs

4. **Social Features**
   - User ratings and reviews
   - Social sharing
   - Wishlist functionality

5. **Marketing Tools**
   - Email campaigns
   - Promotional codes
   - Loyalty program

6. **Mobile App**
   - Native iOS/Android apps
   - Push notifications
   - Offline ordering

## Support & Contact

For questions or issues:
- Email: support@ubuyu.local
- WhatsApp: +254 791 159 145
- GitHub Issues: (if open-sourced)

## License

Proprietary - Ubuyu Marketplace 2024

---

**Built with ❤️ for African entrepreneurs**
