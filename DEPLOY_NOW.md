# ✅ DEPLOY IN 2 HOURS - ACTION CHECKLIST

Follow these steps EXACTLY to deploy today!

---

## ⏰ HOUR 1: SETUP ACCOUNTS (60 minutes)

### 1. Paystack (15 min) ⭐ CRITICAL
```
□ Go to: https://paystack.com
□ Sign up with email
□ Verify email (check inbox)
□ Go to Settings → API Keys & Webhooks
□ Copy Test Secret Key: sk_test_xxxxx
□ Copy Test Public Key: pk_test_xxxxx
□ Add webhook: https://your-app.railway.app/api/marketplace/payments/webhook/
□ Copy Webhook Secret
□ Save all 3 keys in notepad
```

### 2. Sendchamp (15 min) ⭐ CRITICAL
```
□ Go to: https://www.sendchamp.com
□ Sign up with email
□ Verify email
□ Go to Settings → API Keys
□ Copy Public Key: sendchamp_pk_xxxxx
□ Copy Secret Key: sendchamp_sk_xxxxx
□ Go to Wallet → Fund Wallet
□ Add ₦5,000 via bank transfer or card
□ Save both keys in notepad
```

### 3. Cloudinary (10 min) ⭐ CRITICAL
```
□ Go to: https://cloudinary.com/users/register/free
□ Sign up with email
□ Verify email
□ Dashboard shows credentials immediately
□ Copy Cloud Name: campusdeal (or yours)
□ Copy API Key: 123456789012345
□ Copy API Secret: xxxxxxxxxxxxx
□ Go to Settings → Upload
□ Click "Add upload preset"
□ Name: campusdeal_items
□ Mode: Unsigned
□ Save
□ Save all 3 credentials in notepad
```

### 4. Railway (10 min) ⭐ CRITICAL
```
□ Go to: https://railway.app
□ Sign up with GitHub
□ Click "New Project"
□ Select "Provision PostgreSQL"
□ Wait 1 minute for setup
□ Click on PostgreSQL service
□ Go to "Connect" tab
□ Copy DATABASE_URL (starts with postgresql://)
□ Save in notepad
```

### 5. GitHub (10 min) ⭐ CRITICAL
```
□ Go to: https://github.com/new
□ Repository name: campusdeal-backend
□ Make it Private
□ Don't initialize with README
□ Click "Create repository"
□ Copy the git commands shown
□ Keep page open
```

---

## ⏰ HOUR 2: DEPLOY (60 minutes)

### 6. Prepare Code (15 min)

**Run these commands in your project folder:**

```bash
# Windows Command Prompt:
cd c:\Users\divin\campusdeal-backend

# Install missing packages
pip install gunicorn whitenoise dj-database-url

# Update requirements
pip freeze > requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Check for issues
python manage.py check
```

### 7. Push to GitHub (10 min)

```bash
# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Ready for deployment"

# Add remote (use YOUR GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/campusdeal-backend.git

# Push
git branch -M main
git push -u origin main
```

**If you get authentication error:**
- Use GitHub Personal Access Token instead of password
- Go to: https://github.com/settings/tokens
- Generate new token (classic)
- Select "repo" scope
- Use token as password

### 8. Deploy on Railway (20 min)

```
□ Go back to Railway dashboard
□ Click "New Project"
□ Select "Deploy from GitHub repo"
□ Authorize GitHub if asked
□ Select: campusdeal-backend
□ Railway auto-detects Django!
□ Wait 3-5 minutes for initial build
```

### 9. Add Environment Variables (10 min)

**In Railway, click on your service → Variables tab**

Add these ONE BY ONE (copy from your notepad):

```
SECRET_KEY=your-random-50-character-string-change-this
DEBUG=False
ALLOWED_HOSTS=*.railway.app
FRONTEND_URL=https://yourfrontend.vercel.app

PAYSTACK_SECRET_KEY=sk_test_xxxxx
PAYSTACK_PUBLIC_KEY=pk_test_xxxxx

SENDCHAMP_PUBLIC_KEY=sendchamp_pk_xxxxx
SENDCHAMP_SECRET_KEY=sendchamp_sk_xxxxx
SENDCHAMP_SENDER_ID=Sendchamp

CLOUDINARY_CLOUD_NAME=campusdeal
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=xxxxxxxxxxxxx

CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourfrontend.vercel.app
```

**Note:** DATABASE_URL is already set by Railway automatically!

### 10. Run Migrations (5 min)

```
□ In Railway, click your service
□ Click "..." (three dots) → "Shell"
□ Wait for shell to open
□ Run these commands:

python manage.py migrate
python manage.py createsuperuser

# Enter:
Username: admin
Email: admin@campusdeal.com
Password: (strong password - save it!)
Password (again): (same password)
```

### 11. Create Categories (5 min)

**In the Railway shell, continue:**

```python
python manage.py shell

# Copy and paste this:
from marketplace.models import ItemCategory

categories = ['Electronics', 'Books', 'Clothing', 'Furniture', 'Phones', 'Laptops', 'Accessories', 'Other']

for cat in categories:
    ItemCategory.objects.get_or_create(name=cat)

print("✅ Categories created!")
exit()
```

### 12. Get Your URL (1 min)

```
□ In Railway, click "Settings" tab
□ Scroll to "Domains"
□ Copy the URL: https://campusdeal-backend-production-xxxx.up.railway.app
□ Save this URL!
```

---

## 🧪 TESTING (5 minutes)

### Test 1: API Health
```bash
# Open browser or use curl:
https://your-app.railway.app/admin/

# Should show Django admin login
```

### Test 2: Admin Panel
```
□ Go to: https://your-app.railway.app/admin/
□ Login with superuser credentials
□ Check you can see:
  - Users
  - Item Categories
  - Item Listings
  - Orders
```

### Test 3: API Endpoint
```bash
# In browser or Postman:
GET https://your-app.railway.app/api/marketplace/categories/

# Should return JSON with categories
```

---

## ✅ SUCCESS CHECKLIST

You're successfully deployed when:

- [x] Railway shows "Deployed" status (green)
- [x] Admin panel loads and you can login
- [x] Categories API returns data
- [x] No errors in Railway logs
- [x] You have your backend URL saved

---

## 🎉 YOU'RE LIVE!

**Your Backend URL:**
```
https://campusdeal-backend-production-xxxx.up.railway.app
```

**Share this with your frontend team!**

---

## 📱 CONNECT FRONTEND

Update your frontend .env:

```env
NEXT_PUBLIC_API_URL=https://your-app.railway.app
NEXT_PUBLIC_PAYSTACK_PUBLIC_KEY=pk_test_xxxxx
```

---

## 🔄 SWITCHING TO LIVE MODE (Later)

When Paystack KYC is approved (1-3 days):

1. Go to Paystack Dashboard
2. Toggle to "Live Mode"
3. Copy Live Keys
4. Update Railway Variables:
   - PAYSTACK_SECRET_KEY=sk_live_xxxxx
   - PAYSTACK_PUBLIC_KEY=pk_live_xxxxx
5. Railway auto-redeploys

---

## 🚨 TROUBLESHOOTING

### Build Failed
```
□ Check Railway logs (click "Deployments" → latest deployment)
□ Common issue: Missing package
□ Fix: Add to requirements.txt, commit, push
```

### Can't Access Admin
```
□ Check ALLOWED_HOSTS includes *.railway.app
□ Check DEBUG=False is set
□ Check migrations ran successfully
```

### Database Error
```
□ Check DATABASE_URL is set (Railway sets automatically)
□ Run migrations again in Railway shell
```

### SMS Not Sending
```
□ Check Sendchamp wallet has balance
□ Check SENDCHAMP_SENDER_ID=Sendchamp (not CampusDeal yet)
□ Check phone format: +234XXXXXXXXXX
```

---

## 💰 COSTS TODAY

- Railway: FREE (500MB database)
- Sendchamp: ₦5,000 (one-time top-up)
- Cloudinary: FREE
- Paystack: FREE (test mode)
- **Total: ₦5,000**

---

## 📞 NEED HELP?

**Railway Issues:**
- Check logs in dashboard
- Discord: https://discord.gg/railway

**Paystack Issues:**
- support@paystack.com
- +234 1 888 3881

**Sendchamp Issues:**
- support@sendchamp.com

---

## ⏱️ TIME TRACKING

- [ ] Hour 1 Complete (Accounts setup)
- [ ] Hour 2 Complete (Deployment)
- [ ] Testing Complete
- [ ] Frontend Connected
- [ ] 🎉 LIVE!

---

**START NOW! You can be live in 2 hours! 🚀**
