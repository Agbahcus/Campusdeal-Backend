# 🚀 CAMPUSDEAL DEPLOYMENT GUIDE

## ✅ FEATURES IMPLEMENTED

### Core Features:
- ✅ User authentication (register, login, logout)
- ✅ Phone verification via SMS
- ✅ Password reset
- ✅ Marketplace listings
- ✅ Order management
- ✅ Order cancellation
- ✅ Wallet system
- ✅ Withdrawal system
- ✅ Refund system
- ✅ Review system
- ✅ Hostel listings
- ✅ Chat system

### Security Features:
- ✅ Rate limiting
- ✅ Password complexity
- ✅ Token blacklist
- ✅ Input validation
- ✅ Race condition protection
- ✅ SQL injection protection

---

## 📋 PRE-DEPLOYMENT CHECKLIST

### 1. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### 2. Required Services

#### Paystack (Payment Gateway)
1. Sign up at https://paystack.com
2. Get API keys from Settings → API Keys & Webhooks
3. Add to .env:
   ```
   PAYSTACK_PUBLIC_KEY=pk_live_xxx
   PAYSTACK_SECRET_KEY=sk_live_xxx
   ```
4. Configure webhook: `https://yourdomain.com/api/marketplace/payments/webhook/`

#### Termii (SMS Service)
1. Sign up at https://termii.com
2. Get API key from dashboard
3. Add to .env:
   ```
   TERMII_API_KEY=your_api_key
   TERMII_SENDER_ID=CampusDeal
   ```

### 3. Database Setup (PostgreSQL)
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE campusdeal_db;
CREATE USER campusdeal_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE campusdeal_db TO campusdeal_user;
\q

# Update .env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=campusdeal_db
DB_USER=campusdeal_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 8. Create Media Directories
```bash
mkdir -p media/profile_pics
mkdir -p media/item_images
mkdir -p media/hostel_images
mkdir -p media/refund_evidence
```

---

## 🔒 PRODUCTION SETTINGS

### Update .env for Production:
```bash
SECRET_KEY=generate-new-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
FRONTEND_URL=https://yourdomain.com
```

### Generate Secret Key:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 🌐 DEPLOYMENT OPTIONS

### Option 1: Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize
railway init

# Deploy
railway up
```

### Option 2: Heroku
```bash
# Install Heroku CLI
# Create Procfile
echo "web: gunicorn campusdeal.wsgi" > Procfile

# Deploy
heroku create campusdeal-api
git push heroku main
heroku run python manage.py migrate
```

### Option 3: DigitalOcean/AWS
```bash
# Install Nginx
sudo apt-get install nginx

# Install Gunicorn
pip install gunicorn

# Create systemd service
sudo nano /etc/systemd/system/campusdeal.service

# Start service
sudo systemctl start campusdeal
sudo systemctl enable campusdeal
```

---

## 🧪 POST-DEPLOYMENT TESTING

### 1. Test Registration
```bash
curl -X POST https://yourdomain.com/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"+2348012345678","password":"Test123","full_name":"Test User","email":"test@test.com","primary_location":"ilorin"}'
```

### 2. Test Login
```bash
curl -X POST https://yourdomain.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"+2348012345678","password":"Test123"}'
```

### 3. Test Withdrawal
```bash
curl -X GET https://yourdomain.com/api/marketplace/wallet/withdrawal-fees/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 MONITORING

### Setup Error Tracking (Sentry)
```bash
pip install sentry-sdk

# Add to settings.py
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

### Setup Logging
```python
# Already configured in settings.py
# Logs will be in logs/django.log
```

---

## 🔐 SECURITY CHECKLIST

- [ ] SECRET_KEY changed
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS configured
- [ ] HTTPS enabled
- [ ] Paystack webhook configured
- [ ] Database password strong
- [ ] Firewall configured
- [ ] Rate limiting active
- [ ] CORS configured
- [ ] Static files served via CDN

---

## 📞 SUPPORT

### Common Issues:

**SMS not sending:**
- Check TERMII_API_KEY is correct
- Check account balance
- Check sender ID is approved

**Payments failing:**
- Check PAYSTACK_SECRET_KEY
- Verify webhook URL is accessible
- Check Paystack dashboard for errors

**Withdrawals failing:**
- Check Paystack transfer is enabled
- Verify bank account details
- Check webhook is receiving events

---

## 🎯 NEXT STEPS

1. Test all endpoints
2. Create test data
3. Invite beta users
4. Monitor error logs
5. Setup backup system
6. Configure CDN for media files
7. Setup automated backups

---

**Deployment Status:** READY ✅  
**Missing:** External service credentials only
