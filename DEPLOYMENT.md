# Deployment Guide for Vercel

This guide will help you deploy your Flask portfolio application to Vercel.

## 📋 Pre-Deployment Checklist

- [ ] Database set up (MySQL recommended)
- [ ] Environment variables ready
- [ ] All dependencies in `requirements.txt`
- [ ] Code is pushed to GitHub
- [ ] Vercel account created

## 🗄️ Database Setup

### Option 1: PlanetScale (Recommended for Vercel)

PlanetScale is MySQL-compatible and serverless-friendly:

1. Sign up at [planetscale.com](https://planetscale.com)
2. Create a new database
3. Get your connection string from the dashboard
4. Format: `mysql+pymysql://username:password@host:port/database?ssl-mode=REQUIRED`

### Option 2: Railway

1. Sign up at [railway.app](https://railway.app)
2. Create a new MySQL database
3. Get connection string from the database settings

### Option 3: AWS RDS

1. Create an RDS MySQL instance
2. Configure security groups to allow connections
3. Get connection string from RDS dashboard

### Option 4: Supabase (PostgreSQL)

If using PostgreSQL, you'll need to:
1. Change `PyMySQL` to `psycopg2-binary` in `requirements.txt`
2. Update `DATABASE_URL` format to PostgreSQL
3. Update SQLAlchemy connection string

## 🚀 Vercel Deployment Steps

### Step 1: Prepare Your Repository

1. Ensure all changes are committed:
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

### Step 2: Create Vercel Project

1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Vercel will auto-detect the project settings

### Step 3: Configure Environment Variables

In Vercel project settings, add these environment variables:

```
SECRET_KEY=your-random-secret-key-here
DATABASE_URL=mysql+pymysql://user:pass@host:port/db?charset=utf8mb4
SESSION_COOKIE_SECURE=true
```

**Important:**
- Generate a strong `SECRET_KEY` (use `python -c "import secrets; print(secrets.token_hex(32))"`)
- Set `SESSION_COOKIE_SECURE=true` for HTTPS (required in production)
- Use your production database URL

### Step 4: Deploy

1. Click "Deploy"
2. Wait for the build to complete
3. Your app will be available at `https://your-project.vercel.app`

### Step 5: Initialize Database

After first deployment:

1. Visit your app URL
2. The database tables will be created automatically
3. Or visit `/signup` to create your first user
4. Update the user role to 'admin' in your database:

```sql
UPDATE user SET role='admin' WHERE email='your-email@example.com';
```

## 🔧 Vercel Configuration

The `vercel.json` file is already configured:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

This configuration:
- Uses `api/index.py` as the serverless function entry point
- Routes all requests to the Flask app
- Serves static files from `/static`

## 📁 Project Structure for Vercel

```
portfolio_flask/
├── api/
│   └── index.py          # Vercel entry point
├── app.py                # Main Flask app
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
└── ... (other files)
```

## 🔍 Troubleshooting

### Database Connection Issues

**Problem:** Cannot connect to database

**Solutions:**
- Check `DATABASE_URL` format
- Ensure database allows connections from Vercel IPs
- For PlanetScale, use the connection pooling URL
- Check if SSL is required (add `?ssl-mode=REQUIRED`)
- Verify database credentials

### Import Errors

**Problem:** Module not found errors

**Solutions:**
- Ensure all dependencies are in `requirements.txt`
- Check that `api/index.py` imports correctly
- Verify Python path configuration

### Session Issues

**Problem:** Sessions not working

**Solutions:**
- Ensure `SECRET_KEY` is set
- Set `SESSION_COOKIE_SECURE=true` for HTTPS
- Clear browser cookies
- Check session cookie settings in `app.py`

### Static Files Not Loading

**Problem:** CSS/JS/images not loading

**Solutions:**
- Ensure static files are in `/static` directory
- Check file paths in templates
- Verify Vercel is serving static files correctly
- Check browser console for 404 errors

### Cold Start Issues

**Problem:** Slow first request

**Solutions:**
- This is normal for serverless functions
- Consider using Vercel Pro for faster cold starts
- Optimize database queries
- Use connection pooling (already configured)

## 🔒 Security Considerations

1. **Environment Variables**: Never commit `.env` files
2. **SECRET_KEY**: Use a strong, random secret key
3. **Database**: Use SSL connections in production
4. **Sessions**: Enable secure cookies for HTTPS
5. **API Keys**: Store in environment variables
6. **CORS**: Configure CORS properly for your domain

## 📊 Monitoring

After deployment:

1. Check Vercel logs for errors
2. Monitor database connections
3. Set up error tracking (Sentry, etc.)
4. Monitor API usage and performance

## 🔄 Updating Your Deployment

To update your deployed app:

1. Make changes to your code
2. Commit and push to GitHub
3. Vercel will automatically redeploy
4. Check deployment logs for any issues

## 📝 Additional Notes

### File Storage

- HTML and ESP8266 code are stored in the database
- Static images should be uploaded to external storage (S3, Cloudinary)
- File uploads in admin panel need external storage for production

### Real-time Data

- The `latest_data` dictionary is per-serverless-instance
- For production, consider using Redis or database for shared state
- Current implementation works but may have inconsistencies across instances

### Database Migrations

- Tables are auto-created on first request
- For production, consider using Flask-Migrate for schema management
- Backup your database regularly

## 🆘 Getting Help

If you encounter issues:

1. Check Vercel deployment logs
2. Check database connection
3. Verify environment variables
4. Check application logs
5. Open an issue on GitHub

## 🎉 Success!

Once deployed, your app will be available at:
- Production: `https://your-project.vercel.app`
- Preview: `https://your-project-git-branch.vercel.app`

Your Flask portfolio is now live on Vercel! 🚀

