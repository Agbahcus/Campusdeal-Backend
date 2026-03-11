# 🚀 MASTER DEPLOYMENT CHECKLIST

## Complete this in order - 60 minutes to LIVE!

---

## ✅ PHASE 1: SETUP ACCOUNTS (30 min)

### 1. Paystack (DONE ✅)
- [x] Account created
- [x] Pre-approved
- [x] Test keys obtained

**Your keys**:
```
PAYSTACK_SECRET_KEY=sk_test_xxxxx (you have this)
PAYSTACK_PUBLIC_KEY=pk_test_xxxxx (you have this)
```

---

### 2. Sendchamp (15 min) ⭐ DO THIS NOW

**Follow**: `SENDCHAMP_SETUP.md`

**Quick steps**:
1. Go to: https://www.sendchamp.com
2. Sign up → Verify email
3. Settings → API Keys → Copy both keys
4. Wallet → Fund ₦5,000
5. SMS → Send test SMS to your phone

**You need**:
```
SENDCHAMP_PUBLIC_KEY=sendchamp_live_pk_xxxxx
SENDCHAMP_SECRET_KEY=sendchamp_live_sk_xxxxx
SENDCHAMP_SENDER_ID=Sendchamp
```

- [ ] Account created
- [ ] Email verified
- [ ] API keys copied
- [ ] Wallet funded (₦5,000)
- [ ] Test SMS sent successfully

---

### 3. Cloudinary (10 min) ⭐ DO THIS NOW

**Follow**: `CLOUDINARY_SETUP.md`

**Quick steps**:
1. Go to: https://cloudinary.com/users/register/free
2. Sign up → Verify email
3. Dashboard → Copy Cloud Name, API Key, API Secret
4. Settings → Upload → Create preset (optional)

**You need**:
```
CLOUDINARY_CLOUD_NAME=campusdeal (or your chosen name)
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=aBcDeFgHiJkLmNoPqRsTuVwXyZ
```

- [ ] Account created
- [ ] Email verified
- [ ] Cloud Name chosen
- [ ] API Key copied
- [ ] API Secret copied

---

### 4. Railway (5 min) ⭐ DO THIS NOW

**Quick steps**:
1. Go to: https://railway.app
2. Sign up with GitHub
3. Authorize Railway to access your repos

- [ ] Account created with GitHub
- [ ] Railway authorized

---

## ✅ PHASE 2: DEPLOY TO RAILWAY (30 min)

### 5. Create Railway Project (5 min)

**Follow**: `RAILWAY_DEPLOY_GUIDE.md` - Step 1 & 2

1. Railway Dashboard → "New Project"
2. "Deploy from GitHub repo"
3. Select: Campusdeal-Backend
4. Wait for build (3-5 min)
5. Add PostgreSQL database

- [ ] Project created
- [ ] GitHub repo connected
- [ ] Initial build successful
- [ ] PostgreSQL added

---

### 6. Add Environment Variables (15 min)

**Follow**: `RAILWAY_DEPLOY_GUIDE.md` - Step 3

**Click your Django service → Variables tab → Add these ONE BY ONE**:

```
SECRET_KEY=(generate: https://djecrety.ir/)
DEBUG=False
ALLOWED_HOSTS=*.railway.app,*.up.railway.app
FRONTEND_URL=https://yourfrontend.vercel.app
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourfrontend.vercel.app

PAYSTACK_SECRET_KEY=(from Paystack)
PAYSTACK_PUBLIC_KEY=(from Paystack)

SENDCHAMP_PUBLIC_KEY=(from Sendchamp)
SENDCHAMP_SECRET_KEY=(from Sendchamp)
SENDCHAMP_SENDER_ID=Sendchamp
SENDCHAMP_BASE_URL=https://api.sendchamp.com/api/v1

CLOUDINARY_CLOUD_NAME=(from Cloudinary)
CLOUDINARY_API_KEY=(from Cloudinary)
CLOUDINARY_API_SECRET=(from Cloudinary)
```

- [ ] All 14 variables added
- [ ] Deployment successful (check Deployments tab)

---

### 7. Get Your URL (1 min)

**Follow**: `RAILWAY_DEPLOY_GUIDE.md` - Step 5

1. Settings → Domains → Generate Domain
2. Copy URL: `https://campusdeal-backend-production-xxxx.up.railway.app`
3. **SAVE THIS URL!**

**Your URL**:
```
_________________________________
```

- [ ] Domain generated
- [ ] URL saved

---

### 8. Run Migrations (10 min)

**Follow**: `RAILWAY_DEPLOY_GUIDE.md` - Step 6

1. Click service → "..." → "Shell"
2. Run: `python manage.py migrate`
3. Run: `python manage.py createsuperuser`
   - Username: admin
   - Email: admin@campusdeal.com
   - Password: (choose strong password - SAVE IT!)
4. Run: `python manage.py shell`
5. Paste category creation code

**Superuser Password**:
```
_________________________________
```

- [ ] Migrations run
- [ ] Superuser created
- [ ] Categories created

---

## ✅ PHASE 3: TEST DEPLOYMENT (10 min)

### 9. Test Admin Panel

**URL**: `https://your-app.railway.app/admin/`

- [ ] Admin panel loads
- [ ] Can login with admin credentials
- [ ] Can see all models (Users, Orders, etc.)

---

### 10. Test API

**URL**: `https://your-app.railway.app/api/marketplace/categories/`

- [ ] Returns JSON with categories
- [ ] No errors

---

### 11. Test Registration (with Postman or curl)

```bash
POST https://your-app.railway.app/api/auth/register/
Body: {
  "username": "testuser",
  "email": "test@example.com",
  "phone_number": "+2348012345678",
  "password": "Test1234",
  "first_name": "Test",
  "last_name": "User"
}
```

- [ ] Registration successful
- [ ] SMS received on phone
- [ ] User created in admin panel

---

## 🎉 YOU'RE LIVE!

**Backend URL**: `https://your-app.railway.app`  
**Admin Panel**: `https://your-app.railway.app/admin/`  
**Admin User**: admin  
**Admin Pass**: (your password)

---

## 📱 NEXT STEPS

### Update Paystack Webhook
```
Go to: https://dashboard.paystack.com
Settings → API Keys & Webhooks
Webhook URL: https://your-app.railway.app/api/marketplace/payments/webhook/
Save
```

### Share with Frontend Team
```
Backend URL: https://your-app.railway.app
Paystack Public Key: pk_test_xxxxx
```

### Test End-to-End
1. Register user
2. Create listing
3. Place order
4. Process payment (test card: 4084084084084081)
5. Confirm delivery
6. Withdraw funds

---

## 💰 TOTAL COST TODAY

- Railway: FREE ($5 credit)
- Sendchamp: ₦5,000 (SMS credits)
- Cloudinary: FREE
- Paystack: FREE (test mode)

**Total: ₦5,000**

---

## 🚨 IF SOMETHING FAILS

### Build Failed
- Check Railway logs (Deployments → Latest → View logs)
- Usually: Missing package in requirements.txt

### Can't Access Admin
- Check ALLOWED_HOSTS includes *.railway.app
- Try with trailing slash: /admin/

### SMS Not Sending
- Check Sendchamp wallet balance
- Check phone format: +234XXXXXXXXXX
- Check SENDCHAMP_SENDER_ID=Sendchamp

### Database Error
- Ensure PostgreSQL service is running
- Run migrations again

---

## 📞 SUPPORT

**Railway**: https://discord.gg/railway  
**Sendchamp**: support@sendchamp.com  
**Cloudinary**: support@cloudinary.com  
**Paystack**: support@paystack.com

---

## ⏱️ TIME TRACKING

- [ ] Phase 1 Complete (30 min) - Setup accounts
- [ ] Phase 2 Complete (30 min) - Deploy to Railway
- [ ] Phase 3 Complete (10 min) - Testing
- [ ] 🎉 LIVE! (70 minutes total)

---

## 🎯 START HERE:

1. **Open**: `SENDCHAMP_SETUP.md`
2. **Complete**: Sendchamp setup (15 min)
3. **Open**: `CLOUDINARY_SETUP.md`
4. **Complete**: Cloudinary setup (10 min)
5. **Open**: `RAILWAY_DEPLOY_GUIDE.md`
6. **Complete**: Railway deployment (30 min)
7. **Test**: Everything works
8. **Celebrate**: You're LIVE! 🎉

---

**LET'S GO! START WITH SENDCHAMP NOW! 🚀**
