# 🖼️ CLOUDINARY SETUP - COMPLETE WALKTHROUGH

## ⏱️ Time: 10 minutes

---

## STEP 1: CREATE ACCOUNT (2 min)

1. **Go to**: https://cloudinary.com/users/register/free
2. **Fill the form**:
   ```
   Email: your-email@gmail.com
   Password: (Strong password - save it!)
   Cloud Name: campusdeal (or any unique name - SAVE THIS!)
   ```
   
   **IMPORTANT**: Cloud Name must be unique globally. If "campusdeal" is taken, try:
   - campusdeal2024
   - campusdeal-ng
   - campusdeal-marketplace
   
3. **Check**: "I agree to terms"
4. **Click**: "Create Account"
5. **Check your email** for verification link
6. **Click the link** to verify

---

## STEP 2: SKIP THE WIZARD (1 min)

After verification, you'll see a setup wizard.

1. **You'll see**: "Tell us about yourself"
2. **Click**: "Skip" or "I'll do this later" (bottom of page)
3. **You'll land on**: Dashboard (main page)

---

## STEP 3: GET YOUR CREDENTIALS (2 min)

**On the Dashboard homepage, you'll immediately see a box called "Account Details"**

It shows:
```
Cloud name: ca
API Key: 478756491371227
API Secret: RXRtrSg52KbhbZGr0mydcuHdayY   (click eye icon to reveal)
```

**COPY ALL THREE** to notepad:

1. **Cloud Name**: campusdeal (or whatever you chose)
2. **API Key**: Click to copy (looks like: 123456789012345)
3. **API Secret**: 
   - Click the **eye icon** (👁️) to reveal
   - Click to copy (looks like: aBcDeFgHiJkLmNoPqRsTuVwXyZ)

**Save to notepad**:
```
CLOUDINARY_CLOUD_NAME=campusdeal
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=aBcDeFgHiJkLmNoPqRsTuVwXyZ
```

---

## STEP 4: CREATE UPLOAD PRESET (5 min)

**This allows your app to upload images directly**

1. **Top navigation** → Click **"Settings"** (gear icon, top right)
2. **Left sidebar** → Click **"Upload"** (under "Product Environment")
3. **Scroll down** to **"Upload presets"** section
4. **Click**: "Add upload preset" (blue link)

**Configure the preset**:

```
Preset name: campusdeal_items
Signing mode: Unsigned (IMPORTANT!)
Folder: campusdeal/items
Use filename: Yes
Unique filename: Yes
Overwrite: No
```

**Advanced settings** (scroll down):
```
Format: Auto (leave as is)
Quality: Auto (leave as is)
Allowed formats: jpg, png, webp
Max file size: 5 MB
```

5. **Click**: "Save" (top right)

**COPY THE PRESET NAME** to notepad:
```
CLOUDINARY_UPLOAD_PRESET=campusdeal_items
```

---

## STEP 5: CREATE FOLDERS (Optional - 2 min)

**Organize your images by type**

1. **Top navigation** → Click **"Media Library"**
2. **Click**: "New Folder" (top right)
3. **Create these folders**:
   ```
   campusdeal/items
   campusdeal/hostels
   campusdeal/profiles
   ```

**This is optional** - folders will be created automatically when you upload.

---

## STEP 6: TEST UPLOAD (Optional - 2 min)

**Verify everything works**

1. **Go to**: "Media Library"
2. **Click**: "Upload" (blue button)
3. **Select any image** from your computer
4. **Wait for upload** (should be instant)
5. **You'll see the image** in your library

**If upload works**: ✅ Setup complete!

---

## ✅ WHAT YOU NEED FOR RAILWAY

Copy these to your notepad:

```
CLOUDINARY_CLOUD_NAME=campusdeal
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=aBcDeFgHiJkLmNoPqRsTuVwXyZ
```

**Note**: We're not using upload preset in backend (Django handles uploads), but good to have.

---

## 📊 FREE TIER LIMITS

**What you get FREE forever**:
- **Storage**: 25 GB
- **Bandwidth**: 25 GB/month
- **Transformations**: 25,000/month
- **Images**: Unlimited

**This is enough for**:
- 10,000+ item listings (3 images each)
- 5,000+ hostel listings
- 50,000+ monthly views

**You won't need to upgrade until you have 10,000+ users!**

---

## 🚨 COMMON ISSUES

### Issue 1: Cloud Name Already Taken
**Solution**: Try variations:
- campusdeal2024
- campusdeal-ng
- campusdeal-marketplace
- campusdeal-app

### Issue 2: Can't Find API Credentials
**Solution**: 
- Go to Dashboard (home page)
- Look for "Account Details" box
- It's right at the top!

### Issue 3: Upload Preset Not Working
**Solution**: 
- Make sure "Signing mode" is "Unsigned"
- Check preset name is correct (no spaces)

### Issue 4: Can't See API Secret
**Solution**: 
- Click the eye icon (👁️) next to API Secret
- Then click to copy

---

## 🔒 SECURITY NOTE

**NEVER commit these to GitHub**:
- API Secret (keep private!)
- API Key (can be public, but better to keep private)

**Your .gitignore already protects**:
- .env files
- credentials

---

## 📞 SUPPORT

**Email**: support@cloudinary.com  
**Live Chat**: Available on dashboard (bottom right)  
**Docs**: https://cloudinary.com/documentation  
**Response Time**: 4-8 hours

---

## ✅ CHECKLIST

- [ ] Account created
- [ ] Email verified
- [ ] Cloud Name chosen and saved
- [ ] API Key copied
- [ ] API Secret copied (revealed and copied)
- [ ] Upload preset created (optional)
- [ ] Test upload successful (optional)
- [ ] All credentials saved in notepad

---

## 📝 YOUR CREDENTIALS SUMMARY

**Copy this to notepad and fill in your values**:

```
# SENDCHAMP
SENDCHAMP_PUBLIC_KEY=sendchamp_live_$2a$10$uEji8QDvv9.peFAYkREixOz3QaNlZtelbR/IfVxeBp59l60OISp3S
SENDCHAMP_SECRET_KEY=sendchamp_live_sk_xxxxxxxxxxxxx
SENDCHAMP_SENDER_ID=Sendchamp
SENDCHAMP_BASE_URL=https://api.sendchamp.com/api/v1

# CLOUDINARY
CLOUDINARY_CLOUD_NAME=campusdeal
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=aBcDeFgHiJkLmNoPqRsTuVwXyZ

# PAYSTACK (you already have these)
PAYSTACK_SECRET_KEY=sk_test_xxxxxxxxxxxxx
PAYSTACK_PUBLIC_KEY=pk_test_xxxxxxxxxxxxx
```

---

**NEXT**: Deploy to Railway!

**Status**: ✅ Cloudinary Ready!
