# 📱 SENDCHAMP SETUP - COMPLETE WALKTHROUGH

## ⏱️ Time: 15 minutes

---

## STEP 1: CREATE ACCOUNT (3 min)

1. **Go to**: https://www.sendchamp.com
2. **Click**: "Get Started Free" (big blue button, top right)
3. **Fill the form**:
   ```
   Full Name: Your Name
   Email: your-email@gmail.com
   Phone Number: +234XXXXXXXXXX
   Password: (Strong password - save it!)
   Business Name: CampusDeal
   ```
4. **Click**: "Sign Up"
5. **Check your email** for verification link
6. **Click the link** in email to verify

---

## STEP 2: COMPLETE PROFILE (2 min)

After email verification, you'll be redirected to dashboard.

1. **You'll see a welcome popup** - Click "Get Started"
2. **Complete Business Profile**:
   ```
   Business Type: Technology/Software
   Industry: E-commerce/Marketplace
   Use Case: OTP & Transactional SMS
   Expected Monthly Volume: 1,000 - 5,000 SMS
   ```
3. **Click**: "Save" or "Continue"

---

## STEP 3: GET API KEYS (2 min)

1. **Look at left sidebar** → Click **"Settings"** (gear icon at bottom)
2. **Click**: "API Keys" (in the settings menu)
3. **You'll see TWO keys**:
   ```
   Public Key: sendchamp_live_pk_xxxxxxxxxxxxx
   Secret Key: sendchamp_live_sk_xxxxxxxxxxxxx (click "Show" to reveal)
   ```
4. **COPY BOTH KEYS** to a notepad file:
   ```
   SENDCHAMP_PUBLIC_KEY=sendchamp_live_pk_xxxxxxxxxxxxx
   SENDCHAMP_SECRET_KEY=sendchamp_live_sk_xxxxxxxxxxxxx
   ```

**IMPORTANT**: These are LIVE keys (not test keys). Sendchamp doesn't have test mode.

---

## STEP 4: FUND YOUR WALLET (5 min)

**You MUST fund wallet before sending SMS!**

1. **Left sidebar** → Click **"Wallet"**
2. **Click**: "Fund Wallet" (big button)
3. **Enter amount**: ₦5,000 (minimum recommended)
4. **Choose payment method**:
   - **Option A: Bank Transfer** (instant, free)
     - Copy the account details shown
     - Transfer ₦5,000 from your bank app
     - Wait 1-2 minutes for confirmation
   
   - **Option B: Card Payment** (instant)
     - Click "Pay with Card"
     - Enter card details
     - Complete payment
     - Instant credit

5. **Wait for confirmation** - You'll see balance update

---

## STEP 5: REGISTER SENDER ID (Optional - Can Skip for Now)

**What is Sender ID?** The name that appears as SMS sender (e.g., "CampusDeal")

**For TODAY**: Skip this! Use "Sendchamp" as sender (pre-approved)

**For LATER** (after launch):
1. **Left sidebar** → Click **"SMS"** → **"Sender IDs"**
2. **Click**: "Request Sender ID"
3. **Fill form**:
   ```
   Sender ID: CampusDeal (max 11 characters, no spaces)
   Purpose: Transactional
   Sample Message: "Your CampusDeal verification code is 123456"
   ```
4. **Upload**: ID card or CAC certificate
5. **Submit** - Wait 1-2 business days for approval

**Until approved, use**: `SENDCHAMP_SENDER_ID=Sendchamp`

---

## STEP 6: TEST SMS (3 min)

**Let's verify everything works!**

1. **Left sidebar** → Click **"SMS"** → **"Send SMS"**
2. **Fill the form**:
   ```
   Sender ID: Sendchamp (from dropdown)
   Recipient: +234XXXXXXXXXX (your phone number)
   Message: "Test SMS from CampusDeal. If you receive this, setup is complete!"
   ```
3. **Click**: "Send SMS"
4. **Check your phone** - SMS should arrive in 5-30 seconds
5. **Check wallet** - Balance should reduce by ₦1.50

**If SMS arrives**: ✅ Setup complete!
**If SMS doesn't arrive**: Check phone number format (+234, not 0)

---

## ✅ WHAT YOU NEED FOR RAILWAY

Copy these to your notepad:

```
SENDCHAMP_PUBLIC_KEY=sendchamp_live_pk_xxxxxxxxxxxxx
SENDCHAMP_SECRET_KEY=sendchamp_live_sk_xxxxxxxxxxxxx
SENDCHAMP_SENDER_ID=Sendchamp
SENDCHAMP_BASE_URL=https://api.sendchamp.com/api/v1
```

**Wallet Balance**: ₦5,000 (or whatever you funded)

---

## 💰 PRICING

- **Cost per SMS**: ₦1.50
- **Your ₦5,000**: ~3,333 SMS
- **Enough for**: 1,600+ user registrations (2 SMS each)

---

## 🚨 COMMON ISSUES

### Issue 1: "Insufficient Balance"
**Solution**: Fund wallet with at least ₦1,000

### Issue 2: SMS Not Sending
**Solution**: 
- Check phone format: +234XXXXXXXXXX (not 0XXXXXXXXXX)
- Check wallet has balance
- Use "Sendchamp" as sender (not "CampusDeal" until approved)

### Issue 3: Can't Find API Keys
**Solution**: Settings (gear icon) → API Keys

### Issue 4: Payment Not Reflecting
**Solution**: 
- Bank transfer: Wait 2-5 minutes
- Card payment: Should be instant
- Contact support: support@sendchamp.com

---

## 📞 SUPPORT

**Email**: support@sendchamp.com  
**WhatsApp**: +234 817 000 1234  
**Response Time**: 1-2 hours

---

## ✅ CHECKLIST

- [ ] Account created
- [ ] Email verified
- [ ] Profile completed
- [ ] API keys copied
- [ ] Wallet funded (₦5,000)
- [ ] Test SMS sent successfully
- [ ] Keys saved in notepad

---

**NEXT**: Setup Cloudinary (10 minutes)

**Status**: ✅ Sendchamp Ready!
