# 🚀 RENDER DEPLOYMENT GUIDE (Railway Alternative)

## ✅ 100% FREE - No Credit Card Required!

---

## WHY RENDER?

- ✅ **Completely FREE** (no trial, no credit card)
- ✅ **750 hours/month** free (enough for 24/7 uptime)
- ✅ **PostgreSQL included** (free)
- ✅ **Auto-deploy from GitHub**
- ✅ **SSL certificate** (free HTTPS)
- ⚠️ **Sleeps after 15 min inactivity** (wakes up in 30 seconds)

**Perfect for launch and testing!**

---

## STEP 1: CREATE RENDER ACCOUNT (2 min)

1. **Go to**: https://render.com
2. **Click**: "Get Started" (top right)
3. **Sign up with GitHub** (easiest option)
4. **Authorize Render** to access your repos
5. **Done!** No credit card needed!

---

## STEP 2: CREATE WEB SERVICE (5 min)

1. **Dashboard** → Click **"New +"** (top right)
2. Select **"Web Service"**
3. **Connect GitHub repository**:
   - If not connected, click "Connect account"
   - Find: **Campusdeal-Backend**
   - Click **"Connect"**

4. **Configure Service**:
   ```
   Name: campusdeal-backend
   Region: Frankfurt (closest to Nigeria)
   Branch: main
   Runtime: Python 3
   Build Command: pip install -r requirements.txt && python manage.py collectstatic --noinput
   Start Command: gunicorn campusdeal.wsgi:application --bind 0.0.0.0:$PORT
   ```

5. **Select Plan**: 
   - Choose **"Free"** (₦0/month)
   - Click **"Create Web Service"**

6. **Wait 5-10 minutes** for initial build

---

## STEP 3: CREATE POSTGRESQL DATABASE (3 min)

1. **Dashboard** → Click **"New +"**
2. Select **"PostgreSQL"**
3. **Configure**:
   ```
   Name: campusdeal-db
   Database: campusdeal
   User: campusdeal
   Region: Frankfurt (same as web service)
   ```
4. **Select Plan**: **"Free"** (₦0/month)
5. **Click**: "Create Database"
6. **Wait 2 minutes** for provisioning

---

## STEP 4: LINK DATABASE TO WEB SERVICE (2 min)

1. **Go to your PostgreSQL database** (click on it)
2. **Scroll down** to "Connections"
3. **Copy "Internal Database URL"** (starts with `postgresql://`)
4. **Go to your Web Service** (campusdeal-backend)
5. **Click**: "Environment" (left sidebar)
6. **Add Environment Variable**:
   ```
   Key: DATABASE_URL
   Value: (paste the Internal Database URL)
   ```
7. **Click**: "Save Changes"

---

## STEP 5: ADD ALL ENVIRONMENT VARIABLES (10 min)

**Still in Environment tab, add these ONE BY ONE**:

### Generate SECRET_KEY first:
Go to: https://djecrety.ir/ and copy the generated key

### Add these variables:

```
SECRET_KEY
(paste from djecrety.ir)

DEBUG
False

ALLOWED_HOSTS
.onrender.com

FRONTEND_URL
https://yourfrontend.vercel.app

CORS_ALLOWED_ORIGINS
http://localhost:3000,https://yourfrontend.vercel.app

PAYSTACK_SECRET_KEY
sk_test_YOUR_KEY

PAYSTACK_PUBLIC_KEY
pk_test_YOUR_KEY

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

PYTHON_VERSION
3.11.0
```

**Click "Save Changes" after adding all**

---

## STEP 6: WAIT FOR DEPLOYMENT (5 min)

1. **Go to "Logs"** tab (left sidebar)
2. **Watch the build process**
3. **Wait for**: "Your service is live 🎉"
4. **If build fails**: Check logs for errors

---

## STEP 7: GET YOUR URL (1 min)

1. **Top of page** shows your URL:
   ```
   https://campusdeal-backend.onrender.com
   ```
2. **Copy and save this URL!**

---

## STEP 8: RUN MIGRATIONS (5 min)

**Render doesn't have a built-in shell, so we'll use a workaround:**

### Option A: Add to Build Command (Recommended)

1. **Go to**: Settings tab
2. **Find**: "Build Command"
3. **Update to**:
   ```
   pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
   ```
4. **Click**: "Save Changes"
5. **Render will redeploy** (wait 5 min)

### Option B: Create Management Script

We'll create a setup endpoint you can call once.

---

## STEP 9: CREATE SUPERUSER & CATEGORIES (5 min)

**We need to create a one-time setup endpoint:**

Create this file: `marketplace/setup_views.py`

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from marketplace.models import ItemCategory

@api_view(['POST'])
def initial_setup(request):
    """One-time setup - DELETE THIS AFTER USE!"""
    
    # Create superuser
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@campusdeal.com',
            password='ChangeThisPassword123!'  # CHANGE THIS!
        )
    
    # Create categories
    categories = ['Electronics', 'Books', 'Clothing', 'Furniture', 
                  'Phones', 'Laptops', 'Accessories', 'Other']
    for cat in categories:
        ItemCategory.objects.get_or_create(name=cat)
    
    return Response({
        "message": "Setup complete!",
        "superuser": "admin",
        "password": "ChangeThisPassword123!",
        "warning": "DELETE THIS ENDPOINT IMMEDIATELY!"
    })
```

**Add to `marketplace/urls.py`:**
```python
from . import setup_views

urlpatterns = [
    # ... existing urls ...
    path('setup/', setup_views.initial_setup, name='setup'),  # TEMPORARY!
]
```

**Commit and push:**
```bash
git add .
git commit -m "Add setup endpoint"
git push origin main
```

**Wait for Render to redeploy (3 min)**

**Call the endpoint:**
```bash
# Use Postman or curl:
POST https://campusdeal-backend.onrender.com/api/marketplace/setup/
```

**You'll get**:
```json
{
  "message": "Setup complete!",
  "superuser": "admin",
  "password": "ChangeThisPassword123!"
}
```

**IMMEDIATELY DELETE THE ENDPOINT:**
```bash
# Remove setup_views.py and the URL
git add .
git commit -m "Remove setup endpoint"
git push origin main
```

---

## STEP 10: TEST DEPLOYMENT (5 min)

### Test 1: Admin Panel
```
https://campusdeal-backend.onrender.com/admin/
Login: admin / ChangeThisPassword123!
```

### Test 2: API
```
https://campusdeal-backend.onrender.com/api/marketplace/categories/
Should return JSON with categories
```

### Test 3: Registration
```
POST https://campusdeal-backend.onrender.com/api/auth/register/
Body: {
  "username": "testuser",
  "email": "test@example.com",
  "phone_number": "+2348012345678",
  "password": "Test1234",
  "first_name": "Test",
  "last_name": "User"
}
```

---

## ✅ SUCCESS CHECKLIST

- [ ] Render account created
- [ ] Web service deployed
- [ ] PostgreSQL database created
- [ ] Database linked to web service
- [ ] All environment variables added
- [ ] Migrations run
- [ ] Superuser created
- [ ] Categories created
- [ ] Admin panel accessible
- [ ] API returns data
- [ ] Registration works

---

## 🎉 YOU'RE LIVE!

**Backend URL**: `https://campusdeal-backend.onrender.com`  
**Admin Panel**: `https://campusdeal-backend.onrender.com/admin/`  
**Username**: admin  
**Password**: ChangeThisPassword123! (change in admin panel!)

---

## ⚠️ IMPORTANT: FREE TIER LIMITATIONS

**Render Free tier sleeps after 15 minutes of inactivity**

**What this means**:
- First request after sleep: 30-50 seconds to wake up
- Subsequent requests: Normal speed
- Not ideal for production, but perfect for testing!

**Solutions**:
1. **For testing**: Accept the 30-second wake-up time
2. **For production**: Upgrade to $7/month (no sleep)
3. **Workaround**: Use a cron job to ping every 14 minutes (keeps it awake)

---

## 💰 COSTS

**Today (Free Tier)**:
- Render Web Service: FREE
- Render PostgreSQL: FREE
- Sendchamp: ₦5,000 (already paid)
- Cloudinary: FREE
- Paystack: FREE (test mode)
- **Total: ₦5,000**

**Production (Paid Tier)**:
- Render Web Service: $7/month (₦10,500)
- Render PostgreSQL: $7/month (₦10,500)
- Everything else: Same
- **Total: ₦21,000/month**

---

## 🚨 TROUBLESHOOTING

### Build Failed
- Check Logs tab for errors
- Usually: Missing package or wrong Python version

### Can't Access Admin
- Check ALLOWED_HOSTS includes .onrender.com
- Try with trailing slash: /admin/

### Database Connection Error
- Ensure DATABASE_URL is set correctly
- Check database is running (green status)

### Service Sleeping
- First request takes 30-50 seconds
- This is normal for free tier
- Upgrade to $7/month to prevent sleep

---

## 📞 SUPPORT

**Render Docs**: https://render.com/docs  
**Render Community**: https://community.render.com  
**Response Time**: 24-48 hours

---

## 🔄 ALTERNATIVE: Use Render's Shell (Advanced)

If you have SSH access:

1. Go to your web service
2. Click "Shell" tab
3. Run commands directly:
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py shell
```

**Note**: Shell access may require paid plan

---

**YOU'RE LIVE ON RENDER! 🎉**

**Next**: Update Paystack webhook and connect frontend!
