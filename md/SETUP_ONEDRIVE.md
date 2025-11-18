# ⚡ Quick OneDrive Setup

## 🎯 3-Step Setup

### Step 1: Create `.env` File

Create `scraper/.env` file with your OneDrive credentials:

```bash
ONEDRIVE_TENANT_ID=your-tenant-id
ONEDRIVE_CLIENT_ID=your-client-id
ONEDRIVE_CLIENT_SECRET=your-client-secret
ONEDRIVE_USER_ID=your-user-id
ONEDRIVE_PARENT_FOLDER=your-folder-id
```

### Step 2: Get Credentials from Azure Portal

1. Go to: https://portal.azure.com
2. Navigate: **Azure Active Directory** → **App registrations**
3. Find your app (or create new one)
4. Copy values:
   - **Tenant ID**: From "Overview" → "Directory (tenant) ID"
   - **Client ID**: From "Overview" → "Application (client) ID"
   - **Client Secret**: Create new in "Certificates & secrets"
   - **User ID & Folder ID**: From your existing OneDrive setup

### Step 3: Test

```bash
cd scraper
python modules/onedrive_uploader.py
```

Should see: `OneDrive authentication successful!`

---

## ✅ Done!

The `.env` file is already in `.gitignore`, so your secrets won't be committed to git.

**The app will automatically use these credentials when you enable OneDrive uploads!**

---

## 🔒 Security Note

- ✅ `.env` is in `.gitignore` (won't be committed)
- ✅ Never commit secrets to git
- ✅ Use `.env.example` as a template (no real values)

