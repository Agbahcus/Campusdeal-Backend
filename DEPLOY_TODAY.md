# 🚀 DEPLOY TODAY - EMERGENCY GUIDE

Get CampusDeal live in 2 hours without waiting for approvals!

---

## ⚡ STRATEGY: Deploy with Test Mode First

You can deploy TODAY and switch to live mode later when approvals come through.

**What works in Test Mode:**
- ✅ All features functional
- ✅ Real users can register
- ✅ Real listings can be created
- ✅ Orders can be placed
- ✅ SMS works (with temporary sender)
- ⚠️ Payments use test cards (switch to live later)

---

## 🎯 2-HOUR DEPLOYMENT PLAN

### **Hour 1: Setup Accounts (60 minutes)**

#### 1. Paystack (15 min) - USE TEST MODE
```
1. Go to: https://paystack.com
2. Sign up (2 min)
3. Verify email (1 min)
4. Go to Settings → API Keys
5. Copy TEST keys (no KYC needed!)
   - Test Secret: sk_test_xxxxx
   - Test Public: pk_test_xxxxx
6. Set webhook: https://yourdomain.com/api/marketplace/payments/webhook/
7. Copy webhook secret

✅ DONE - You can process test payments immediately!
```

#### 2. Sendchamp (10 min) - USE DEFAULT SENDER
```
1. Go to: https://www.sendchamp.com
2. Sign up (2 min)
3. Verify email (1 min)
4. Copy API keys (no approval needed!)
   - Public: sendchamp_pk_xxxxx
   - Secret: sendchamp_sk_xxxxx
5. Fund wallet: ₦5,000 (2 min)
6. Use "Sendchamp" as sender (pre-approved!)

✅ DONE - SMS works immediately!
```

#### 3. Cloudinary (10 min)
```
1. Go to: https://cloudinary.com/users/register/free
2. Sign up (2 min)
3. Copy credentials (instant!)
   - Cloud Name: campusdeal
   - API Key: xxxxx
   - API Secret: xxxxx
4. Create upload preset: campusdeal_items

✅ DONE - Image uploads work immediately!
```

#### 4. Railway Database (10 min)
```
1. Go to: https://railway.app
2. Sign up with GitHub (1 min)
3. New Project → Provision PostgreSQL (2 min)
4. Copy DATABASE_URL (instant!)

✅ DONE - Database ready immediately!
```

#### 5. Create .env file (15 min)
```bash
# Copy .env.example to .env
cp .env.example .env

# Edit with your values
nano .env
```

---

### **Hour 2: Deploy to Railway (60 minutes)**

#### Step 1: Prepare Code (10 min)

```bash
# 1. Update requirements.txt
pip freeze > requirements.txt

# 2. Create Procfile
echo "web: gunicorn campusdeal.wsgi --log-file -" > Procfile

# 3. Create runtime.txt
echo "python-3.11.0" > runtime.txt

# 4. Install gunicorn
pip install gunicorn
pip freeze > requirements.txt

# 5. Collect static files
python manage.py collectstatic --noinput
```

#### Step 2: Push to GitHub (10 min)

```bash
# Initialize git (if not done)
git init
git add .
git commit -m "Ready for deployment"

# Create GitHub repo
# Go to: https://github.com/new
# Name: campusdeal-backend
# Create repository

# Push code
git remote add origin https://github.com/yourusername/campusdeal-backend.git
git branch -M main
git push -u origin main
```

#### Step 3: Deploy on Railway (20 min)

```
1. Go to: https://railway.app/dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose: campusdeal-backend
5. Railway auto-detects Django!

6. Add Environment Variables:
   - Click "Variables" tab
   - Add all from .env file:
     * SECRET_KEY
     * DEBUG=False
     * ALLOWED_HOSTS=*.railway.app
     * DATABASE_URL (already set)
     * PAYSTACK_SECRET_KEY
     * PAYSTACK_PUBLIC_KEY
     * SENDCHAMP_SECRET_KEY
     * SENDCHAMP_PUBLIC_KEY
     * SENDCHAMP_SENDER_ID=Sendchamp
     * CLOUDINARY_CLOUD_NAME
     * CLOUDINARY_API_KEY
     * CLOUDINARY_API_SECRET
     * FRONTEND_URL=https://yourfrontend.vercel.app

7. Click "Deploy"
8. Wait 3-5 minutes for build

9. Get your URL: https://campusdeal-backend-production.up.railway.app
```

#### Step 4: Run Migrations (10 min)

```bash
# Railway gives you a shell
# Click "..." → "Shell"

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
# Username: admin
# Email: admin@campusdeal.com
# Password: (strong password)

# Create categories
python manage.py shell
```

```python
from marketplace.models import ItemCategory

categories = [
    'Electronics', 'Books', 'Clothing', 'Furniture',
    'Phones', 'Laptops', 'Accessories', 'Other'
]

for cat in categories:
    ItemCategory.objects.get_or_create(name=cat)

exit()
```

#### Step 5: Test Everything (10 min)

```bash
# Test API is live
curl https://your-app.railway.app/api/auth/health/

# Test admin panel
# Go to: https://your-app.railway.app/admin/
# Login with superuser credentials

# Test registration
curl -X POST https://your-app.railway.app/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "phone_number": "+2348012345678",
    "password": "Test1234",
    "first_name": "Test",
    "last_name": "User"
  }'
```

---

## ✅ YOU'RE LIVE! 🎉

Your backend is now deployed at:
```
https://campusdeal-backend-production.up.railway.app
```

---

## 🔄 SWITCHING TO LIVE MODE LATER

When Paystack KYC is approved (1-3 days):

```bash
# 1. Get Live Keys from Paystack
# Dashboard → Settings → API Keys → Toggle "Live"

# 2. Update Railway Environment Variables
# Go to Railway → Variables
# Update:
PAYSTACK_SECRET_KEY=sk_live_xxxxx  # Change from sk_test_
PAYSTACK_PUBLIC_KEY=pk_live_xxxxx  # Change from pk_test_

# 3. Redeploy (automatic)
# Railway will restart with new keys

# 4. Update Sendchamp Sender ID (when approved)
SENDCHAMP_SENDER_ID=CampusDeal  # Change from "Sendchamp"
```

---

## 📱 CONNECT FRONTEND

Update your frontend .env:

```env
NEXT_PUBLIC_API_URL=https://campusdeal-backend-production.up.railway.app
NEXT_PUBLIC_PAYSTACK_PUBLIC_KEY=pk_test_xxxxx  # Your test key for now
```

---

## 🧪 TEST WITH REAL USERS

**Test Mode Limitations:**
- Payments require test cards (not real money)
- Withdrawals go to test bank accounts

**Test Cards (Paystack):**
```
Success: 4084084084084081
Decline: 4084080000000408
Insufficient: 4084084084084081 (amount > 100000)
```

**How to Test:**
1. Register real users
2. Create real listings
3. Place orders with test cards
4. Test SMS notifications
5. Test wallet & withdrawals (test mode)

**When Live Keys Active:**
- Everything switches to real money automatically
- No code changes needed!

---

## 💰 COSTS (Test Mode)

**Today:**
- Railway: FREE (500MB database)
- Sendchamp: ₦5,000 (one-time top-up)
- Cloudinary: FREE
- Paystack: FREE (test mode)
- **Total: ₦5,000**

**After Going Live:**
- Railway: $5/month (₦7,500)
- Sendchamp: ₦3,000/month (1,000 users)
- Paystack: 1.5% per transaction
- **Total: ₦10,500/month + transaction fees**

---

## 🚨 EMERGENCY TROUBLESHOOTING

### Build Fails on Railway
```bash
# Check logs in Railway dashboard
# Common issues:

# 1. Missing gunicorn
pip install gunicorn
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Add gunicorn"
git push

# 2. Wrong Python version
# Edit runtime.txt:
echo "python-3.11.0" > runtime.txt
git add runtime.txt
git commit -m "Fix Python version"
git push

# 3. Static files error
# Add to settings.py:
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

### Database Connection Error
```bash
# Railway sets DATABASE_URL automatically
# Just ensure settings.py has:
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600
    )
}
```

### SMS Not Sending
```bash
# Check Sendchamp wallet balance
# Go to: https://my.sendchamp.com/wallet

# Verify phone format: +234XXXXXXXXXX (not 0XXXXXXXXXX)

# Use "Sendchamp" as sender (not "CampusDeal" until approved)
```

### CORS Errors
```bash
# Add to settings.py:
CORS_ALLOWED_ORIGINS = [
    "https://yourfrontend.vercel.app",
    "http://localhost:3000",  # For local testing
]
```

---

## 📋 DEPLOYMENT CHECKLIST

### Pre-Deployment (30 min)
- [x] All code committed to GitHub
- [x] requirements.txt updated
- [x] Procfile created
- [x] runtime.txt created
- [x] gunicorn installed
- [x] .env.example updated
- [x] Static files collected

### Accounts Setup (30 min)
- [x] Paystack account (test keys)
- [x] Sendchamp account (funded)
- [x] Cloudinary account
- [x] Railway account
- [x] GitHub repository created

### Railway Deployment (30 min)
- [x] Project created
- [x] GitHub repo connected
- [x] Environment variables set
- [x] Database provisioned
- [x] App deployed successfully
- [x] Migrations run
- [x] Superuser created
- [x] Categories created

### Testing (30 min)
- [x] API health check passes
- [x] Admin panel accessible
- [x] User registration works
- [x] SMS sending works
- [x] Image upload works
- [x] Test payment works
- [x] Frontend connected
- [x] End-to-end test completed

---

## 🎯 NEXT STEPS (After Deployment)

### Immediate (Today)
1. ✅ Share backend URL with frontend team
2. ✅ Test all API endpoints
3. ✅ Create test data (users, listings)
4. ✅ Monitor Railway logs for errors

### Tomorrow
1. ⏳ Wait for Paystack KYC approval
2. ⏳ Wait for Sendchamp Sender ID approval
3. 📝 Document API for frontend team
4. 🧪 Continue testing with real users

### This Week
1. 🔄 Switch to Live Keys (when approved)
2. 🌐 Setup custom domain
3. 📊 Setup monitoring (Sentry)
4. 📱 Deploy frontend
5. 🚀 Soft launch to first 10 users

---

## 🆘 NEED HELP?

**Railway Issues:**
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway

**Paystack Issues:**
- Support: support@paystack.com
- Phone: +234 1 888 3881

**Sendchamp Issues:**
- Support: support@sendchamp.com
- WhatsApp: +234 817 000 1234

**Django Issues:**
- Check Railway logs
- Check error messages
- Google the error
- Ask in Django Discord

---

## ⏱️ TIMELINE RECAP

- **Hour 1:** Setup accounts (60 min)
- **Hour 2:** Deploy to Railway (60 min)
- **Total:** 2 hours to LIVE! 🚀

---

## 🎉 SUCCESS CRITERIA

You're successfully deployed when:
- ✅ Backend URL is accessible
- ✅ Admin panel works
- ✅ API returns data
- ✅ SMS sends successfully
- ✅ Test payment processes
- ✅ Frontend can connect
- ✅ No errors in Railway logs

---

**Status:** Ready to deploy NOW! 🚀  
**Time Required:** 2 hours  
**Difficulty:** Medium  
**Cost:** ₦5,000 (Sendchamp top-up only)

**LET'S GO! 💪**
