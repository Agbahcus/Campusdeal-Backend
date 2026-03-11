# 🐘 NEON.TECH SETUP GUIDE - FREE POSTGRESQL

## ⏱️ Time: 5 minutes | Cost: FREE Forever

---

## WHY NEON.TECH?

✅ **FREE FOREVER** (not trial)  
✅ **3GB storage** (enough for 100,000+ users)  
✅ **Always-on** (never sleeps)  
✅ **Auto-scaling** (scales to zero when not used)  
✅ **Instant setup** (no waiting)  
✅ **Global** (fast from Nigeria)  

---

## STEP 1: CREATE ACCOUNT (2 min)

1. **Go to**: https://neon.tech
2. **Click**: "Sign up" (top right)
3. **Choose**: "Continue with GitHub" (easiest option)
4. **Authorize Neon** to access your GitHub
5. **You're in!** No email verification needed

---

## STEP 2: CREATE PROJECT (2 min)

After login, you'll see the dashboard.

1. **Click**: "Create a project" (big green button)

2. **Configure project**:
   ```
   Project name: campusdeal
   Region: AWS Europe (Frankfurt) - closest to Nigeria
   PostgreSQL version: 15 (latest)
   Compute size: 0.25 vCPU, 1 GB RAM (free tier)
   ```

3. **Click**: "Create project"

4. **Wait 30 seconds** for provisioning

---

## STEP 3: GET CONNECTION STRING (1 min)

After project creation, you'll see the **Connection Details** page.

### **Copy these details**:

**You'll see something like this**:
```
Host: ep-cool-darkness-123456.eu-central-1.aws.neon.tech
Database: neondb
Username: neondb_owner
Password: AbCdEf123456 (click eye icon to reveal)
```

### **Connection String (Most Important)**:
```
postgresql://neondb_owner:AbCdEf123456@ep-cool-darkness-123456.eu-central-1.aws.neon.tech/neondb?sslmode=require
```

**COPY THIS ENTIRE STRING** - you'll need it for Koyeb!

**Save to notepad**:
```
DATABASE_URL=postgresql://neondb_owner:AbCdEf123456@ep-cool-darkness-123456.eu-central-1.aws.neon.tech/neondb?sslmode=require
```

---

## STEP 4: TEST CONNECTION (Optional - 1 min)

**You can skip this, but if you want to test**:

1. **Click**: "SQL Editor" (left sidebar)
2. **Try this query**:
   ```sql
   SELECT version();
   ```
3. **Click**: "Run"
4. **Should show**: PostgreSQL version info

**If it works**: ✅ Database ready!

---

## STEP 5: UNDERSTAND YOUR LIMITS

### **Free Tier Includes**:
```
✅ 3 GB storage (enough for 100,000+ users)
✅ 0.5 GB RAM
✅ Unlimited compute hours
✅ Always active (never sleeps)
✅ 1 database
✅ Automatic backups (7 days)
✅ Connection pooling
```

### **When You'll Need to Upgrade**:
```
Storage > 3GB: $19/month (Pro plan)
Need more performance: $19/month
Need multiple databases: $19/month
Need longer backups: $19/month
```

**For CampusDeal**: Free tier will work for **months** (maybe years!)

---

## ✅ WHAT YOU NEED FOR KOYEB

**Copy this to notepad** (replace with your actual values):

```
DATABASE_URL=postgresql://neondb_owner:YOUR_PASSWORD@ep-YOUR-PROJECT.eu-central-1.aws.neon.tech/neondb?sslmode=require
```

---

## 🔒 SECURITY NOTES

### **Connection is Secure**:
- ✅ SSL/TLS encryption (`sslmode=require`)
- ✅ Password authentication
- ✅ IP allowlist (optional)
- ✅ Connection pooling

### **Keep Private**:
- ❌ Never commit DATABASE_URL to GitHub
- ❌ Never share password publicly
- ✅ Only add to Koyeb environment variables

---

## 📊 MONITORING YOUR DATABASE

### **Check Usage**:
1. **Neon Dashboard** → Your project
2. **Click**: "Monitoring" tab
3. **See**:
   - Storage used (out of 3GB)
   - Active connections
   - Query performance
   - Backup status

### **Typical Usage for CampusDeal**:
```
1,000 users: ~50MB storage
10,000 users: ~500MB storage
100,000 users: ~2.5GB storage
```

**You have plenty of room!**

---

## 🚨 COMMON ISSUES

### Issue 1: "Connection failed"
**Solution**: 
- Check connection string is complete
- Ensure `sslmode=require` is included
- Verify password is correct (click eye icon to reveal)

### Issue 2: "Database not found"
**Solution**: 
- Default database name is `neondb`
- Don't change it unless you created a custom database

### Issue 3: "Too many connections"
**Solution**: 
- Free tier has connection limits
- Neon automatically handles connection pooling
- Usually not an issue for Django apps

### Issue 4: "SSL required"
**Solution**: 
- Always include `?sslmode=require` in connection string
- Neon requires SSL for security

---

## 📞 SUPPORT

**Neon Docs**: https://neon.tech/docs  
**Community**: https://discord.gg/92vNTzKDGp  
**Email**: support@neon.tech  
**Response Time**: 24-48 hours  

---

## ✅ CHECKLIST

- [ ] Account created with GitHub
- [ ] Project created (campusdeal)
- [ ] Region selected (Frankfurt)
- [ ] Connection string copied
- [ ] DATABASE_URL saved in notepad
- [ ] Password revealed and copied
- [ ] Ready for Koyeb deployment!

---

## 🎯 NEXT STEP

**Your DATABASE_URL is ready!**

```
DATABASE_URL=postgresql://neondb_owner:YOUR_PASSWORD@ep-YOUR-PROJECT.eu-central-1.aws.neon.tech/neondb?sslmode=require
```

**Now setup Koyeb** using the `KOYEB_SETUP.md` guide!

---

## 💡 PRO TIPS

### **Backup Strategy**:
- Neon automatically backs up every day
- Free tier keeps 7 days of backups
- You can restore to any point in time

### **Performance**:
- Neon auto-scales compute based on load
- Scales to zero when not used (saves resources)
- Wakes up instantly on first request

### **Monitoring**:
- Set up alerts for storage usage (when approaching 3GB)
- Monitor slow queries in dashboard
- Check connection count if app gets slow

---

**Status**: ✅ Neon.tech Ready!  
**Next**: Setup Koyeb hosting