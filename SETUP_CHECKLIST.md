# ✅ ACCOUNT SETUP QUICK CHECKLIST

Print this and check off as you complete each step!

---

## 🎯 PAYSTACK (30 minutes)

**Website:** https://paystack.com

- [ ] Create account with business email
- [ ] Verify email address
- [ ] Complete business profile
- [ ] Upload ID card (Driver's License/NIN/Passport)
- [ ] Upload proof of address (utility bill)
- [ ] Wait for KYC approval (1-3 days)
- [ ] Copy Test Secret Key: `sk_test_xxxxx`
- [ ] Copy Test Public Key: `pk_test_xxxxx`
- [ ] Set webhook URL: `https://yourdomain.com/api/marketplace/payments/webhook/`
- [ ] Copy Webhook Secret: `whsec_xxxxx`
- [ ] Enable Transfers feature
- [ ] Set Transfer PIN (4 digits)
- [ ] Add keys to .env file

**Cost:** FREE (1.5% per transaction)

---

## 📱 SENDCHAMP (20 minutes)

**Website:** https://www.sendchamp.com

- [ ] Create account
- [ ] Verify email address
- [ ] Complete business profile
- [ ] Copy Public Key: `sendchamp_pk_xxxxx`
- [ ] Copy Secret Key: `sendchamp_sk_xxxxx`
- [ ] Register Sender ID: "CampusDeal"
- [ ] Upload ID/CAC for Sender ID approval
- [ ] Fund wallet with ₦5,000 (for testing)
- [ ] Send test SMS to your phone
- [ ] Add keys to .env file

**Cost:** ₦1.50 per SMS (₦5,000 minimum top-up)

---

## 🖼️ CLOUDINARY (15 minutes)

**Website:** https://cloudinary.com/users/register/free

- [ ] Create account
- [ ] Verify email address
- [ ] Copy Cloud Name: `campusdeal`
- [ ] Copy API Key: `123456789012345`
- [ ] Copy API Secret: `xxxxxxxxxxxxx`
- [ ] Create upload preset: `campusdeal_items`
- [ ] Enable unsigned uploads
- [ ] Set max file size: 5MB
- [ ] Test image upload
- [ ] Add credentials to .env file

**Cost:** FREE (25GB storage + 25GB bandwidth)

---

## 🗄️ POSTGRESQL (10 minutes)

**Choose ONE option:**

### Option A: Railway (Easiest)
**Website:** https://railway.app

- [ ] Create account with GitHub
- [ ] Create new project
- [ ] Provision PostgreSQL
- [ ] Copy connection string
- [ ] Add to .env as DATABASE_URL

**Cost:** FREE (500MB) or $5/month (8GB)

### Option B: Supabase (Free Forever)
**Website:** https://supabase.com

- [ ] Create account
- [ ] Create project: "campusdeal-prod"
- [ ] Set strong database password
- [ ] Choose region: Singapore
- [ ] Copy connection string
- [ ] Add to .env as DATABASE_URL

**Cost:** FREE (500MB)

### Option C: Hetzner VPS (Self-hosted)

- [ ] SSH into server
- [ ] Install PostgreSQL: `sudo apt install postgresql`
- [ ] Create database: `campusdeal`
- [ ] Create user with password
- [ ] Add to .env as DATABASE_URL

**Cost:** FREE (included in VPS)

---

## 🐛 SENTRY (10 minutes) - OPTIONAL

**Website:** https://sentry.io/signup/

- [ ] Create account
- [ ] Create organization: "CampusDeal"
- [ ] Create project: "campusdeal-backend"
- [ ] Select platform: Django
- [ ] Copy DSN: `https://xxxxx@xxxxx.ingest.sentry.io/xxxxx`
- [ ] Install: `pip install sentry-sdk`
- [ ] Add DSN to .env file
- [ ] Test by triggering error

**Cost:** FREE (5,000 errors/month)

---

## 📧 EMAIL SMTP (5 minutes) - OPTIONAL

**Using Gmail:**

- [ ] Go to Google Account settings
- [ ] Enable 2-Factor Authentication
- [ ] Generate App Password
- [ ] Copy 16-character password
- [ ] Add to .env:
  ```
  EMAIL_HOST=smtp.gmail.com
  EMAIL_PORT=587
  EMAIL_HOST_USER=your-email@gmail.com
  EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
  ```

**Cost:** FREE

---

## 🔔 FIREBASE (15 minutes) - OPTIONAL (Phase 2)

**Website:** https://console.firebase.google.com

- [ ] Create account
- [ ] Create project: "CampusDeal"
- [ ] Disable Google Analytics
- [ ] Go to Project Settings
- [ ] Go to Cloud Messaging tab
- [ ] Copy Server Key
- [ ] Add to .env as FIREBASE_SERVER_KEY

**Cost:** FREE (unlimited notifications)

---

## 📝 FINAL .ENV FILE

Copy this template and fill in your values:

```env
# Django
SECRET_KEY=change-this-to-random-50-character-string
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
FRONTEND_URL=https://yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@host:5432/database

# Paystack
PAYSTACK_SECRET_KEY=sk_test_xxxxxxxxxxxxx
PAYSTACK_PUBLIC_KEY=pk_test_xxxxxxxxxxxxx
PAYSTACK_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx

# Sendchamp
SENDCHAMP_PUBLIC_KEY=sendchamp_pk_xxxxxxxxxxxxx
SENDCHAMP_SECRET_KEY=sendchamp_sk_xxxxxxxxxxxxx
SENDCHAMP_SENDER_ID=CampusDeal
SENDCHAMP_BASE_URL=https://api.sendchamp.com/api/v1

# Cloudinary
CLOUDINARY_CLOUD_NAME=campusdeal
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=xxxxxxxxxxxxxxxxxxxxx

# Sentry (Optional)
SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx

# Email (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=CampusDeal <noreply@campusdeal.com>

# Firebase (Optional - Phase 2)
FIREBASE_SERVER_KEY=xxxxxxxxxxxxxxxxxxxxx
```

---

## 🧪 TESTING CHECKLIST

After setup, test each service:

### Paystack
- [ ] Initialize test payment
- [ ] Complete payment with test card: `4084084084084081`
- [ ] Verify payment callback works
- [ ] Check webhook receives events

### Sendchamp
- [ ] Send SMS to your phone number
- [ ] Verify SMS arrives within 30 seconds
- [ ] Check wallet balance deducted correctly

### Cloudinary
- [ ] Upload test image via API
- [ ] Verify image appears in dashboard
- [ ] Test image URL loads in browser
- [ ] Check image transformations work

### PostgreSQL
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Access admin panel
- [ ] Create test data

### Sentry
- [ ] Trigger test error: `raise Exception("Test error")`
- [ ] Check error appears in Sentry dashboard
- [ ] Verify email notification received

---

## 💰 COST SUMMARY

### Setup Costs (One-Time)
- Domain: ₦5,000/year
- **Total: ₦5,000**

### Monthly Costs (1,000 users)
- Paystack: ₦0 (pay per transaction)
- Sendchamp: ₦3,000
- Cloudinary: ₦0 (free tier)
- PostgreSQL: ₦0 (free tier)
- Sentry: ₦0 (free tier)
- **Total: ₦3,000/month**

### Transaction Costs
- Paystack: 1.5% per transaction
- Example: ₦50,000 sale = ₦750 fee
- Withdrawal: ₦50 per transfer

---

## ⏱️ TIME ESTIMATE

- **Paystack:** 30 minutes (+ 1-3 days KYC wait)
- **Sendchamp:** 20 minutes (+ 1-2 days Sender ID approval)
- **Cloudinary:** 15 minutes
- **PostgreSQL:** 10 minutes
- **Sentry:** 10 minutes (optional)
- **Email:** 5 minutes (optional)
- **Testing:** 30 minutes

**Total Active Time:** ~90 minutes  
**Total Wait Time:** 1-3 days (for approvals)

---

## 🚨 COMMON ISSUES & SOLUTIONS

### Paystack KYC Rejected
- **Solution:** Ensure ID is clear and not expired
- **Solution:** Use recent utility bill (within 3 months)
- **Solution:** Contact support: support@paystack.com

### Sendchamp SMS Not Sending
- **Solution:** Check wallet balance
- **Solution:** Verify phone number format: +234XXXXXXXXXX
- **Solution:** Use approved Sender ID or "Sendchamp"

### Cloudinary Upload Fails
- **Solution:** Check file size < 5MB
- **Solution:** Verify API keys are correct
- **Solution:** Enable unsigned uploads in preset

### PostgreSQL Connection Error
- **Solution:** Check DATABASE_URL format
- **Solution:** Verify database exists
- **Solution:** Check firewall allows port 5432

---

## 📞 SUPPORT CONTACTS

| Service | Contact | Response Time |
|---------|---------|---------------|
| **Paystack** | support@paystack.com | 2-4 hours |
| **Sendchamp** | support@sendchamp.com | 1-2 hours |
| **Cloudinary** | support@cloudinary.com | 4-8 hours |
| **Railway** | help@railway.app | 12-24 hours |
| **Supabase** | support@supabase.com | 24-48 hours |

---

## ✅ COMPLETION CHECKLIST

- [ ] All accounts created
- [ ] All KYC documents submitted
- [ ] All API keys copied
- [ ] .env file updated
- [ ] All services tested
- [ ] Sendchamp funded (₦5,000)
- [ ] Test SMS sent successfully
- [ ] Test payment processed
- [ ] Test image uploaded
- [ ] Database migrations run
- [ ] Superuser created
- [ ] Ready for deployment! 🚀

---

**Next Step:** Deploy to production server!  
**See:** `DEPLOYMENT_GUIDE.md` for deployment instructions
