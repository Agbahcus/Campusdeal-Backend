# 🚀 KOYEB + NEON DEPLOYMENT - MASTER GUIDE

## ⏱️ Total Time: 20 minutes | Cost: FREE Forever

---

## 🎯 DEPLOYMENT PLAN

### **Phase 1: Setup Database** (5 min)
- Create Neon.tech account
- Create PostgreSQL database
- Get connection string

### **Phase 2: Setup Hosting** (15 min)
- Create Koyeb account
- Deploy from GitHub
- Configure environment variables
- Test everything

---

## 📋 WHAT YOU NEED

### **Already Have** ✅:
- [x] GitHub account with code
- [x] Paystack keys (test mode)
- [x] Sendchamp keys + ₦5,000 funded
- [x] Cloudinary credentials

### **Will Create** ⏳:
- [ ] Neon.tech account (database)
- [ ] Koyeb account (hosting)

---

## 🗂️ GUIDES TO FOLLOW (IN ORDER)

### **Step 1**: Open `NEON_SETUP.md` (5 min)
- Create free PostgreSQL database
- Get DATABASE_URL connection string

### **Step 2**: Open `KOYEB_SETUP.md` (15 min)
- Deploy your app from GitHub
- Add all environment variables
- Test everything works

---

## 📝 CREDENTIALS TEMPLATE

**Copy this to Notepad and fill in as you go**:

```env
# ============================================
# DATABASE (Get from Neon.tech)
# ============================================
DATABASE_URL=postgresql://username:password@host/database?sslmode=require

# ============================================
# DJANGO (Generate SECRET_KEY)
# ============================================
SECRET_KEY=(generate at https://djecrety.ir/)
DEBUG=False
ALLOWED_HOSTS=.koyeb.app
FRONTEND_URL=https://yourfrontend.vercel.app
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourfrontend.vercel.app

# ============================================
# PAYSTACK (You already have these)
# ============================================
PAYSTACK_SECRET_KEY=sk_test_xxxxx
PAYSTACK_PUBLIC_KEY=pk_test_xxxxx

# ============================================
# SENDCHAMP (You already have these)
# ============================================
SENDCHAMP_PUBLIC_KEY=sendchamp_live_$2a$10$uEji8QDvv9.peFAYkREixOz3QaNlZtelbR/IfVxeBp59l60OISp3S
SENDCHAMP_SECRET_KEY=sendchamp_live_$2a$10$uEji8QDvv9.peFAYkREixOz3QaNlZtelbR/IfVxeBp59l60OISp3S
SENDCHAMP_SENDER_ID=Sendchamp
SENDCHAMP_BASE_URL=https://api.sendchamp.com/api/v1

# ============================================
# CLOUDINARY (You already have these)
# ============================================
CLOUDINARY_CLOUD_NAME=campusdeal
CLOUDINARY_API_KEY=478756491371227
CLOUDINARY_API_SECRET=RXRtrSg52KbhbZGr0mydcuHdayY
```

---

## 🚀 QUICK START CHECKLIST

### **Before You Start**:
- [ ] Code is pushed to GitHub
- [ ] Have all credentials ready (Paystack, Sendchamp, Cloudinary)
- [ ] Notepad open for copying credentials

### **Phase 1 - Database (5 min)**:
- [ ] Go to https://neon.tech
- [ ] Sign up with GitHub
- [ ] Create project "campusdeal"
- [ ] Copy DATABASE_URL
- [ ] Save to notepad

### **Phase 2 - Hosting (15 min)**:
- [ ] Go to https://koyeb.com
- [ ] Sign up with GitHub
- [ ] Create app from GitHub repo
- [ ] Add all environment variables
- [ ] Deploy and wait for build
- [ ] Call setup endpoint
- [ ] Delete setup endpoint
- [ ] Test admin panel and API

### **Phase 3 - Final Setup (2 min)**:
- [ ] Configure Paystack webhook
- [ ] Test SMS registration
- [ ] Share URL with frontend team

---

## 💰 WHY KOYEB + NEON?

### **vs Railway**:
```
Railway: Trial expired ❌
Koyeb: FREE forever ✅
```

### **vs Render**:
```
Render: Sleeps after 15 min ❌
Koyeb: Always on ✅

Render: $14/month when scaling
Koyeb: $5.34/month when scaling
```

### **vs Heroku**:
```
Heroku: No free tier ❌
Koyeb: FREE tier ✅

Heroku: $7/month minimum
Koyeb: FREE or $5.34/month
```

---

## 🎯 EXPECTED RESULTS

### **After Neon Setup**:
```
✅ PostgreSQL database running
✅ 3GB storage available
✅ Connection string ready
✅ Always-on (never sleeps)
```

### **After Koyeb Setup**:
```
✅ Backend live at: https://campusdeal-backend-xxx.koyeb.app
✅ Admin panel: https://campusdeal-backend-xxx.koyeb.app/admin/
✅ API working: https://campusdeal-backend-xxx.koyeb.app/api/
✅ SMS sending successfully
✅ Always-on (never sleeps)
```

---

## 🚨 COMMON ISSUES & SOLUTIONS

### **Neon Issues**:
| Problem | Solution |
|---------|----------|
| Can't connect to database | Check connection string includes `?sslmode=require` |
| "Database not found" | Use default database name `neondb` |
| Connection timeout | Check region is Frankfurt (closest to Nigeria) |

### **Koyeb Issues**:
| Problem | Solution |
|---------|----------|
| Build failed | Check Dockerfile and requirements.txt |
| Can't access admin | Check ALLOWED_HOSTS includes `.koyeb.app` |
| 500 errors | Check environment variables are set correctly |
| SMS not sending | Check Sendchamp wallet balance and credentials |

---

## 📞 SUPPORT CONTACTS

**Neon.tech**:
- Docs: https://neon.tech/docs
- Discord: https://discord.gg/92vNTzKDGp
- Email: support@neon.tech

**Koyeb**:
- Docs: https://www.koyeb.com/docs
- Discord: https://discord.gg/koyeb
- Email: support@koyeb.com

---

## 🎉 SUCCESS CRITERIA

**You're successfully deployed when**:
- [ ] Admin panel loads and you can login
- [ ] API endpoints return data
- [ ] Registration sends SMS
- [ ] No errors in Koyeb logs
- [ ] Database shows connected in Neon dashboard

---

## 📱 FINAL DELIVERABLE

**Share this with your frontend team**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   CAMPUSDEAL BACKEND - LIVE!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Production API:
https://campusdeal-backend-xxx.koyeb.app/api

Status: ✅ ALWAYS ON (never sleeps)
Speed: ⚡ Fast from Nigeria
Cost: 💰 FREE

Test Credentials:
Phone: +234XXXXXXXXXX
Test Card: 4084 0840 8408 4081

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🚀 START NOW!

1. **Open**: `NEON_SETUP.md`
2. **Complete**: Database setup (5 min)
3. **Open**: `KOYEB_SETUP.md`
4. **Complete**: Hosting setup (15 min)
5. **Test**: Everything works
6. **Celebrate**: You're LIVE! 🎉

---

**Total Time**: 20 minutes  
**Total Cost**: ₦0 (FREE forever)  
**Result**: Production-ready backend  

**LET'S GO! 🚀**