# ✅ RAILWAY DEPLOYMENT - FINAL STEPS

## 🎉 CODE IS ON GITHUB! Now deploy to Railway...

---

## STEP 1: CREATE RAILWAY PROJECT (5 min)

1. Go to: **https://railway.app/dashboard**
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. If asked, click **"Configure GitHub App"** and authorize Railway
5. Select repository: **Campusdeal-Backend**
6. Railway will auto-detect Django and start building!
7. Wait 3-5 minutes for initial build

---

## STEP 2: ADD POSTGRESQL DATABASE (2 min)

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Wait 1 minute for provisioning
4. DATABASE_URL is automatically linked to your Django service!

---

## STEP 3: ADD ENVIRONMENT VARIABLES (10 min)

1. Click on your **Django service** (not the database)
2. Go to **"Variables"** tab
3. Click **"+ New Variable"** for each one below:

### Copy these ONE BY ONE:

```
SECRET_KEY
```
Value: (Generate one - see below)

```
DEBUG
```
Value: `False`

```
ALLOWED_HOSTS
```
Value: `*.railway.app,*.up.railway.app`

```
FRONTEND_URL
```
Value: `https://yourfrontend.vercel.app` (update later)

```
CORS_ALLOWED_ORIGINS
```
Value: `http://localhost:3000,https://yourfrontend.vercel.app`

```
PAYSTACK_SECRET_KEY
```
Value: `sk_test_YOUR_KEY` (from Paystack dashboard)

```
PAYSTACK_PUBLIC_KEY
```
Value: `pk_test_YOUR_KEY` (from Paystack dashboard)

```
SENDCHAMP_PUBLIC_KEY
```
Value: `sendchamp_pk_YOUR_KEY` (from Sendchamp dashboard)

```
SENDCHAMP_SECRET_KEY
```
Value: `sendchamp_sk_YOUR_KEY` (from Sendchamp dashboard)

```
SENDCHAMP_SENDER_ID
```
Value: `Sendchamp`

```
SENDCHAMP_BASE_URL
```
Value: `https://api.sendchamp.com/api/v1`

```
CLOUDINARY_CLOUD_NAME
```
Value: `your_cloud_name` (from Cloudinary dashboard)

```
CLOUDINARY_API_KEY
```
Value: `your_api_key` (from Cloudinary dashboard)

```
CLOUDINARY_API_SECRET
```
Value: `your_api_secret` (from Cloudinary dashboard)

### Generate SECRET_KEY:

**Option A: Online Generator**
- Go to: https://djecrety.ir/
- Copy the generated key

**Option B: Python Command**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## STEP 4: WAIT FOR DEPLOYMENT (3 min)

1. Railway will automatically redeploy with new variables
2. Go to **"Deployments"** tab
3. Wait for status to show **"SUCCESS"** (green checkmark)
4. If it fails, click on the deployment to see logs

---

## STEP 5: GET YOUR URL (1 min)

1. Go to **"Settings"** tab
2. Scroll to **"Domains"** section
3. Click **"Generate Domain"**
4. Copy your URL: `https://campusdeal-backend-production-xxxx.up.railway.app`
5. **SAVE THIS URL!**

---

## STEP 6: RUN MIGRATIONS (5 min)

1. In Railway, click your Django service
2. Click **"..."** (three dots) → **"Shell"** or **"Terminal"**
3. Wait for shell to open (30 seconds)
4. Run these commands ONE BY ONE:

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

**When prompted:**
- Username: `admin`
- Email: `admin@campusdeal.com`
- Password: (choose strong password - SAVE IT!)
- Password (again): (same password)

```bash
# Create categories
python manage.py shell
```

**Then paste this:**
```python
from marketplace.models import ItemCategory
categories = ['Electronics', 'Books', 'Clothing', 'Furniture', 'Phones', 'Laptops', 'Accessories', 'Other']
for cat in categories:
    ItemCategory.objects.get_or_create(name=cat)
print("✅ Categories created!")
exit()
```

---

## STEP 7: TEST YOUR DEPLOYMENT (5 min)

### Test 1: Admin Panel
```
Go to: https://your-app.railway.app/admin/
Login with: admin / your-password
✅ Should see Django admin dashboard
```

### Test 2: API Health
```
Go to: https://your-app.railway.app/api/marketplace/categories/
✅ Should see JSON with categories
```

### Test 3: Registration
```
Use Postman or curl:
POST https://your-app.railway.app/api/auth/register/
Body: {
  "username": "testuser",
  "email": "test@example.com",
  "phone_number": "+2348012345678",
  "password": "Test1234",
  "first_name": "Test",
  "last_name": "User"
}
✅ Should return success + send SMS
```

---

## ✅ SUCCESS CHECKLIST

- [ ] Railway project created
- [ ] PostgreSQL database added
- [ ] All environment variables set
- [ ] Deployment shows SUCCESS
- [ ] Domain generated and saved
- [ ] Migrations run successfully
- [ ] Superuser created
- [ ] Categories created
- [ ] Admin panel accessible
- [ ] API returns data
- [ ] Registration works
- [ ] SMS sends successfully

---

## 🎉 YOU'RE LIVE!

**Your Backend URL:**
```
https://campusdeal-backend-production-xxxx.up.railway.app
```

**Share this with your frontend team!**

**Admin Panel:**
```
https://your-app.railway.app/admin/
Username: admin
Password: (your password)
```

---

## 📱 NEXT STEPS

### 1. Update Paystack Webhook
```
Go to: https://dashboard.paystack.com
Settings → API Keys & Webhooks
Webhook URL: https://your-app.railway.app/api/marketplace/payments/webhook/
Save
```

### 2. Connect Frontend
```
Update frontend .env:
NEXT_PUBLIC_API_URL=https://your-app.railway.app
NEXT_PUBLIC_PAYSTACK_PUBLIC_KEY=pk_test_xxxxx
```

### 3. Test End-to-End
```
- Register user (frontend)
- Create listing
- Place order
- Process payment (test card: 4084084084084081)
- Confirm delivery
- Withdraw funds
```

---

## 🚨 TROUBLESHOOTING

### Build Failed
```
Check Railway logs:
- Click "Deployments" → Latest deployment → View logs
- Common issue: Missing package in requirements.txt
- Fix: Add package, commit, push
```

### Can't Access Admin
```
- Check ALLOWED_HOSTS includes *.railway.app
- Check DEBUG=False is set
- Try: https://your-app.railway.app/admin/ (with trailing slash)
```

### Database Error
```
- Ensure PostgreSQL service is running
- Check DATABASE_URL is automatically set
- Run migrations again in shell
```

### SMS Not Sending
```
- Check Sendchamp wallet has balance
- Check SENDCHAMP_SENDER_ID=Sendchamp (not CampusDeal)
- Check phone format: +234XXXXXXXXXX
- Test in Sendchamp dashboard first
```

---

## 💰 COSTS

**Today:**
- Railway: FREE (500MB database, $5 credit)
- Sendchamp: ₦5,000 (already funded)
- Cloudinary: FREE
- Paystack: FREE (test mode)

**After Free Tier:**
- Railway: $5/month (when you exceed 500MB or $5 credit)
- Everything else stays the same

---

## 🔄 SWITCHING TO LIVE MODE (Later)

When Paystack KYC approved (1-3 days):

1. Go to Paystack Dashboard
2. Toggle to **"Live Mode"**
3. Copy Live Keys
4. Update Railway Variables:
   - PAYSTACK_SECRET_KEY=`sk_live_xxxxx`
   - PAYSTACK_PUBLIC_KEY=`pk_live_xxxxx`
5. Railway auto-redeploys
6. Real payments now work!

---

## 📞 SUPPORT

**Railway Issues:**
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway

**Deployment Help:**
- Check Railway logs first
- Google the error message
- Ask in Railway Discord

---

**YOU'RE LIVE! 🚀 CONGRATULATIONS!**
