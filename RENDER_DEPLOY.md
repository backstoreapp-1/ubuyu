# Ubuyu Marketplace - Render Deployment Guide

## Prerequisites
- GitHub account with your repository pushed
- Render account (https://render.com)

## Deployment Steps

### 1. Push to GitHub
```bash
cd /home/shakes/Desktop/ubuyu/marketplace
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ubuyu.git
git push -u origin main
```

### 2. Create Render Account & Connect GitHub
- Visit https://render.com and sign up
- Connect your GitHub account in the dashboard

### 3. Deploy Using render.yaml (Recommended)
1. Go to Render Dashboard → Create New → Blueprint
2. Select your GitHub repository
3. Enter repository URL with `render.yaml` in root
4. Render will auto-detect and deploy all services

### 4. Manual Setup (Alternative)
1. Go to Render Dashboard → Create New → Web Service
2. Select "GitHub" and choose your repository
3. Configure:
   - **Name**: ubuyu-marketplace
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT --timeout 120 'app:create_app("production")'`
   - **Plan**: Free (or paid)

### 5. Set Environment Variables
In Render Dashboard → Your Service → Environment:
- `FLASK_ENV`: production
- `SECRET_KEY`: [auto-generated or enter secure key]
- `DATABASE_URL`: [Render PostgreSQL connection string]

### 6. Add PostgreSQL Database
1. Create New → PostgreSQL
2. Name it: `ubuyu-db`
3. Copy the connection string
4. Add to Web Service Environment as `DATABASE_URL`

### 7. Initialize Database
1. Go to your service dashboard
2. Click "Shell"
3. Run:
```bash
flask db upgrade
# or manually:
python3 -c "from app import create_app, db; app = create_app('production'); db.create_all()"
```

### 8. Monitor Deployment
- View logs in Render Dashboard
- Check health status
- Monitor file uploads (uploads folder needs persistence)

## Important Notes
- **Free tier**: Will spin down after 15 minutes of inactivity
- **Uploads**: Store on external service (AWS S3, Render Disks, etc.)
- **Database**: Free PostgreSQL included with `render.yaml`
- **SSL**: Automatic HTTPS enabled
- **CORS**: Configured for public access

## Production Checklist
- [ ] Change `SECRET_KEY` in environment variables
- [ ] Set `SESSION_COOKIE_SECURE = True` (already done in config)
- [ ] Use PostgreSQL (not SQLite)
- [ ] Enable HTTPS (automatic on Render)
- [ ] Configure file upload storage
- [ ] Set up monitoring/alerts
- [ ] Test email notifications if applicable
- [ ] Backup database regularly

## Troubleshooting

**App won't start?**
- Check logs in Render Dashboard
- Verify `Procfile` and `render.yaml` format
- Ensure all imports work: `python3 -c "from app import create_app"`

**Database connection error?**
- Verify `DATABASE_URL` environment variable is set
- Check PostgreSQL service is running
- Ensure migrations/tables exist

**Uploads not persisting?**
- Free tier doesn't persist files to disk
- Configure uploads to Render Disk or cloud storage

---

For more info: https://render.com/docs
