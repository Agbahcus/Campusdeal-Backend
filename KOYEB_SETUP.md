# 🚀 KOYEB SETUP GUIDE - FREE HOSTING

## ⏱️ Time: 15 minutes | Cost: FREE Forever

---

## WHY KOYEB?

✅ **FREE FOREVER** (not trial)  
✅ **NEVER SLEEPS** (unlike Render/Heroku free)  
✅ **512MB RAM** + Shared CPU  
✅ **Global CDN** (fast from Nigeria)  
✅ **Auto-deploy** from GitHub  
✅ **Docker support** (modern deployment)  

---

## STEP 1: CREATE ACCOUNT (2 min)

1. **Go to**: https://koyeb.com
2. **Click**: "Start for Free" (top right)
3. **Choose**: "Continue with GitHub" (recommended)
4. **Authorize Koyeb** to access your repositories
5. **You're in!** No credit card required

---

## STEP 2: PREPARE YOUR CODE (5 min)

### **2.1 Commit Docker Files**

**Make sure you have these files** (I already created them):
- ✅ `Dockerfile`
- ✅ `.dockerignore`

**Commit and push**:
```bash
cd c:\Users\divin\campusdeal-backend
git add .
git commit -m "Add Docker support for Koyeb"
git push origin main
```

### **2.2 Verify Requirements**

**Check `requirements.txt` includes**:
```
gunicorn==23.0.0
whitenoise==6.8.2
dj-database-url==2.1.0
psycopg2-binary==2.9.10
```

**If missing, add them**:
```bash
pip install gunicorn whitenoise dj-database-url psycopg2-binary
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements for production"
git push origin main
```

---

## STEP 3: CREATE KOYEB APP (5 min)

### **3.1 Start New App**

1. **Koyeb Dashboard** → Click **"Create App"**
2. **Choose**: "GitHub" (deploy from repository)

### **3.2 Connect Repository**

1. **If first time**: Click "Install Koyeb on GitHub"
   - Select your GitHub account
   - Choose "All repositories" or select "Campusdeal-Backend"
   - Click "Install"

2. **Select Repository**: 
   - Find: **Campusdeal-Backend**
   - Click **"Select"**

3. **Branch**: `main` (should be auto-selected)

### **3.3 Configure Build**

**Build Settings**:
```
Builder: Docker
Dockerfile: Dockerfile (auto-detected)
Build context: / (root directory)
```

**Instance Settings**:
```
Region: Frankfurt (fra) - closest to Nigeria
Instance type: Free (Eco)
Scaling: 1 instance (min and max)
```

**Port**: `8000` (auto-detected from Dockerfile)

---

## STEP 4: ADD ENVIRONMENT VARIABLES (5 min)

**Click "Environment variables" section and add these ONE BY ONE**:

### **4.1 Generate SECRET_KEY**

**Go to**: https://djecrety.ir/  
**Copy the generated key** (50+ characters)

### **4.2 Add All Variables**

```
SECRET_KEY
(paste from djecrety.ir - looks like: django-insecure-abc123...)

DEBUG
False

ALLOWED_HOSTS
.koyeb.app

DATABASE_URL
(paste from Neon.tech - starts with postgresql://)

PAYSTACK_SECRET_KEY
sk_test_YOUR_KEY_HERE

PAYSTACK_PUBLIC_KEY
pk_test_YOUR_KEY_HERE

SENDCHAMP_PUBLIC_KEY
sendchamp_live_$2a$10$uEji8QDvv9.peFAYkREixOz3QaNlZtelbR/IfVxeBp59l60OISp3S

SENDCHAMP_SECRET_KEY
sendchamp_live_$2a$10$uEji8QDvv9.peFAYkREixOz3QaNlZtelbR/IfVxeBp59l60OISp3S

SENDCHAMP_SENDER_ID
Sendchamp

SENDCHAMP_BASE_URL
https://api.sendchamp.com/api/v1

CLOUDINARY_CLOUD_NAME
campusdeal

CLOUDINARY_API_KEY
478756491371227

CLOUDINARY_API_SECRET
RXRtrSg52KbhbZGr0mydcuHdayY

FRONTEND_URL
https://yourfrontend.vercel.app

CORS_ALLOWED_ORIGINS
http://localhost:3000,https://yourfrontend.vercel.app
```

**Important**: Replace placeholder values with your actual credentials!

---

## STEP 5: DEPLOY! (3 min)

### **5.1 Review and Deploy**

1. **Review all settings**:
   - Repository: ✅ Campusdeal-Backend
   - Branch: ✅ main
   - Builder: ✅ Docker
   - Region: ✅ Frankfurt
   - Instance: ✅ Free
   - Environment variables: ✅ All added

2. **App Name**: `campusdeal-backend` (or auto-generated)

3. **Click**: "Deploy" (big blue button)

### **5.2 Wait for Build**

**Build process** (3-5 minutes):
1. ✅ Cloning repository
2. ✅ Building Docker image
3. ✅ Installing dependencies
4. ✅ Collecting static files
5. ✅ Starting application

**Watch the logs** in real-time to see progress.

### **5.3 Get Your URL**

**After successful deployment**:
```
Your app URL: https://campusdeal-backend-xxx.koyeb.app
```

**Copy and save this URL!**

---

## STEP 6: CREATE SUPERUSER (2 min)

**Since Koyeb doesn't have a built-in shell, we'll use a temporary endpoint**:

### **6.1 Create Setup Endpoint**

**I already created this file**: `marketplace/setup_views.py`

**Make sure it's in your URLs** (check `marketplace/urls.py`):
```python
path('setup/', setup_views.initial_setup, name='initial-setup'),
```

### **6.2 Call Setup Endpoint**

**Use Postman, curl, or browser**:

```bash
POST https://campusdeal-backend-xxx.koyeb.app/api/marketplace/setup/
```

**Response**:
```json
{
  "superuser": {
    "username": "admin",
    "password": "CampusDeal2024!",
    "message": "⚠️ CHANGE PASSWORD IMMEDIATELY IN ADMIN PANEL!"
  },
  "categories": [
    "Created: Electronics",
    "Created: Books",
    ...
  ],
  "warnings": [
    "⚠️ DELETE THIS ENDPOINT IMMEDIATELY AFTER USE!"
  ]
}
```

### **6.3 DELETE Setup Endpoint (IMPORTANT!)**

**After successful setup**:

1. **Delete**: `marketplace/setup_views.py`
2. **Remove from**: `marketplace/urls.py`
3. **Commit and push**:
   ```bash
   git rm marketplace/setup_views.py
   git add marketplace/urls.py
   git commit -m "Remove setup endpoint for security"
   git push origin main
   ```

**Koyeb will auto-redeploy** (1-2 minutes)

---

## STEP 7: TEST DEPLOYMENT (3 min)

### **7.1 Test Admin Panel**

**URL**: `https://campusdeal-backend-xxx.koyeb.app/admin/`

**Login**:
- Username: `admin`
- Password: `CampusDeal2024!`

**Should see**: Django admin dashboard with all your models

**IMMEDIATELY**: Change admin password in admin panel!

### **7.2 Test API Endpoints**

**Categories**:
```
GET https://campusdeal-backend-xxx.koyeb.app/api/marketplace/categories/
```
**Should return**: JSON array with categories

**Registration**:
```bash
POST https://campusdeal-backend-xxx.koyeb.app/api/auth/register/
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "phone_number": "+2348012345678",
  "password": "Test1234",
  "first_name": "Test",
  "last_name": "User"
}
```

**Should**: 
- Return success response
- Send SMS to phone number
- Create user in admin panel

### **7.3 Test SMS**

**If registration SMS arrives**: ✅ Everything works!  
**If no SMS**: Check Sendchamp wallet balance and credentials

---

## STEP 8: CONFIGURE WEBHOOKS (2 min)

### **8.1 Paystack Webhook**

1. **Go to**: https://dashboard.paystack.com
2. **Settings** → **API Keys & Webhooks**
3. **Webhook URL**: 
   ```
   https://campusdeal-backend-xxx.koyeb.app/api/marketplace/payments/webhook/
   ```
4. **Click**: "Save"

### **8.2 Test Webhook**

**Paystack will send a test event** - check Koyeb logs to see if received.

---

## ✅ SUCCESS CHECKLIST

- [ ] Koyeb account created
- [ ] GitHub connected
- [ ] Repository selected
- [ ] Docker build configured
- [ ] Environment variables added
- [ ] App deployed successfully
- [ ] Setup endpoint called
- [ ] Superuser created
- [ ] Categories created
- [ ] Setup endpoint deleted
- [ ] Admin panel accessible
- [ ] API endpoints working
- [ ] SMS sending
- [ ] Paystack webhook configured

---

## 🎉 YOU'RE LIVE!

**Your Backend**:
```
URL: https://campusdeal-backend-xxx.koyeb.app
API: https://campusdeal-backend-xxx.koyeb.app/api
Admin: https://campusdeal-backend-xxx.koyeb.app/admin
```

**Credentials**:
```
Admin Username: admin
Admin Password: CampusDeal2024! (CHANGE THIS!)
```

---

## 📱 SHARE WITH FRONTEND TEAM

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   CAMPUSDEAL BACKEND - LIVE!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Production API:
https://campusdeal-backend-xxx.koyeb.app/api

Key Endpoints:
POST /auth/register/
POST /auth/login/
GET  /marketplace/listings/
GET  /marketplace/categories/
POST /marketplace/orders/initiate/

Status: ✅ ALWAYS ON (never sleeps)
Speed: ⚡ Fast from Nigeria (Frankfurt CDN)

Test Credentials:
Phone: +234XXXXXXXXXX
Locations: ilorin, malete, offa
User Types: student, landlord

Paystack Test Card:
4084 0840 8408 4081
CVV: 408, Expiry: 12/25

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 💰 COST BREAKDOWN

### **Current (FREE)**:
```
Koyeb Web Service: FREE ✅
├─ 1 instance always on
├─ 512MB RAM, shared CPU
├─ 2.5GB disk space
└─ Unlimited bandwidth

Neon PostgreSQL: FREE ✅
├─ 3GB storage
├─ Always active
└─ Automatic backups

Total: ₦0/month
```

### **When You Scale**:
```
Need more performance:
├─ Koyeb: $5.34/month (1 dedicated instance)
├─ Neon: Still FREE (3GB plenty)
└─ Total: ₦8,500/month

Need high availability:
├─ Koyeb: $10.68/month (2 instances)
├─ Neon: $19/month (Pro plan)
└─ Total: ₦47,000/month
```

---

## 🚨 TROUBLESHOOTING

### Build Failed
**Check Koyeb logs**:
- Click your app → "Logs" tab
- Look for error messages
- Common: Missing package in requirements.txt

### Can't Access Admin
**Solutions**:
- Check ALLOWED_HOSTS includes `.koyeb.app`
- Try with trailing slash: `/admin/`
- Verify superuser was created

### API Returns 500 Error
**Solutions**:
- Check environment variables are set
- Verify DATABASE_URL is correct
- Check Koyeb logs for Python errors

### SMS Not Sending
**Solutions**:
- Check Sendchamp wallet balance
- Verify SENDCHAMP credentials
- Use phone format: +234XXXXXXXXXX

### Database Connection Error
**Solutions**:
- Verify DATABASE_URL from Neon
- Check Neon database is active
- Ensure `sslmode=require` in connection string

---

## 📊 MONITORING

### **Koyeb Dashboard**:
- **Metrics**: CPU, RAM, requests/sec
- **Logs**: Real-time application logs
- **Deployments**: Build history
- **Settings**: Environment variables

### **Neon Dashboard**:
- **Storage**: Usage out of 3GB
- **Connections**: Active database connections
- **Queries**: Slow query analysis
- **Backups**: Automatic backup status

---

## 🔄 AUTO-DEPLOYMENT

**Every time you push to GitHub**:
1. Koyeb detects changes
2. Builds new Docker image
3. Deploys automatically
4. Zero downtime deployment

**To disable auto-deploy**:
- Koyeb Dashboard → Your app → Settings → GitHub
- Toggle "Auto-deploy" off

---

## 📞 SUPPORT

**Koyeb**:
- Docs: https://www.koyeb.com/docs
- Discord: https://discord.gg/koyeb
- Email: support@koyeb.com

**Neon**:
- Docs: https://neon.tech/docs
- Discord: https://discord.gg/92vNTzKDGp
- Email: support@neon.tech

---

## 🎯 NEXT STEPS

1. **Change admin password** in admin panel
2. **Test all features** with frontend team
3. **Monitor usage** in dashboards
4. **Set up alerts** for storage/performance
5. **Plan scaling** when you get users

---

**Status**: ✅ LIVE ON KOYEB!  
**Performance**: ⚡ Always-on, fast from Nigeria  
**Cost**: 💰 FREE (can stay free for months)  
**Scalability**: 📈 Ready to scale when needed  

**CONGRATULATIONS! 🎉**