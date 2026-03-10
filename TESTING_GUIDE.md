# API Flow Testing Guide

## Quick Start

### 1. Start the Server
```bash
python manage.py runserver
```

### 2. Run Automated Tests
```bash
pip install requests
python test_api_flow.py
```

## Manual Testing (Using curl or Postman)

### Test 1: Registration (Password Validation)
```bash
# Should FAIL - weak password
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d "{\"phone_number\":\"+2348012345678\",\"password\":\"weak123\",\"first_name\":\"Test\",\"last_name\":\"User\",\"email\":\"test@example.com\",\"university\":\"Test Uni\"}"

# Should SUCCEED - strong password
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d "{\"phone_number\":\"+2348012345679\",\"password\":\"StrongPass123\",\"first_name\":\"Test\",\"last_name\":\"User\",\"email\":\"test2@example.com\",\"university\":\"Test Uni\"}"
```

### Test 2: Login
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d "{\"phone_number\":\"+2348012345679\",\"password\":\"StrongPass123\"}"
```

Save the `access` and `refresh` tokens from response.

### Test 3: Browse Listings (with Search Validation)
```bash
# Replace YOUR_TOKEN with actual token
curl -X GET "http://127.0.0.1:8000/api/marketplace/listings/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test search
curl -X GET "http://127.0.0.1:8000/api/marketplace/listings/?search=laptop" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test XSS protection (should sanitize)
curl -X GET "http://127.0.0.1:8000/api/marketplace/listings/?search=<script>alert('xss')</script>" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test 4: Hostel Listings
```bash
curl -X GET "http://127.0.0.1:8000/api/marketplace/hostels/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test 5: User Profile
```bash
curl -X GET "http://127.0.0.1:8000/api/auth/profile/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test 6: Logout (Token Blacklist)
```bash
curl -X POST http://127.0.0.1:8000/api/auth/logout/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\":\"YOUR_REFRESH_TOKEN\"}"
```

### Test 7: Rate Limiting
```bash
# Try logging in 11 times with wrong password (should block after 10)
for i in {1..11}; do
  echo "Attempt $i"
  curl -X POST http://127.0.0.1:8000/api/auth/login/ \
    -H "Content-Type: application/json" \
    -d "{\"phone_number\":\"+2348099999999\",\"password\":\"WrongPass123\"}"
  echo ""
done
```

## Expected Results

### ✅ Working Features:
- Strong password required (uppercase, lowercase, number)
- Rate limiting blocks after threshold
- Login returns JWT tokens
- Logout blacklists tokens
- Search input sanitized
- All endpoints respond correctly
- Database transactions atomic

### ❌ Expected Limitations (until external services setup):
- Phone verification won't send SMS (no Termii account)
- Payment processing won't work (no Paystack account)
- Image uploads to cloud won't work (no S3/Cloudinary)

## Troubleshooting

### Server won't start:
```bash
python manage.py migrate
python manage.py check
```

### Import errors:
```bash
pip install -r requirements.txt
```

### Database locked:
```bash
# Delete db.sqlite3 and recreate
python manage.py migrate
```

## What to Check

1. ✅ Server starts without errors
2. ✅ Weak passwords rejected
3. ✅ Strong passwords accepted
4. ✅ Login returns tokens
5. ✅ Logout blacklists tokens
6. ✅ Rate limiting works
7. ✅ Search sanitizes input
8. ✅ All endpoints respond
9. ✅ No database errors
10. ✅ No race condition errors

## Next Steps After Testing

1. Create superuser: `python manage.py createsuperuser`
2. Access admin: http://127.0.0.1:8000/admin/
3. Create test data
4. Setup external services (Paystack, Termii)
5. Test payment flows
