# 📋 QUICK REFERENCE CARD

## Print this or keep it open while deploying!

---

## 🔗 IMPORTANT LINKS

| Service | URL | Purpose |
|---------|-----|---------|
| **Sendchamp** | https://www.sendchamp.com | SMS service |
| **Cloudinary** | https://cloudinary.com | Image storage |
| **Railway** | https://railway.app | Hosting |
| **Paystack** | https://dashboard.paystack.com | Payments |
| **GitHub** | https://github.com/Agbahcus/Campusdeal-Backend | Your code |
| **Secret Key Generator** | https://djecrety.ir/ | Generate Django SECRET_KEY |

---

## 📂 GUIDES TO FOLLOW (IN ORDER)

1. **SENDCHAMP_SETUP.md** (15 min)
2. **CLOUDINARY_SETUP.md** (10 min)
3. **RAILWAY_DEPLOY_GUIDE.md** (30 min)
4. **MASTER_CHECKLIST.md** (track progress)

---

## 🔑 CREDENTIALS TEMPLATE

**Copy this to Notepad and fill in as you go**:

```
# ============================================
# PAYSTACK (DONE ✅)
# ============================================
PAYSTACK_SECRET_KEY=sk_test_
PAYSTACK_PUBLIC_KEY=pk_test_

# ============================================
# SENDCHAMP (Get from: Settings → API Keys)
# ============================================
SENDCHAMP_PUBLIC_KEY=sendchamp_live_pk_
SENDCHAMP_SECRET_KEY=sendchamp_live_sk_
SENDCHAMP_SENDER_ID=Sendchamp
SENDCHAMP_BASE_URL=https://api.sendchamp.com/api/v1

# ============================================
# CLOUDINARY (Get from: Dashboard homepage)
# ============================================
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

# ============================================
# DJANGO (Generate SECRET_KEY)
# ============================================
SECRET_KEY=
DEBUG=False
ALLOWED_HOSTS=*.railway.app,*.up.railway.app
FRONTEND_URL=https://yourfrontend.vercel.app
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourfrontend.vercel.app

# ============================================
# DEPLOYMENT INFO (Fill after Railway setup)
# ============================================
BACKEND_URL=https://campusdeal-backend-production-xxxx.up.railway.app
ADMIN_USERNAME=admin
ADMIN_PASSWORD=
```

---

## ⚡ QUICK COMMANDS

### Test SMS (Sendchamp Dashboard)
```
Sender: Sendchamp
Recipient: +234XXXXXXXXXX
Message: Test from CampusDeal
```

### Test Card (Paystack)
```
Card: 4084 0840 8408 4081
CVV: 408
Expiry: 12/25
PIN: 0000
```

### Railway Shell Commands
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py shell
```

### Create Categories (in Django shell)
```python
from marketplace.models import ItemCategory
categories = ['Electronics', 'Books', 'Clothing', 'Furniture', 'Phones', 'Laptops', 'Accessories', 'Other']
for cat in categories:
    ItemCategory.objects.get_or_create(name=cat)
print("✅ Done!")
exit()
```

---

## 🚨 TROUBLESHOOTING QUICK FIXES

| Problem | Solution |
|---------|----------|
| SMS not sending | Check wallet balance, use +234 format |
| Build failed | Check Railway logs, missing package |
| Can't access admin | Add trailing slash: /admin/ |
| Database error | Run migrations again |
| CORS error | Check CORS_ALLOWED_ORIGINS |

---

## 💰 COSTS

- **Today**: ₦5,000 (Sendchamp only)
- **Monthly**: ₦10,000 (Railway $5 + SMS ₦3,000)
- **Per transaction**: 1.5% (Paystack)

---

## ⏱️ TIME ESTIMATE

- Sendchamp: 15 min
- Cloudinary: 10 min
- Railway: 30 min
- Testing: 10 min
- **Total: 65 minutes**

---

## ✅ SUCCESS CRITERIA

You're live when:
- [ ] Admin panel loads
- [ ] API returns data
- [ ] Registration sends SMS
- [ ] Test payment works
- [ ] No errors in Railway logs

---

## 📞 EMERGENCY CONTACTS

**Railway**: https://discord.gg/railway  
**Sendchamp**: support@sendchamp.com  
**Cloudinary**: support@cloudinary.com  
**Paystack**: support@paystack.com / +234 1 888 3881

---

## 🎯 YOUR DEPLOYMENT URL

**Fill this in after Railway deployment**:

```
Backend: https://________________________________
Admin: https://________________________________/admin/
Username: admin
Password: ________________________________
```

---

**KEEP THIS OPEN WHILE DEPLOYING! 📌**
