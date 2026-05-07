# 🚀 RENDER DEPLOYMENT - 10 MINUTE GUIDE

## ⚡ QUICK DEPLOY

### Step 1: Push to GitHub ✅ DONE!

Your code is already on GitHub.

---

### Step 2: Create Render Account (2 min)

1. Go to: **https://render.com**
2. Click **"Get Started"**
3. Click **"Sign up with GitHub"**
4. Authorize Render to access your repositories

---

### Step 3: Create PostgreSQL Database (2 min)

1. In Render Dashboard, click **"New +"** (top right)
2. Select **"PostgreSQL"**
3. Fill in:
   - **Name:** `campusdeal-db`
   - **Database:** `campusdeal`
   - **User:** `campusdeal`
   - **Region:** `Frankfurt` (closest to Nigeria)
   - **PostgreSQL Version:** `15`
4. **Instance Type:** Select **"Free"**
5. Click **"Create Database"**
6. Wait 1-2 minutes for provisioning
7. **IMPORTANT:** Copy the **"Internal Database URL"** (you'll need it in Step 5)
   - It looks like: `postgresql://campusdeal:xxxxx@dpg-xxxxx/campusdeal`

---

### Step 4: Create Web Service (3 min)

1. In Render Dashboard, click **"New +"** (top right)
2. Select **"Web Service"**
3. Click **"Build and deploy from a Git repository"**
4. Click **"Connect account"** (if you haven't connected GitHub yet)
5. Find your repository: **"campusdeal-backend"** or **"Campusdeal-Backend"**
6. Click **"Connect"** next to your repository

**Configure the service:**

- **Name:** `campusdeal-backend`
- **Region:** `Frankfurt`
- **Branch:** `main`
- **Root Directory:** (leave blank)
- **Runtime:** `Python 3`
- **Build Command:**
  ```
  pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
  ```
- **Start Command:**
  ```
  gunicorn campusdeal.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120
  ```
- **Instance Type:** Select **"Free"**

**DON'T CLICK "Create Web Service" YET** - Scroll down to add environment variables first!

---

### Step 5: Add Environment Variables (3 min)

**Scroll down to "Environment Variables" section**

Click **"Add Environment Variable"** and add each of these:

**Copy values from your local `.env` file:**

```
Key: SECRET_KEY
Value: [Copy from your .env file]

Key: DEBUG
Value: False

Key: ALLOWED_HOSTS
Value: .onrender.com

Key: DATABASE_URL
Value: [Paste the Internal Database URL from Step 3]

Key: FRONTEND_URL
Value: https://campusdeal.vercel.app

Key: CORS_ALLOWED_ORIGINS
Value: http://localhost:3000,https://campusdeal.vercel.app

Key: PAYSTACK_SECRET_KEY
Value: [Copy from your .env file]

Key: PAYSTACK_PUBLIC_KEY
Value: [Copy from your .env file]

Key: SENDCHAMP_PUBLIC_KEY
Value: [Copy from your .env file]

Key: SENDCHAMP_SECRET_KEY
Value: [Copy from your .env file]

Key: SENDCHAMP_SENDER_ID
Value: Sendchamp

Key: SENDCHAMP_BASE_URL
Value: https://api.sendchamp.com/api/v1

Key: CLOUDINARY_CLOUD_NAME
Value: [Copy from your .env file]

Key: CLOUDINARY_API_KEY
Value: [Copy from your .env file]

Key: CLOUDINARY_API_SECRET
Value: [Copy from your .env file]

Key: SECURE_SSL_REDIRECT
Value: True

Key: SESSION_COOKIE_SECURE
Value: True

Key: CSRF_COOKIE_SECURE
Value: True

Key: PYTHON_VERSION
Value: 3.11.0
```

**NOW CLICK "Create Web Service"**

---

### Step 6: Wait for Deployment (5 min)

1. You'll automatically see the **"Logs"** tab
2. Watch the deployment process:
   - `==> Cloning from https://github.com/...`
   - `==> Installing dependencies...`
   - `==> Collecting static files...`
   - `==> Running migrations...`
   - `==> Starting server...`
3. Wait for: **"Your service is live 🎉"**

**Your URL will be:** `https://campusdeal-backend.onrender.com`

---

### Step 7: Test Your Deployment (1 min)

**Test Health Check:**
```bash
curl https://campusdeal-backend.onrender.com/health/
```

**Expected Response:**
```json
{
  "status": "healthy",
  "checks": {
    "database": "connected",
    "configuration": "ok"
  }
}
```

**If you see this, YOU'RE LIVE! 🎉**

---

## 🔧 POST-DEPLOYMENT (5 minutes)

### Create Superuser

1. In Render dashboard, go to your web service
2. Click **"Shell"** tab (left sidebar)
3. Wait for shell to connect
4. Run:
```bash
python manage.py createsuperuser
```
5. Follow prompts:
   - Username: `admin`
   - Email: `your-email@example.com`
   - Password: (choose strong password)

### Test Admin Panel

Go to: **https://campusdeal-backend.onrender.com/admin/**  
Login with your superuser credentials

### Test API

**List Categories:**
```
GET https://campusdeal-backend.onrender.com/api/marketplace/categories/
```

**Test Registration (SMS):**
```bash
curl -X POST https://campusdeal-backend.onrender.com/api/accounts/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "email": "test@example.com",
    "phone_number": "+2348012345678",
    "password": "TestPass123",
    "primary_location": "ilorin"
  }'
```

**Check your phone for SMS verification code!**

---

## 🔗 UPDATE FRONTEND

Update your frontend environment variables:

**In Vercel Dashboard:**
1. Go to your frontend project
2. Settings → Environment Variables
3. Update or add:
   ```
   NEXT_PUBLIC_API_URL=https://campusdeal-backend.onrender.com
   ```
4. Redeploy frontend

---

## ⚠️ IMPORTANT NOTES

### 1. Free Tier Limitations
- **Sleeps after 15 minutes** of inactivity
- First request after sleep: 30-50 seconds
- Subsequent requests: Normal speed
- **Workaround:** Use cron-job.org to ping `/health/` every 10 minutes

### 2. Free for 90 Days
- After 90 days: $7/month for web service + $7/month for database
- Total: $14/month (₦22,400)
- You have time to migrate to Appliku+Hetzner (cheaper)

### 3. Using LIVE Credentials
- Paystack: LIVE keys (real money transactions)
- Sendchamp: LIVE keys (real SMS charges)
- Test carefully before going fully public!

---

## 🐛 TROUBLESHOOTING

### Build Failed?
**Check logs for:**
- Missing dependencies → Check `requirements.txt`
- Syntax errors → Check recent code changes
- Database connection → Verify DATABASE_URL

### Health Check Fails?
- Verify DATABASE_URL is correct
- Check database is running (Render Dashboard → Database)
- Look for errors in logs

### SMS Not Sending?
- Check Sendchamp balance: https://my.sendchamp.com
- Verify SENDCHAMP_SECRET_KEY is correct
- Check logs for SMS errors

### Images Not Uploading?
- Verify Cloudinary credentials
- Test in Cloudinary dashboard: https://cloudinary.com/console
- Check CLOUDINARY_CLOUD_NAME matches

---

## 📊 MONITORING

### View Logs
Render Dashboard → Your Service → **Logs** tab

### Check Health
```bash
curl https://campusdeal-backend.onrender.com/health/
```

### Monitor Performance
Render Dashboard → Your Service → **Metrics** tab

---

## ✅ DEPLOYMENT CHECKLIST

- [x] Code pushed to GitHub
- [ ] Render account created
- [ ] PostgreSQL database created
- [ ] Web service created
- [ ] Environment variables added
- [ ] Deployment successful
- [ ] Health check returns 200
- [ ] Superuser created
- [ ] Admin panel accessible
- [ ] API endpoints working
- [ ] SMS sending tested
- [ ] Image upload tested
- [ ] Frontend connected

---

## 🎯 YOUR URLS

**Backend API:** https://campusdeal-backend.onrender.com  
**Admin Panel:** https://campusdeal-backend.onrender.com/admin/  
**Health Check:** https://campusdeal-backend.onrender.com/health/  
**API Docs:** See `API_DOCUMENTATION.md`

---

## 📞 NEED HELP?

**Render Support:**
- Docs: https://render.com/docs
- Community: https://community.render.com
- Email: support@render.com

**Your Documentation:**
- `DEPLOYMENT_READY.md` - All fixes applied
- `DEPLOYMENT_STRATEGY.md` - Migration plan to Appliku

---

**Status:** ✅ READY TO DEPLOY  
**Time:** 10 minutes  
**Cost:** FREE (90 days)

**Now go deploy!** 🚀
