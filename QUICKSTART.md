# Ubuyu Marketplace - Quick Start Guide

## What's Included

This is a **complete, production-ready** full-stack marketplace application for selling African ubuyu candies online.

## Quick Start

### 1. Install Dependencies
```bash
cd marketplace
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

### 3. Access the Site
- **Frontend**: http://localhost:5000
- **Products**: http://localhost:5000/products/catalog
- **Login**: http://localhost:5000/auth/login
- **Register**: http://localhost:5000/auth/register

## Default Credentials

**Admin Account** (create via Python shell):
```python
python
>>> from app import app, db
>>> from models import User
>>> with app.app_context():
...     admin = User(email='admin@ubuyu.local', username='admin', full_name='Admin', role='admin')
...     admin.set_password('admin123')
...     db.session.add(admin)
...     db.session.commit()
>>> exit()
```

Then login at http://localhost:5000/auth/login

## Key Features

✅ **User Registration & Authentication**
- Secure password hashing
- Role-based access (customer, vendor, admin)

✅ **Product Catalog**
- Search and filter products
- Advanced filtering (price, category, vendor)
- Product detail pages with reviews

✅ **Shopping Cart**
- localStorage-based cart
- Add/remove items
- Checkout system

✅ **Vendor Dashboard**
- Sell your ubuyu products
- Manage inventory
- Track orders and earnings

✅ **Admin Panel**
- Manage users and vendors
- Approve vendor applications
- View all orders

✅ **Modern Design**
- Vibrant African colors (red, orange, yellow, brown)
- Netflix-inspired UI
- Fully responsive mobile design
- Smooth animations

✅ **Communication**
- Private messaging system
- Floating chat widget
- Notifications bell
- WhatsApp order integration

## File Structure

```
marketplace/
├── app.py               ← Start here!
├── config.py            ← Settings
├── models.py            ← Database models
├── requirements.txt     ← Dependencies
│
├── routes/              ← Page handlers
├── templates/           ← HTML pages
├── static/
│   ├── css/style.css    ← Modern styling
│   └── js/main.js       ← JavaScript
└── README.md            ← Full documentation
```

## Database

By default uses **SQLite** (`ubuyu.db`). To use MySQL:

Edit `config.py`:
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@localhost/ubuyu'
```

## Deployment

Ready for deployment on:
- **Heroku** (just add Procfile)
- **Render.com** (free tier available)
- **AWS**, **Google Cloud**, **DigitalOcean**, etc.

See README.md for detailed deployment guide.

## All Pages Included

**Public Pages:**
- ✅ Landing page with featured products
- ✅ Product catalog with filters
- ✅ Product detail pages
- ✅ Login & Registration
- ✅ About, Contact pages

**Customer Pages:**
- ✅ Shopping cart
- ✅ Checkout
- ✅ Order history & tracking
- ✅ User profile
- ✅ Message inbox
- ✅ Notifications

**Vendor Pages:**
- ✅ Vendor dashboard with stats
- ✅ Add/edit/delete products
- ✅ Order management
- ✅ Earnings tracking
- ✅ Store settings

**Admin Pages:**
- ✅ Admin dashboard with analytics
- ✅ User management
- ✅ Vendor approval system
- ✅ Product management
- ✅ Order overview

## Customization

### Change Colors
Edit `static/css/style.css` CSS variables:
```css
--primary-red: #d32f2f;
--primary-orange: #f57c00;
--primary-yellow: #fbc02d;
--primary-brown: #8d6e63;
```

### Change Store Name
Edit `templates/base.html`:
```html
<a href="/" class="logo">🍬 Your Store Name</a>
```

### Add More Products
Add sample data in Python:
```python
from app import app, db
from models import User, Vendor, Product

with app.app_context():
    vendor = Vendor.query.first()
    if vendor:
        p = Product(
            vendor_id=vendor.id,
            name="Premium Ubuyu",
            slug="premium-ubuyu",
            price=250,
            stock=100
        )
        db.session.add(p)
        db.session.commit()
```

## Next Steps

1. **Test the application** - Browse products, add to cart, checkout
2. **Create a vendor account** - Add products and list them
3. **Test admin panel** - Approve vendors, manage orders
4. **Customize design** - Update colors, logos, content
5. **Deploy** - Push to Heroku/Render for production

## Troubleshooting

**Port 5000 already in use?**
```bash
python app.py --port 8000
```

**Database errors?**
```bash
rm ubuyu.db
python app.py  # Will recreate database
```

**Missing template?**
Check that templates are in `templates/` folder with correct path in routes.

## Support

- Read full README.md for detailed documentation
- All code is commented and self-explanatory
- Use Flask's debug mode for troubleshooting

---

🎉 **Congratulations!** You now have a full-featured marketplace ready to scale. Happy selling!
