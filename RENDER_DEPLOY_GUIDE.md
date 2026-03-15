# 🚀 RENDER DEPLOYMENT GUIDE - COMPLETE SETUP

## ⏱️ Time: 25 minutes | Cost: FREE (90 days), then $7/month

---

## WHY RENDER?

✅ **FREE for 90 days** (no credit card for free tier)  
✅ **PostgreSQL included** (free)  
✅ **Auto-deploy** from GitHub  
✅ **SSL certificate** (free HTTPS)  
⚠️ **Sleeps after 15 min** (wakes in 30 seconds)  
⚠️ **Becomes paid** after 90 days  

---

## STEP 1: CREATE RENDER ACCOUNT (2 min)

1. **Go to**: https://render.com
2. **Click**: "Get Started" (top right)
3. **Sign up with GitHub** (easiest option)
4. **Authorize Render** to access your repos
5. **Done!** No credit card needed for free tier

---

## STEP 2: CREATE POSTGRESQL DATABASE (3 min)

1. **Dashboard** → Click **"New +"** (top right)
2. Select **"PostgreSQL"**
3. **Configure**:
   ```
   Name: campusdeal-db
   Database: campusdeal
   User: campusdeal
   Region: Frankfurt (closest to Nigeria)
   PostgreSQL Version: 15
   ```
4. **Select Plan**: **"Free"** (₦0/month for 90 days)
5. **Click**: "Create Database"
6. **Wait 2 minutes** for provisioning

---

## STEP 3: CREATE WEB SERVICE (5 min)

1. **Dashboard** → Click **"New +"**
2. Select **"Web Service"**
3. **Connect GitHub repository**:
   - If not connected, click "Connect account"
   - Find: **Campusdeal-Backend**
   - Click **"Connect"**

4. **Configure Service**:
   ```
   Name: campusdeal-backend
   Region: Frankfurt
   Branch: main
   Runtime: Python 3
   Build Command: pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
   Start Command: gunicorn campusdeal.wsgi:application --bind 0.0.0.0:$PORT
   ```

5. **Select Plan**: **"Free"** (₦0/month for 90 days)
6. **Click**: "Create Web Service"

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

---

## STEP 5: ADD ALL ENVIRONMENT VARIABLES (10 min)

**In Environment tab, add these ONE BY ONE**:

### Generate SECRET_KEY:
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

## STEP 8: CREATE SUPERUSER & CATEGORIES (3 min)

**Use the setup endpoint I created**:

### Call Setup Endpoint:
```bash
POST https://campusdeal-backend.onrender.com/api/marketplace/setup/
```

**Response**:
```json
{
  "superuser": {
    "username": "admin",
    "password": "CampusDeal2024!",
    "message": "⚠️ CHANGE PASSWORD IMMEDIATELY!"
  },
  "categories": ["Created: Electronics", ...],
  "warnings": ["⚠️ DELETE THIS ENDPOINT AFTER USE!"]
}
```

### Delete Setup Endpoint (IMPORTANT!):
```bash
git rm marketplace/setup_views.py
# Remove from marketplace/urls.py
git add .
git commit -m "Remove setup endpoint for security"
git push origin main
```

---

## STEP 9: TEST DEPLOYMENT (3 min)

### Test Admin Panel:
```
https://campusdeal-backend.onrender.com/admin/
Login: admin / CampusDeal2024!
```

### Test API:
```
https://campusdeal-backend.onrender.com/api/marketplace/categories/
```

### Test Registration:
```bash
POST https://campusdeal-backend.onrender.com/api/auth/register/
{
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
- [ ] PostgreSQL database created
- [ ] Web service deployed
- [ ] Database linked
- [ ] Environment variables added
- [ ] Migrations run
- [ ] Superuser created
- [ ] Categories created
- [ ] Admin panel accessible
- [ ] API working
- [ ] SMS sending

---

## 🎉 YOU'RE LIVE!

**Backend URL**: `https://campusdeal-backend.onrender.com`  
**Admin Panel**: `https://campusdeal-backend.onrender.com/admin/`  
**Username**: admin  
**Password**: CampusDeal2024! (change immediately!)

---

## ⚠️ RENDER FREE TIER LIMITATIONS

**Sleeps after 15 minutes of inactivity**
- First request after sleep: 30-50 seconds
- Subsequent requests: Normal speed
- **Solution**: Upgrade to $7/month for always-on

---

## 💰 COSTS

**Free Tier (90 days)**:
- Web Service: FREE
- PostgreSQL: FREE
- **Total: ₦0**

**After 90 days**:
- Web Service: $7/month (₦11,200)
- PostgreSQL: $7/month (₦11,200)
- **Total: ₦22,400/month**

---

## 📞 SUPPORT

**Render Docs**: https://render.com/docs  
**Community**: https://community.render.com  
**Email**: support@render.com

---

**NEXT**: Implement Financial Tracking System (2 hours)