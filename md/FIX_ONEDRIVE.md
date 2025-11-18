# 🔧 Fix OneDrive Configuration

## ✅ Current Status

**The app is working fine!** OneDrive is just disabled because the client secret has expired.

**You can still scrape products** - images will use their original URLs (faster, but not permanent).

---

## 🐛 The Problem

From the logs:
```
AADSTS7000222: The provided client secret keys for app '2c49e728-9879-4003-99d8-c7799bfb8909' are expired.
```

**Translation:** Your Azure client secret has expired and needs to be renewed.

---

## 🔄 How to Fix (2 Options)

### Option 1: Renew Client Secret (Recommended)

1. **Go to Azure Portal**
   - Visit: https://portal.azure.com
   - Navigate to: **Azure Active Directory** → **App registrations**
   - Find your app: `2c49e728-9879-4003-99d8-c7799bfb8909`

2. **Create New Client Secret**
   - Click **"Certificates & secrets"** in the left menu
   - Click **"+ New client secret"**
   - Description: "Product Scraper - 2025"
   - Expires: Choose duration (6 months, 1 year, or 2 years)
   - Click **"Add"**

3. **Copy the Secret Value**
   - ⚠️ **IMPORTANT:** Copy the **VALUE** (not the Secret ID)
   - ⚠️ **You can only see it once!** Save it immediately.

4. **Update Environment Variables**
   - Create or update `.env` file in `scraper/` folder:
     ```bash
     ONEDRIVE_CLIENT_SECRET=YOUR_NEW_SECRET_VALUE_HERE
     ```
   - Or set as environment variable:
     ```bash
     export ONEDRIVE_CLIENT_SECRET=YOUR_NEW_SECRET_VALUE_HERE
     ```

5. **Test It**
   ```bash
   cd scraper
   python modules/onedrive_uploader.py
   ```
   
   Should see: `OneDrive authentication successful!`

6. **Restart the App**
   - The app will automatically detect the new credentials
   - OneDrive uploads will now work!

---

### Option 2: Use Environment Variables (More Secure)

Instead of hardcoding the secret, use environment variables:

1. **Create `.env` file** in `scraper/` folder:
   ```bash
   ONEDRIVE_TENANT_ID=your-tenant-id-here
   ONEDRIVE_CLIENT_ID=your-client-id-here
   ONEDRIVE_CLIENT_SECRET=your-client-secret-here
   ONEDRIVE_USER_ID=your-user-id-here
   ONEDRIVE_PARENT_FOLDER=your-folder-id-here
   ```
   
   **Get these values from:**
   - Azure Portal → App registrations → Your app
   - Tenant ID: Directory (tenant) ID
   - Client ID: Application (client) ID
   - Client Secret: From "Certificates & secrets"
   - User ID & Folder ID: From your OneDrive setup

2. **Install python-dotenv** (if not already):
   ```bash
   pip install python-dotenv
   ```

3. **Update `onedrive_uploader.py`** to load from `.env`:
   ```python
   from dotenv import load_dotenv
   load_dotenv()  # Add this at the top
   ```

4. **Add `.env` to `.gitignore`** (so secrets aren't committed):
   ```bash
   echo ".env" >> .gitignore
   ```

---

## ✅ Verify It Works

After updating credentials:

```bash
cd scraper
python modules/onedrive_uploader.py
```

**Success looks like:**
```
OneDrive authentication successful!
Image uploaded successfully!
Share link: https://onedrive.live.com/...
```

**Failure looks like:**
```
OneDrive not configured
OneDrive authentication failed: 401 Unauthorized
```

---

## 🎯 Current Behavior (Without OneDrive)

**The app works perfectly without OneDrive!**

- ✅ Scraping works
- ✅ Data extraction works
- ✅ Images are included (original URLs)
- ❌ Images are NOT uploaded to OneDrive
- ❌ No shareable OneDrive links

**When you check "☁️ Upload images to OneDrive" in the UI:**
- The checkbox is checked, but OneDrive is disabled
- Images will use original URLs (faster!)
- No errors - it just skips uploads

---

## 📝 Summary

**To enable OneDrive:**
1. Get new client secret from Azure portal
2. Update `modules/onedrive_uploader.py` line 40
3. Restart the app
4. Done! ✅

**To continue without OneDrive:**
- Just uncheck the "☁️ Upload images to OneDrive" checkbox
- Everything works, just no uploads

---

## 🔗 Helpful Links

- **Azure Portal:** https://portal.azure.com
- **Create New Secret:** https://aka.ms/NewClientSecret
- **App Registration:** https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationMenuBlade/~/Overview

---

**The app is running fine - OneDrive is just optional!** 🚀

