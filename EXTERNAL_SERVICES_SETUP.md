# 🔧 EXTERNAL SERVICES SETUP GUIDE

Complete guide to create and configure all external accounts needed for CampusDeal.

---

## 📋 SERVICES OVERVIEW

| Service | Purpose | Cost | Priority |
|---------|---------|------|----------|
| **Paystack** | Payment processing & withdrawals | 1.5% per transaction | ⭐⭐⭐ CRITICAL |
| **Sendchamp** | SMS verification & notifications | ₦1.50/SMS | ⭐⭐⭐ CRITICAL |
| **Cloudinary** | Image storage & optimization | Free (25GB) | ⭐⭐ HIGH |
| **PostgreSQL** | Production database | Free-₦5K/month | ⭐⭐⭐ CRITICAL |
| **Sentry** | Error monitoring | Free (5K errors/month) | ⭐ MEDIUM |

---

## 1️⃣ PAYSTACK SETUP (Payment Gateway)

### **Step 1: Create Account**

1. Go to: https://paystack.com
2. Click **"Get Started"** (top right)
3. Fill in details:
   - **Business Name:** CampusDeal
   - **Email:** your-email@gmail.com
   - **Phone:** +234XXXXXXXXXX
   - **Password:** (Strong password)
4. Click **"Create Account"**
5. **Verify email** (check inbox)

### **Step 2: Complete Business Profile**

1. Login to dashboard: https://dashboard.paystack.com
2. Go to **Settings** → **Business Profile**
3. Fill in:
   - **Business Type:** Marketplace/E-commerce
   - **Business Category:** Student Services
   - **Business Description:** "Campus marketplace for students"
   - **Website:** campusdeal.com (or your domain)
   - **Business Address:** Your address
4. Click **"Save"**

### **Step 3: Submit KYC Documents**

**Required Documents:**
- ✅ Valid ID (Driver's License, NIN, Passport, or Voter's Card)
- ✅ Proof of Address (Utility bill, Bank statement)
- ✅ CAC Certificate (if registered business) - **Optional for now**

**How to Submit:**
1. Go to **Settings** → **Compliance**
2. Upload documents
3. Wait 1-3 business days for approval

**Note:** You can test with Test Keys immediately, but need approval for Live Keys.

### **Step 4: Get API Keys**

**Test Keys (Use for Development):**
1. Go to **Settings** → **API Keys & Webhooks**
2. Copy:
   - **Test Public Key:** `pk_test_xxxxxxxxxxxxx`
   - **Test Secret Key:** `sk_test_xxxxxxxxxxxxx`

**Live Keys (After KYC Approval):**
1. Toggle to **"Live Mode"** (top right)
2. Copy:
   - **Live Public Key:** `pk_live_xxxxxxxxxxxxx`
   - **Live Secret Key:** `sk_live_xxxxxxxxxxxxx`

### **Step 5: Setup Webhook**

1. Go to **Settings** → **API Keys & Webhooks**
2. Scroll to **"Webhook URL"**
3. Enter: `https://yourdomain.com/api/marketplace/payments/webhook/`
4. Click **"Save"**
5. Copy **Webhook Secret** (for signature verification)

### **Step 6: Enable Transfer Feature**

**For Withdrawals:**
1. Go to **Settings** → **Preferences**
2. Enable **"Transfers"**
3. Set **Transfer PIN** (4 digits)
4. Confirm via email

**Important:** Transfers require:
- ✅ Verified business account
- ✅ Minimum ₦10,000 balance
- ✅ Transfer PIN set

### **What to Add to .env:**

```env
# Paystack Configuration
PAYSTACK_SECRET_KEY=sk_test_xxxxxxxxxxxxx  # Use sk_live_ in production
PAYSTACK_PUBLIC_KEY=pk_test_xxxxxxxxxxxxx  # Use pk_live_ in production
PAYSTACK_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
```

### **Pricing:**
- Transaction Fee: **1.5%** (capped at ₦2,000)
- Transfer Fee: **₦50** per withdrawal
- No monthly fees
- No setup fees

---

## 2️⃣ SENDCHAMP SETUP (SMS Service)

### **Step 1: Create Account**

1. Go to: https://www.sendchamp.com
2. Click **"Get Started Free"**
3. Fill in:
   - **Full Name:** Your Name
   - **Email:** your-email@gmail.com
   - **Phone:** +234XXXXXXXXXX
   - **Password:** (Strong password)
   - **Business Name:** CampusDeal
4. Click **"Sign Up"**
5. **Verify email** (check inbox)

### **Step 2: Complete Profile**

1. Login to dashboard: https://my.sendchamp.com
2. Go to **Settings** → **Profile**
3. Fill in:
   - **Business Type:** Technology/Marketplace
   - **Use Case:** OTP & Transactional SMS
   - **Monthly Volume:** 1,000-5,000 SMS
4. Click **"Save"**

### **Step 3: Get API Keys**

1. Go to **Settings** → **API Keys**
2. Copy:
   - **Public Key:** `sendchamp_pk_xxxxxxxxxxxxx`
   - **Secret Key:** `sendchamp_sk_xxxxxxxxxxxxx`

### **Step 4: Register Sender ID**

**What is Sender ID?** The name that appears as SMS sender (e.g., "CampusDeal")

1. Go to **SMS** → **Sender IDs**
2. Click **"Add Sender ID"**
3. Enter: **CampusDeal** (max 11 characters, no spaces)
4. Select **Purpose:** Transactional
5. Upload **CAC Certificate** (if available) or **ID Card**
6. Click **"Submit"**
7. Wait 1-2 business days for approval

**Temporary Solution:** Use **"Sendchamp"** as sender ID (pre-approved)

### **Step 5: Fund Account**

**Minimum Top-up:** ₦1,000

1. Go to **Wallet** → **Fund Wallet**
2. Enter amount: ₦5,000 (recommended for testing)
3. Pay via:
   - Bank Transfer
   - Card Payment
   - USSD
4. Confirm payment

### **Step 6: Test SMS**

1. Go to **SMS** → **Send SMS**
2. Enter your phone number
3. Type test message
4. Click **"Send"**
5. Confirm you receive SMS

### **What to Add to .env:**

```env
# Sendchamp Configuration
SENDCHAMP_PUBLIC_KEY=sendchamp_pk_xxxxxxxxxxxxx
SENDCHAMP_SECRET_KEY=sendchamp_sk_xxxxxxxxxxxxx
SENDCHAMP_SENDER_ID=CampusDeal  # Or "Sendchamp" until approved
SENDCHAMP_BASE_URL=https://api.sendchamp.com/api/v1
```

### **Pricing:**
- SMS Cost: **₦1.50** per SMS (50% cheaper than Termii!)
- No monthly fees
- No setup fees
- Pay-as-you-go

### **SMS Budget Estimate:**
- 1,000 users/month × 2 SMS each = 2,000 SMS
- Cost: 2,000 × ₦1.50 = **₦3,000/month**

---

## 3️⃣ CLOUDINARY SETUP (Image Storage)

### **Step 1: Create Account**

1. Go to: https://cloudinary.com/users/register/free
2. Fill in:
   - **Email:** your-email@gmail.com
   - **Password:** (Strong password)
   - **Cloud Name:** campusdeal (or any unique name)
3. Click **"Create Account"**
4. **Verify email**

### **Step 2: Get Credentials**

1. Login to dashboard: https://cloudinary.com/console
2. You'll see **Account Details** on homepage:
   - **Cloud Name:** campusdeal
   - **API Key:** 123456789012345
   - **API Secret:** xxxxxxxxxxxxxxxxxxxxx
3. Copy these values

### **Step 3: Configure Upload Settings**

1. Go to **Settings** → **Upload**
2. Enable:
   - ✅ **Unsigned uploads** (for direct browser uploads)
   - ✅ **Auto-tagging**
   - ✅ **Auto-format** (automatic image optimization)
3. Set **Upload Preset:**
   - Click **"Add upload preset"**
   - Name: `campusdeal_items`
   - Mode: **Unsigned**
   - Folder: `campusdeal/items`
   - Format: **Auto**
   - Quality: **Auto**
   - Click **"Save"**

### **Step 4: Create Upload Presets**

**For Item Images:**
- Preset Name: `campusdeal_items`
- Max file size: 5MB
- Allowed formats: jpg, png, webp
- Transformation: Resize to 1200x1200 (maintain aspect ratio)

**For Hostel Images:**
- Preset Name: `campusdeal_hostels`
- Max file size: 5MB
- Allowed formats: jpg, png, webp
- Transformation: Resize to 1600x1200

### **What to Add to .env:**

```env
# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=campusdeal
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=xxxxxxxxxxxxxxxxxxxxx
CLOUDINARY_UPLOAD_PRESET=campusdeal_items
```

### **Free Tier Limits:**
- Storage: **25GB**
- Bandwidth: **25GB/month**
- Transformations: **25,000/month**
- **Perfect for 10,000+ listings!**

### **Pricing (if you exceed free tier):**
- Storage: ₦15/GB/month
- Bandwidth: ₦20/GB
- Upgrade when you hit 10,000 users

---

## 4️⃣ POSTGRESQL DATABASE

### **Option A: Railway (Recommended - Easiest)**

1. Go to: https://railway.app
2. Click **"Start a New Project"**
3. Select **"Provision PostgreSQL"**
4. Copy connection details:
   - Host: `containers-us-west-xxx.railway.app`
   - Port: `5432`
   - Database: `railway`
   - Username: `postgres`
   - Password: `xxxxxxxxxxxxx`

**What to Add to .env:**
```env
DATABASE_URL=postgresql://postgres:password@host:5432/railway
```

**Pricing:**
- Free: 500MB storage, 5GB bandwidth
- Paid: $5/month for 8GB storage

---

### **Option B: Supabase (Free Forever)**

1. Go to: https://supabase.com
2. Click **"Start your project"**
3. Create organization: **CampusDeal**
4. Create project:
   - Name: **campusdeal-prod**
   - Database Password: (Strong password)
   - Region: **Singapore** (closest to Nigeria)
5. Wait 2 minutes for setup
6. Go to **Settings** → **Database**
7. Copy **Connection String**

**What to Add to .env:**
```env
DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
```

**Pricing:**
- Free: 500MB storage, unlimited API requests
- Paid: $25/month for 8GB storage

---

### **Option C: Hetzner + Self-Hosted (Cheapest)**

**If using Hetzner VPS:**
1. SSH into server
2. Install PostgreSQL:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib -y
```

3. Create database:
```bash
sudo -u postgres psql
CREATE DATABASE campusdeal;
CREATE USER campusdeal_user WITH PASSWORD 'your_strong_password';
GRANT ALL PRIVILEGES ON DATABASE campusdeal TO campusdeal_user;
\q
```

**What to Add to .env:**
```env
DATABASE_URL=postgresql://campusdeal_user:password@localhost:5432/campusdeal
```

**Pricing:** Free (included in VPS cost)

---

## 5️⃣ SENTRY SETUP (Error Monitoring)

### **Step 1: Create Account**

1. Go to: https://sentry.io/signup/
2. Sign up with GitHub or Email
3. Create organization: **CampusDeal**

### **Step 2: Create Project**

1. Click **"Create Project"**
2. Select platform: **Django**
3. Project name: **campusdeal-backend**
4. Click **"Create Project"**

### **Step 3: Get DSN**

1. You'll see setup instructions
2. Copy **DSN**: `https://xxxxx@xxxxx.ingest.sentry.io/xxxxx`

### **Step 4: Install & Configure**

```bash
pip install sentry-sdk
```

**What to Add to .env:**
```env
SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx
```

**Add to settings.py:**
```python
import sentry_sdk

if not DEBUG:
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        traces_sample_rate=0.1,
        environment='production'
    )
```

**Pricing:**
- Free: 5,000 errors/month
- Paid: $26/month for 50,000 errors

---

## 6️⃣ OPTIONAL SERVICES

### **A. AWS S3 (Alternative to Cloudinary)**

**Only if you prefer S3 over Cloudinary**

1. Go to: https://aws.amazon.com
2. Create account (requires credit card)
3. Go to **S3** → **Create Bucket**
4. Bucket name: `campusdeal-media`
5. Region: **eu-west-1** (Ireland - closest to Nigeria)
6. Uncheck **"Block all public access"**
7. Create IAM user with S3 permissions
8. Copy Access Key & Secret Key

**Pricing:**
- Storage: $0.023/GB/month (₦35/GB)
- Transfer: $0.09/GB (₦135/GB)
- **More expensive than Cloudinary!**

---

### **B. Firebase (Push Notifications)**

**For in-app notifications (Phase 2)**

1. Go to: https://console.firebase.google.com
2. Click **"Add Project"**
3. Project name: **CampusDeal**
4. Disable Google Analytics (not needed)
5. Go to **Project Settings** → **Cloud Messaging**
6. Copy **Server Key**

**What to Add to .env:**
```env
FIREBASE_SERVER_KEY=xxxxxxxxxxxxxxxxxxxxx
```

**Pricing:** Free (unlimited notifications)

---

## 📝 COMPLETE .ENV FILE

After setting up all services, your `.env` should look like:

```env
# Django
SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
FRONTEND_URL=https://yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@host:5432/database

# Paystack
PAYSTACK_SECRET_KEY=sk_live_xxxxxxxxxxxxx
PAYSTACK_PUBLIC_KEY=pk_live_xxxxxxxxxxxxx
PAYSTACK_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx

# Sendchamp (SMS)
SENDCHAMP_PUBLIC_KEY=sendchamp_pk_xxxxxxxxxxxxx
SENDCHAMP_SECRET_KEY=sendchamp_sk_xxxxxxxxxxxxx
SENDCHAMP_SENDER_ID=CampusDeal
SENDCHAMP_BASE_URL=https://api.sendchamp.com/api/v1

# Cloudinary (Images)
CLOUDINARY_CLOUD_NAME=campusdeal
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=xxxxxxxxxxxxxxxxxxxxx

# Sentry (Error Monitoring)
SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx

# Email (Optional - for password reset)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=CampusDeal <noreply@campusdeal.com>
```

---

## ✅ SETUP CHECKLIST

### **Critical (Must Have for Launch):**
- [ ] Paystack account created
- [ ] Paystack KYC submitted
- [ ] Paystack Test Keys obtained
- [ ] Paystack Webhook configured
- [ ] Sendchamp account created
- [ ] Sendchamp funded (₦5,000 minimum)
- [ ] Sendchamp Sender ID registered
- [ ] Cloudinary account created
- [ ] Cloudinary upload presets configured
- [ ] PostgreSQL database created
- [ ] All credentials added to .env

### **Important (Recommended):**
- [ ] Sentry account created
- [ ] Sentry DSN configured
- [ ] Email SMTP configured
- [ ] Domain purchased
- [ ] SSL certificate obtained

### **Optional (Can Add Later):**
- [ ] Firebase for push notifications
- [ ] AWS S3 (if not using Cloudinary)
- [ ] Google Analytics
- [ ] Monitoring tools (UptimeRobot)

---

## 💰 TOTAL SETUP COSTS

### **One-Time Costs:**
- Domain name: ₦5,000/year
- SSL certificate: Free (Let's Encrypt)
- **Total: ₦5,000**

### **Monthly Costs (First 1,000 Users):**
- Paystack: ₦0 (pay per transaction)
- Sendchamp: ₦3,000 (2,000 SMS)
- Cloudinary: ₦0 (free tier)
- PostgreSQL: ₦0 (free tier)
- Sentry: ₦0 (free tier)
- **Total: ₦3,000/month**

### **Monthly Costs (5,000 Users):**
- Paystack: ₦0 (pay per transaction)
- Sendchamp: ₦15,000 (10,000 SMS)
- Cloudinary: ₦0 (still within free tier)
- PostgreSQL: ₦7,500 (Railway $5/month)
- Sentry: ₦0 (free tier)
- **Total: ₦22,500/month**

---

## 🚀 NEXT STEPS

1. **Create all accounts** (2-3 hours)
2. **Submit KYC documents** (wait 1-3 days)
3. **Fund Sendchamp** (₦5,000 for testing)
4. **Update .env file** with all credentials
5. **Test each service:**
   - Send test SMS
   - Process test payment
   - Upload test image
   - Trigger test error (Sentry)
6. **Deploy to production**

---

## 📞 SUPPORT CONTACTS

**Paystack:**
- Email: support@paystack.com
- Phone: +234 1 888 3881
- Response time: 2-4 hours

**Sendchamp:**
- Email: support@sendchamp.com
- WhatsApp: +234 817 000 1234
- Response time: 1-2 hours

**Cloudinary:**
- Email: support@cloudinary.com
- Live chat: Available on dashboard
- Response time: 4-8 hours

---

## ⚠️ IMPORTANT SECURITY NOTES

1. **Never commit .env file to GitHub**
2. **Use Test Keys for development**
3. **Switch to Live Keys only in production**
4. **Rotate API keys every 6 months**
5. **Enable 2FA on all accounts**
6. **Keep webhook secrets secure**
7. **Monitor API usage daily**

---

**Status:** Ready to setup! 🚀  
**Time Required:** 2-3 hours  
**Difficulty:** Easy (just follow steps)
