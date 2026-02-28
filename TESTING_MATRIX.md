# 🧪 TESTING CAPABILITY MATRIX
## What You CAN and CANNOT Test Right Now

---

## ✅ CAN TEST NOW (No External Services Required)

### 🔐 Authentication & User Management

| Feature | Can Test? | How to Test | Notes |
|---------|-----------|-------------|-------|
| User Registration | ⚠️ Partial | API endpoint works, but no SMS sent | Check console for verification code |
| Phone Verification | ⚠️ Partial | Works with code from console | Manual code entry |
| Login | ✅ Full | API endpoint with verified users | Create verified users via admin |
| Token Refresh | ✅ Full | Use refresh token endpoint | JWT tokens work |
| Profile View | ✅ Full | GET /api/users/me/ | All fields accessible |
| Profile Update | ✅ Full | PATCH /api/users/me/ | Bio, university, etc. |
| Public Profile View | ✅ Full | GET /api/users/{id}/profile/ | Works for any user |
| Suspension Check | ✅ Full | Set is_suspended=True in admin | Login should fail |

**Testing Method:**
1. Create users via admin panel
2. Set phone_verified=True manually
3. Set password via admin
4. Test login endpoint
5. Use returned JWT tokens

---

### 🛒 Marketplace - Listings

| Feature | Can Test? | How to Test | Notes |
|---------|-----------|-------------|-------|
| Browse Listings | ✅ Full | GET /api/marketplace/listings/ | No auth required |
| Search Listings | ✅ Full | Add ?search=keyword | Works |
| Filter by Location | ✅ Full | Add ?location=ilorin | Works |
| Filter by Category | ✅ Full | Add ?category=1 | Works |
| Filter by Condition | ✅ Full | Add ?condition=new | Works |
| Filter by Price | ✅ Full | Add ?min_price=1000&max_price=5000 | Works |
| Pagination | ✅ Full | Check page parameter | 20 items per page |
| View Single Listing | ✅ Full | GET /api/marketplace/listings/{id}/ | Works |
| View Count | ✅ Full | View same listing multiple times | Increments |
| Create Listing | ⚠️ Partial | POST with JSON (no images) | Images optional now |
| Update Listing | ✅ Full | PATCH own listing | Works |
| Delete Listing | ✅ Full | DELETE own listing | Status changes to 'removed' |
| My Listings | ✅ Full | GET /api/marketplace/my-listings/ | Filter by status |
| User Listings | ✅ Full | GET /api/marketplace/users/{id}/listings/ | Public view |

**Testing Method:**
1. Create listings via API (without images)
2. Or create via admin panel
3. Test all filter combinations
4. Verify permissions (can't edit others' listings)

---

### 📦 Orders & Transactions

| Feature | Can Test? | How to Test | Notes |
|---------|-----------|-------------|-------|
| Initiate Order | ✅ Full | POST /api/marketplace/orders/initiate/ | Creates order |
| Order ID Generation | ✅ Full | Check order_id format | Should be CD + 12 chars |
| Service Fee Calculation | ✅ Full | Check service_fee field | Should be 2.5% |
| Delivery Fee | ✅ Full | Test with campusdeal delivery | ₦500 added |
| Waybill Generation | ✅ Full | Check waybill_number | Auto-generated |
| List Orders | ✅ Full | GET /api/marketplace/orders/ | Buyer & seller views |
| View Order Detail | ✅ Full | GET /api/marketplace/orders/{id}/ | Full details |
| Order Status History | ✅ Full | GET /api/marketplace/orders/{id}/status-history/ | Audit trail |
| Wallet Checkout | ⚠️ Partial | Need to add funds via admin first | Then works |
| Paystack Checkout | ❌ No | Requires Paystack account | Returns error |
| Update Order Status | ✅ Full | POST update-status endpoint | Seller actions |
| Confirm Delivery | ✅ Full | POST confirm-delivery endpoint | Buyer action |
| Cancel Order | ✅ Full | Before payment only | Works |

**Testing Method:**
1. Create order via API
2. Add funds to buyer wallet via admin
3. Checkout with wallet payment
4. Update status through workflow
5. Confirm delivery
6. Check wallet transactions

---

### 💰 Wallet System

| Feature | Can Test? | How to Test | Notes |
|---------|-----------|-------------|-------|
| View Balance | ✅ Full | GET /api/marketplace/wallet/balance/ | Shows current balance |
| Transaction History | ✅ Full | GET /api/marketplace/wallet/transactions/ | All movements |
| Filter Transactions | ✅ Full | Add ?transaction_type=credit | Works |
| Manual Deposit | ✅ Full | Via admin panel | Add to wallet_balance |
| Purchase Deduction | ✅ Full | Complete order with wallet | Auto-deducted |
| Sale Credit | ✅ Full | Complete order as seller | Auto-credited |
| Refund Credit | ✅ Full | Approve refund as admin | Auto-credited |
| Balance Tracking | ✅ Full | Check balance_before/after | Logged correctly |
| Paystack Deposit | ❌ No | Requires Paystack account | Returns error |
| Withdrawal | ❌ No | Not implemented | Returns 501 |

**Testing Method:**
1. Go to admin panel
2. Edit user profile
3. Change wallet_balance
4. Save
5. Check transaction history via API

---

### 💬 Chat & Messaging

| Feature | Can Test? | How to Test | Notes |
|---------|-----------|-------------|-------|
| Create Chat | ✅ Full | POST /api/chats/create/ | With item context |
| List Chats | ✅ Full | GET /api/chats/ | User's conversations |
| View Chat | ✅ Full | GET /api/chats/{id}/ | Chat details |
| Send Message | ✅ Full | POST /api/chats/{id}/messages/send/ | Works |
| Get Messages | ✅ Full | GET /api/chats/{id}/messages/ | Paginated |
| Mark as Read | ✅ Full | POST /api/chats/{id}/mark-read/ | Updates status |
| Unread Count | ✅ Full | GET /api/chats/unread-count/ | Total unread |
| Content Moderation | ✅ Full | Send blocked content | Auto-blocked |
| Phone Detection | ✅ Full | Send "Call 08012345678" | Blocked |
| Email Detection | ✅ Full | Send "test@example.com" | Blocked |
| Location Detection | ✅ Full | Send "meet me at..." | Blocked |
| Strike System | ✅ Full | Send 3 blocked messages | Account suspended |
| Moderation Logs | ✅ Full | GET /api/chats/moderation-logs/ | Admin only |
| System Warnings | ✅ Full | Check message list | Warning messages appear |

**Testing Method:**
1. Create 2 test users
2. Login as user 1
3. Create chat with user 2
4. Send clean messages (should work)
5. Send "Call me on 08012345678" (should be blocked)
6. Check moderation logs in admin

---

### ⭐ Reviews & Ratings

| Feature | Can Test? | How to Test | Notes |
|---------|-----------|-------------|-------|
| Create Review | ✅ Full | POST /api/marketplace/reviews/ | After order completion |
| View User Reviews | ✅ Full | GET /api/marketplace/users/{id}/reviews/ | Public |
| Rating Calculation | ✅ Full | Check profile.rating | Auto-updated |
| Total Ratings Count | ✅ Full | Check profile.total_ratings | Increments |
| One Review Per Order | ✅ Full | Try to review twice | Should fail |
| Review Before Completion | ✅ Full | Try on pending order | Should fail |

**Testing Method:**
1. Complete an order (manually via admin)
2. Set status to 'completed'
3. Create review via API
4. Check reviewee's profile rating

---

### 🔄 Refunds

| Feature | Can Test? | How to Test | Notes |
|---------|-----------|-------------|-------|
| Request Refund | ✅ Full | POST /api/marketplace/orders/{id}/request-refund/ | Works |
| View Refund Request | ✅ Full | GET /api/marketplace/orders/{id}/refund-request/ | Details |
| List Pending Refunds | ✅ Full | GET /api/marketplace/refunds/pending/ | Admin only |
| Approve Refund | ✅ Full | POST /api/marketplace/refunds/{id}/approve/ | Admin only |
| Reject Refund | ✅ Full | POST /api/marketplace/refunds/{id}/reject/ | Admin only |
| Refund Wallet Credit | ✅ Full | Check after approval | Auto-credited |
| Evidence Upload | ⚠️ Partial | Without images for now | Text works |
| 7-Day Window | ✅ Full | Manually set delivered_at | Validation works |

**Testing Method:**
1. Create and complete order
2. Request refund via API
3. Login to admin panel
4. View pending refunds
5. Approve or reject
6. Check wallet transactions

---

### 🏢 Admin Panel

| Feature | Can Test? | How to Test | Notes |
|---------|-----------|-------------|-------|
| Access Admin | ✅ Full | http://127.0.0.1:8000/admin/ | After superuser creation |
| View Users | ✅ Full | Admin → Profiles | All fields |
| Edit Profiles | ✅ Full | Click any profile | Can modify |
| Suspend Users | ✅ Full | Set is_suspended=True | Works |
| View Orders | ✅ Full | Admin → Orders | All details |
| View Refunds | ✅ Full | Admin → Refund Requests | Pending list |
| View Chats | ✅ Full | Admin → Chats | All conversations |
| View Messages | ✅ Full | Admin → Messages | Flagged messages |
| View Moderation Logs | ✅ Full | Admin → Moderated Message Logs | Strike history |
| View Wallet Transactions | ✅ Full | Admin → Wallet Transactions | All movements |
| Create Categories | ✅ Full | Admin → Item Categories | Add new |
| Manually Add Wallet Funds | ✅ Full | Edit profile → wallet_balance | For testing |

**Testing Method:**
1. Create superuser
2. Login to admin
3. Explore all models
4. Test CRUD operations

---

## ❌ CANNOT TEST NOW (Requires External Services)

### 📱 SMS Verification

| Feature | Blocked By | Impact |
|---------|-----------|--------|
| Send SMS Code | No Termii account | Can't verify real phones |
| Resend Code | No Termii account | Can't test resend flow |
| Code Expiration | Can test logic | But no real SMS |
| Phone Validation | Works | But no SMS delivery |

**Workaround:** Use console output for verification codes

---

### 💳 Paystack Payments

| Feature | Blocked By | Impact |
|---------|-----------|--------|
| Initialize Payment | No Paystack keys | Returns error |
| Payment Page | No Paystack keys | Can't redirect |
| Verify Payment | No Paystack keys | Can't verify |
| Webhook Handling | No Paystack keys | Can't test |
| Wallet Deposits | No Paystack keys | Can't add funds via Paystack |
| Seller Payouts | No Paystack keys | Can't transfer to sellers |
| Bank List | No Paystack keys | Can't fetch banks |
| Account Verification | No Paystack keys | Can't verify accounts |

**Workaround:** Use wallet payments with manually added funds

---

### 🖼️ Image Uploads

| Feature | Blocked By | Impact |
|---------|-----------|--------|
| Profile Pictures | No media directory | Upload fails |
| Listing Images | No media directory | Upload fails |
| Refund Evidence | No media directory | Upload fails |
| Image URLs | No media directory | Can't serve images |

**Workaround:** Create media directories, test locally (not production-ready)

---

### 📧 Email Notifications

| Feature | Blocked By | Impact |
|---------|-----------|--------|
| Password Reset | Not implemented | Can't reset password |
| Order Notifications | Not implemented | No email alerts |
| Admin Alerts | Not implemented | No email notifications |

**Workaround:** None - feature not implemented

---

### 🏠 Hostel Module

| Feature | Blocked By | Impact |
|---------|-----------|--------|
| Create Hostel | Not implemented | Module missing |
| Browse Hostels | Not implemented | Module missing |
| Verify Hostels | Not implemented | Module missing |
| All Hostel Features | Not implemented | Complete module missing |

**Workaround:** None - needs to be built

---

## 🎯 TESTING PRIORITY MATRIX

### Priority 1: Test These First (Core Functionality)

1. ✅ User registration (partial)
2. ✅ Login
3. ✅ Profile management
4. ✅ Create listings
5. ✅ Browse listings
6. ✅ Content moderation
7. ✅ Chat messaging
8. ✅ Admin panel access

### Priority 2: Test These Next (Business Logic)

9. ✅ Order creation
10. ✅ Wallet payments
11. ✅ Order status workflow
12. ✅ Delivery confirmation
13. ✅ Reviews
14. ✅ Refund requests
15. ✅ Wallet transactions

### Priority 3: Test When Services Ready

16. ❌ SMS verification (need Termii)
17. ❌ Paystack payments (need Paystack)
18. ❌ Image uploads (need S3/Cloudinary)
19. ❌ Hostel module (need to build)

---

## 📊 TESTING COVERAGE ESTIMATE

### Current Testable: ~70%

| Module | Testable | Blocked | Coverage |
|--------|----------|---------|----------|
| Authentication | 70% | SMS | ⚠️ |
| Marketplace | 90% | Images | ✅ |
| Orders | 60% | Paystack | ⚠️ |
| Wallet | 70% | Paystack | ⚠️ |
| Chat | 100% | None | ✅ |
| Reviews | 100% | None | ✅ |
| Refunds | 90% | Images | ✅ |
| Admin | 100% | None | ✅ |
| Hostels | 0% | Not built | ❌ |

---

## 🔧 WORKAROUNDS FOR TESTING

### For SMS Verification:
```python
# In admin panel:
1. Create user
2. Set phone_verified = True
3. Set password
4. Use login endpoint
```

### For Paystack Payments:
```python
# In admin panel:
1. Edit user profile
2. Set wallet_balance = 10000.00
3. Use wallet payment method
```

### For Image Uploads:
```bash
# Create directories:
mkdir media
mkdir media\profile_pics
mkdir media\item_images
mkdir media\refund_evidence

# Then test locally
# (Not production-ready without S3/Cloudinary)
```

### For Hostel Module:
```
No workaround - must be built
Estimated time: 2-3 days
```

---

## 📝 TESTING CHECKLIST

### Before Starting Tests:

- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Migrations applied (`python manage.py migrate`)
- [ ] Superuser created (`python manage.py createsuperuser`)
- [ ] Media directories created
- [ ] Test users created in admin
- [ ] Test users marked as verified
- [ ] Test categories created
- [ ] Server running (`python manage.py runserver`)

### During Testing:

- [ ] Document what works
- [ ] Document what fails
- [ ] Note error messages
- [ ] Check admin panel after each action
- [ ] Verify database changes
- [ ] Test edge cases
- [ ] Test permissions
- [ ] Test validation

### After Testing:

- [ ] Create bug report
- [ ] List missing features
- [ ] Prioritize fixes
- [ ] Plan next steps

---

## 🚀 RECOMMENDED TESTING SEQUENCE

### Day 1: Setup & Basic Tests (2 hours)
1. Create superuser
2. Create media directories
3. Access admin panel
4. Create test data
5. Test authentication
6. Test profile management

### Day 2: Marketplace Tests (3 hours)
7. Test listing creation
8. Test listing browsing
9. Test search & filters
10. Test listing updates
11. Test permissions

### Day 3: Transaction Tests (3 hours)
12. Test order creation
13. Test wallet payments
14. Test order workflow
15. Test delivery confirmation
16. Test wallet transactions

### Day 4: Communication Tests (2 hours)
17. Test chat creation
18. Test messaging
19. Test content moderation
20. Test strike system
21. Test moderation logs

### Day 5: Reviews & Refunds (2 hours)
22. Test review creation
23. Test rating calculation
24. Test refund requests
25. Test refund approval/rejection

### Day 6: Admin & Edge Cases (2 hours)
26. Test all admin functions
27. Test edge cases
28. Test error handling
29. Test validation
30. Document findings

**Total Testing Time: ~14 hours**

---

## 💡 TESTING TIPS

### Use Postman/Thunder Client:
- Save requests in collections
- Use environment variables for tokens
- Test all HTTP methods
- Check response codes
- Verify response structure

### Check Admin Panel After Each Action:
- Verify database changes
- Check related records
- Verify calculations
- Check timestamps

### Test Negative Cases:
- Invalid data
- Missing required fields
- Unauthorized access
- Expired tokens
- Duplicate actions

### Document Everything:
- What you tested
- What worked
- What failed
- Error messages
- Unexpected behavior

---

## 📞 WHEN TO STOP TESTING

### You've tested enough when:

✅ All testable endpoints work  
✅ Permissions are enforced  
✅ Validation works  
✅ Content moderation works  
✅ Admin panel accessible  
✅ Wallet system works  
✅ Order workflow works  
✅ Edge cases handled  

### Then move to:

1. Setup external services (Paystack, SMS)
2. Build Hostel module
3. Write automated tests
4. Configure production settings
5. Deploy to staging
6. Full end-to-end testing

---

**Remember:** You can test ~70% of functionality right now. The remaining 30% requires external services or missing features.

**Start testing and document your findings!** 🚀
