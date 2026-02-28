# ⚡ IMMEDIATE ACTION CHECKLIST
## Things You Can Do RIGHT NOW (No External Services Needed)

---

## ✅ COMPLETED
- [x] Fixed image_1 field migration issue
- [x] Applied all database migrations
- [x] Installed all required dependencies

---

## 🎯 DO THESE NOW (5 minutes)

### 1. Create Superuser Account
```bash
python manage.py createsuperuser
```
- Username: admin (or your choice)
- Email: your-email@example.com
- Password: (strong password)

### 2. Create Media Directories
```bash
mkdir media
mkdir media\profile_pics
mkdir media\item_images
mkdir media\refund_evidence
```

### 3. Generate New SECRET_KEY
```bash
python manage.py shell
```
Then run:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```
Copy the output and update your .env file

---

## 🧪 TEST WHAT'S WORKING (15 minutes)

### 4. Access Admin Panel
1. Start server: `python manage.py runserver`
2. Go to: http://127.0.0.1:8000/admin/
3. Login with superuser credentials
4. Explore all models

### 5. Create Test Categories
In admin panel:
- Electronics
- Books
- Fashion
- Furniture

### 6. Create Test Users
In admin panel → Profiles:
- Create 2-3 test users
- Set phone_verified = True
- Set different locations

### 7. Test Content Moderator
```bash
python manage.py shell
```
```python
from communication.content_moderator import moderator

# Test messages
test_messages = [
    "Call me on 08012345678",  # Should be blocked
    "Is this still available?",  # Should pass
    "Meet me at my hostel",  # Should be blocked
    "What's the condition?",  # Should pass
]

for msg in test_messages:
    result = moderator.scan_message(msg)
    status = "❌ BLOCKED" if not result['is_clean'] else "✅ PASSED"
    print(f"{status}: {msg}")
    if not result['is_clean']:
        print(f"  Flags: {result['flags']}")
```

---

## 📊 CHECK DATABASE STATUS (2 minutes)

### 8. View Current Data
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User
from accounts.models import Profile
from marketplace.models import ItemCategory, ItemListing, Order

print(f"Users: {User.objects.count()}")
print(f"Profiles: {Profile.objects.count()}")
print(f"Verified: {Profile.objects.filter(phone_verified=True).count()}")
print(f"Categories: {ItemCategory.objects.count()}")
print(f"Listings: {ItemListing.objects.count()}")
print(f"Orders: {Order.objects.count()}")
```

---

## 🔧 CONFIGURATION UPDATES (10 minutes)

### 9. Update .env File
Replace these placeholder values:

```env
# Generate a new one from step 3
SECRET_KEY=your-new-generated-secret-key-here

# Keep as True for development
DEBUG=True

# Add your local IP if testing from mobile
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.XXX
```

### 10. Create .gitignore (if not exists)
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Django
*.log
db.sqlite3
db.sqlite3-journal
/media/
/staticfiles/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

---

## 📝 MANUAL TESTING SCENARIOS (30 minutes)

### 11. Test API Endpoints with Postman/Thunder Client

#### A. Register User (Will fail at SMS, but user created)
```
POST http://127.0.0.1:8000/api/auth/register/
Content-Type: application/json

{
    "full_name": "Test User",
    "email": "test@example.com",
    "phone_number": "+2348012345678",
    "password": "testpass123",
    "primary_location": "ilorin",
    "user_type": "student"
}
```
Note: Check console for verification code

#### B. Verify Phone (Use code from console)
```
POST http://127.0.0.1:8000/api/auth/verify-phone/
Content-Type: application/json

{
    "user_id": 1,
    "code": "123456"
}
```
Save the access_token from response

#### C. Get Profile
```
GET http://127.0.0.1:8000/api/users/me/
Authorization: Bearer YOUR_ACCESS_TOKEN
```

#### D. Create Listing (Will fail without image, but tests validation)
```
POST http://127.0.0.1:8000/api/marketplace/listings/create/
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
    "title": "Test Laptop",
    "description": "Good condition laptop",
    "category": 1,
    "condition": "fairly_used",
    "price": "50000.00",
    "location": "ilorin",
    "is_negotiable": true,
    "allow_pickup": true
}
```

#### E. Browse Listings
```
GET http://127.0.0.1:8000/api/marketplace/listings/
```

#### F. Create Chat
```
POST http://127.0.0.1:8000/api/chats/create/
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
    "other_user_id": 2,
    "item_id": 1
}
```

#### G. Send Message (Test Moderation)
```
POST http://127.0.0.1:8000/api/chats/1/messages/send/
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
    "text": "Is this still available?"
}
```

#### H. Send Blocked Message
```
POST http://127.0.0.1:8000/api/chats/1/messages/send/
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
    "text": "Call me on 08012345678"
}
```
Should be blocked!

---

## 📋 DOCUMENT YOUR FINDINGS (10 minutes)

### 12. Create Test Results Log
Create a file: `TEST_RESULTS.md`

Document:
- What worked ✅
- What failed ❌
- Error messages
- Unexpected behavior
- Questions/concerns

---

## 🚫 WHAT YOU CANNOT TEST YET

### ❌ Requires External Services:
- SMS verification (need Termii account)
- Paystack payments (need Paystack account)
- Image uploads (need media directory + proper setup)
- Wallet deposits via Paystack
- Email notifications

### ❌ Not Implemented:
- Hostel module (completely missing)
- Password reset endpoint
- Push notifications
- Rate limiting

---

## 📊 SUCCESS CRITERIA

After completing these steps, you should have:

✅ Admin panel accessible  
✅ Test users created  
✅ Categories created  
✅ Content moderator tested  
✅ Basic API endpoints tested  
✅ Understanding of what works vs. what doesn't  
✅ Media directories created  
✅ New SECRET_KEY generated  

---

## 🎯 NEXT PRIORITIES

### After completing immediate tasks:

1. **Create Paystack Account** (1 hour)
   - Sign up at https://dashboard.paystack.com/signup
   - Complete KYC
   - Get test keys
   - Update .env file

2. **Create Termii Account** (1 hour)
   - Sign up at https://www.termii.com/
   - Register sender ID "CampusDeal"
   - Add funds (₦2000 for testing)
   - Get API key
   - Update .env file

3. **Implement Hostel Module** (2-3 days)
   - Create models
   - Create views
   - Create serializers
   - Create admin
   - Add URLs
   - Test functionality

4. **Write Basic Tests** (1-2 days)
   - Authentication tests
   - Marketplace tests
   - Payment tests
   - Moderation tests

---

## 💡 TIPS

### For Testing Without SMS:
1. Create users via admin panel
2. Manually set `phone_verified = True`
3. Set a password via admin
4. Use login endpoint

### For Testing Without Paystack:
1. Add funds to wallet via admin panel
2. Test wallet payment flow
3. Manually update order status via admin

### For Testing Without Images:
1. Create listings without images (now allowed)
2. Test all other functionality
3. Add images later when S3/Cloudinary is setup

---

## 📞 QUESTIONS TO ANSWER

Before proceeding to external services:

1. Which SMS provider? Termii (Nigeria) or Twilio (Global)?
2. Which cloud storage? AWS S3 or Cloudinary?
3. Which hosting? Railway, DigitalOcean, or Heroku?
4. Domain name preference? .ng, .com, or other?
5. Launch timeline? When do you need to go live?

---

## ⏱️ TIME ESTIMATE

- Immediate tasks: **30-45 minutes**
- Manual testing: **30-60 minutes**
- Documentation: **15-30 minutes**

**Total: 1.5 - 2.5 hours**

---

**Start with Step 1 (Create Superuser) and work your way down!**

Good luck! 🚀
