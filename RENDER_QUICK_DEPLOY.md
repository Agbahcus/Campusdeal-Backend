# 🚀 RENDER DEPLOYMENT - READY TO GO (10 MINUTES)

## ✅ ALL FIXES APPLIED - DEPLOY NOW!

---

## ⚡ QUICK DEPLOY (10 MINUTES)

### Step 1: Push to GitHub (1 min)
```bash
git add .
git commit -m "Production ready"
git push origin main
```

### Step 2: Create Render Account (2 min)
1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render

### Step 3: Create PostgreSQL Database (2 min)
1. Dashboard → "New +" → "PostgreSQL"
2. Name: `campusdeal-db`
3. Region: **Frankfurt**
4. Plan: **Free**
5. **Copy Internal Database URL** : postgresql://campusdeal_db_user:68QlknibnoHZDM67S90VQZN9iEhElFZd@dpg-d7tu6hbbc2fs73eu2g70-a/campusdeal_db

### Step 4: Create Web Service (3 min)
1. Dashboard → "New +" → "Web Service"
2. Connect repo: `campusdeal-backend`
3. Build Command:
   ```
   pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
   ```
4. Start Command:
   ```
   gunicorn campusdeal.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120
   ```

### Step 5: Add Environment Variables (2 min)

**IMPORTANT:** Get your actual values from your local `.env` file

```
SECRET_KEY=[FROM_YOUR_.ENV]
DEBUG=False
ALLOWED_HOSTS=.onrender.com
DATABASE_URL=[FROM_STEP_3]
FRONTEND_URL=https://campusdeal.vercel.app
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://campusdeal.vercel.app
PAYSTACK_SECRET_KEY=[FROM_YOUR_.ENV]
PAYSTACK_PUBLIC_KEY=[FROM_YOUR_.ENV]
SENDCHAMP_PUBLIC_KEY=[FROM_YOUR_.ENV]
SENDCHAMP_SECRET_KEY=[FROM_YOUR_.ENV]
SENDCHAMP_SENDER_ID=Sendchamp
SENDCHAMP_BASE_URL=https://api.sendchamp.com/api/v1
CLOUDINARY_CLOUD_NAME=[FROM_YOUR_.ENV]
CLOUDINARY_API_KEY=[FROM_YOUR_.ENV]
CLOUDINARY_API_SECRET=[FROM_YOUR_.ENV]
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
PYTHON_VERSION=3.11.0
```

---

## 🧪 TEST DEPLOYMENT

```bash
curl https://campusdeal-backend.onrender.com/health/
```

**Status:** ✅ READY TO DEPLOY  
**Time:** 10 minutes  
**Cost:** FREE (90 days)
