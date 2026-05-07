# ⚡ DEPLOY TO RENDER NOW - 10 MINUTE GUIDE

## 🎯 YOU'RE 10 MINUTES AWAY FROM GOING LIVE!

All fixes are done. Just follow these steps.

---

## ✅ PRE-FLIGHT CHECK

- [x] Sendchamp SMS configured
- [x] Cloudinary media storage configured
- [x] Production security enabled
- [x] Health checks added
- [x] All credentials ready
- [x] Code is production-ready

**Status:** READY TO DEPLOY! 🚀

---

## 📋 10-MINUTE DEPLOYMENT

### ⏱️ Step 1: Push to GitHub (1 min)

```bash
cd c:\Users\divin\campusdeal-backend
git add .
git commit -m "Production ready: All fixes applied"
git push origin main
```

---

### ⏱️ Step 2: Create Render Account (1 min)

1. Go to: https://render.com
2. Click "Get Started"
3. Click "Sign up with GitHub"
4. Authorize Render

---

### ⏱️ Step 3: Create Database (2 min)

1. Click "New +" → "PostgreSQL"
2. Fill in:
   - Name: `campusdeal-db`
   - Database: `campusdeal`
   - User: `campusdeal`
   - Region: **Frankfurt**
   - Version: **15**
3. Plan: **Free**
4. Click "Create Database"
5. **COPY** the "Internal Database URL" (you'll need it in Step 5)

---

### ⏱️ Step 4: Create Web Service (2 min)

1. Click "New +" → "Web Service"
2. Click "Connect account" (if needed)
3. Find and select: **campusdeal-backend**
4. Click "Connect"
5. Fill in:
   - Name: `campusdeal-backend`
   - Region: **Frankfurt**
   - Branch: `main`
   - Runtime: **Python 3**
   - Build Command:
     ```
     pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
     ```
   - Start Command:
     ```
     gunicorn campusdeal.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120
     ```
6. Plan: **Free**
7. **DON'T CLICK CREATE YET** - Go to Step 5 first

---

### ⏱️ Step 5: Add Environment Variables (3 min)

Scroll down to "Environment Variables" section and add these:

**Click "Add Environment Variable" for each:**

```
Key: SECRET_KEY
Value: ql=jryij0+@(6n165q$dqe7@fwh30z-$fe!brxz5v67y0e##x&

Key: DEBUG
Value: False

Key: ALLOWED_HOSTS
Value: .onrender.com

Key: DATABASE_URL
Value: [PASTE THE URL FROM STEP 3]

Key: FRONTEND_URL
Value: https://campusdeal.vercel.app

Key: CORS_ALLOWED_ORIGINS
Value: http://localhost:3000,https://campusdeal.vercel.app

Key: PAYSTACK_SECRET_KEY
Value: [YOUR_PAYSTACK_SECRET_KEY]

Key: PAYSTACK_PUBLIC_KEY
Value: [YOUR_PAYSTACK_PUBLIC_KEY]

Key: SENDCHAMP_PUBLIC_KEY
Value: [YOUR_SENDCHAMP_PUBLIC_KEY]

Key: SENDCHAMP_SECRET_KEY
Value: [YOUR_SENDCHAMP_SECRET_KEY]

Key: SENDCHAMP_SENDER_ID
Value: Sendchamp

Key: SENDCHAMP_BASE_URL
Value: https://api.sendchamp.com/api/v1

Key: CLOUDINARY_CLOUD_NAME
Value: campusdeal

Key: CLOUDINARY_API_KEY
Value: [YOUR_CLOUDINARY_API_KEY]

Key: CLOUDINARY_API_SECRET
Value: [YOUR_CLOUDINARY_API_SECRET]

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

### ⏱️ Step 6: Wait for Deployment (5 min)

1. You'll see the "Logs" tab automatically
2. Watch the build process:
   - Installing dependencies...
   - Collecting static files...
   - Running migrations...
   - Starting server...
3. Wait for: **"Your service is live 🎉"**

**Your URL:** `https://campusdeal-backend.onrender.com`

---

### ⏱️ Step 7: Test Deployment (1 min)

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

## 🎉 YOU'RE LIVE!

**Backend URL:** https://campusdeal-backend.onrender.com  
**Admin Panel:** https://campusdeal-backend.onrender.com/admin/  
**Health Check:** https://campusdeal-backend.onrender.com/health/

---

## 🔧 POST-DEPLOYMENT (5 minutes)

### Create Superuser

1. In Render dashboard, click "Shell" tab
2. Run:
```bash
python manage.py createsuperuser
```
3. Follow prompts:
   - Username: `admin`
   - Email: `your-email@example.com`
   - Password: (choose strong password)

### Test Admin Panel

Go to: https://campusdeal-backend.onrender.com/admin/  
Login with your superuser credentials

### Test API Endpoints

**List Categories:**
```
GET https://campusdeal-backend.onrender.com/api/marketplace/categories/
```

**Register User (Test SMS):**
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

**Check your phone for SMS!**

---

## 🔗 UPDATE FRONTEND

Update your frontend `.env`:

```
NEXT_PUBLIC_API_URL=https://campusdeal-backend.onrender.com
```

Or in Vercel dashboard:
- Go to Settings → Environment Variables
- Update `API_URL` to: `https://campusdeal-backend.onrender.com`
- Redeploy frontend

---

## ⚠️ IMPORTANT NOTES

### 1. Sleep After 15 Minutes
- App sleeps after 15 min of inactivity
- First request after sleep: 30-50 seconds
- **Workaround:** Set up a cron job to ping `/health/` every 10 minutes

### 2. Free for 90 Days
- After 90 days: $7/month for web + $7/month for database
- You have time to migrate to Appliku+Hetzner (cheaper)

### 3. Using LIVE Credentials
- Paystack: LIVE keys (real money)
- Sendchamp: LIVE keys (real SMS charges)
- Test carefully!

---

## 🐛 TROUBLESHOOTING

### Build Failed?
- Check logs in Render dashboard
- Common issues:
  - Missing dependency in requirements.txt
  - Syntax error in code
  - Database connection failed

### Health Check Fails?
- Check DATABASE_URL is correct
- Verify database is running
- Check logs for errors

### SMS Not Sending?
- Verify Sendchamp balance
- Check SENDCHAMP_SECRET_KEY
- Look for errors in logs

### Images Not Uploading?
- Verify Cloudinary credentials
- Check CLOUDINARY_CLOUD_NAME
- Test in Cloudinary dashboard

---

## 📊 MONITORING

### View Logs
Render Dashboard → Your Service → Logs

### Check Health
```bash
curl https://campusdeal-backend.onrender.com/health/
```

### Monitor Performance
Render Dashboard → Your Service → Metrics

---

## 🎯 NEXT STEPS

1. ✅ Test all API endpoints
2. ✅ Connect frontend
3. ✅ Test with real users
4. ✅ Monitor logs for errors
5. ⏳ Set up Appliku+Hetzner in parallel
6. ⏳ Plan migration before day 90

---

## 📞 NEED HELP?

**Render Support:**
- Docs: https://render.com/docs
- Community: https://community.render.com
- Email: support@render.com

**Your Documentation:**
- `RENDER_QUICK_DEPLOY.md` - Detailed guide
- `DEPLOYMENT_STRATEGY.md` - Migration plan
- `DEPLOYMENT_READY.md` - All fixes applied

---

## ✅ DEPLOYMENT CHECKLIST

- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] PostgreSQL database created
- [ ] Web service created
- [ ] Environment variables added
- [ ] Deployment successful (see "Your service is live")
- [ ] Health check returns 200
- [ ] Superuser created
- [ ] Admin panel accessible
- [ ] API endpoints working
- [ ] SMS sending tested
- [ ] Image upload tested
- [ ] Frontend connected
- [ ] Test users invited

---

**Time Taken:** 10 minutes  
**Cost:** FREE (90 days)  
**Status:** LIVE! 🎉

**Now go deploy!** 🚀
