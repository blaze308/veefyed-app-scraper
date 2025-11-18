# ☁️ OneDrive Setup Guide

Complete guide to configure OneDrive image uploads.

---

## 🎯 What is OneDrive Integration?

When enabled, the scraper will:
1. ✅ Download all product images
2. ✅ Upload them to your OneDrive
3. ✅ Generate shareable links
4. ✅ Replace image URLs with OneDrive links
5. ✅ Clean up temp files

**Result:** All product images are hosted on OneDrive with permanent shareable links!

---

## 🔧 Configuration Required

**OneDrive credentials must be set via environment variables or `.env` file.**

The scraper will look for these environment variables:
- `ONEDRIVE_TENANT_ID` - Azure AD tenant ID
- `ONEDRIVE_CLIENT_ID` - Azure app client ID  
- `ONEDRIVE_CLIENT_SECRET` - Azure app client secret (⚠️ Keep this secret!)
- `ONEDRIVE_USER_ID` - OneDrive user ID
- `ONEDRIVE_PARENT_FOLDER` - OneDrive folder ID for uploads

**Never commit secrets to git!** Use `.env` file (already in `.gitignore`).

---

## ✅ Testing OneDrive

### Quick Test

```bash
cd scraper
python modules/onedrive_uploader.py
```

**Expected output:**
```
✅ OneDrive authentication successful!
✅ Image uploaded successfully!
🔗 Share link: https://onedrive.live.com/...
```

**If you see errors:**
- ❌ Authentication failed → Credentials expired
- ❌ Upload failed → Folder permissions issue

---

## 🔄 Using Different Credentials

### Option 1: Environment Variables (Recommended)

Create a `.env` file:

```bash
# scraper/.env
ONEDRIVE_TENANT_ID=your-tenant-id
ONEDRIVE_CLIENT_ID=your-client-id
ONEDRIVE_CLIENT_SECRET=your-secret
ONEDRIVE_USER_ID=your-user-id
ONEDRIVE_PARENT_FOLDER=your-folder-id
```

The scraper will automatically use these!

### Option 2: Edit the File

Edit `modules/onedrive_uploader.py`:

```python
self.tenant_id = "YOUR_TENANT_ID"
self.client_id = "YOUR_CLIENT_ID"
self.client_secret = "YOUR_SECRET"
self.user_id = "YOUR_USER_ID"
self.parent_folder_id = "YOUR_FOLDER_ID"
```

---

## 🎛️ Optional: Disable OneDrive

### In the UI

Simply **uncheck** the box:
```
☁️ Upload images to OneDrive
```

Images will remain as original URLs (not uploaded).

### Permanently Disable

Edit `modules/scraper_engine.py`:

```python
def __init__(self, pattern_library_path: str = 'modules/pattern_library.json', 
             use_onedrive: bool = False):  # Changed to False
```

---

## 📊 OneDrive vs Original URLs

| Feature | OneDrive Upload | Original URLs |
|---------|----------------|---------------|
| **Speed** | Slower (upload time) | Faster |
| **Reliability** | High (permanent links) | Variable (may break) |
| **Storage** | Uses your OneDrive | No storage needed |
| **Links** | Shareable OneDrive links | Direct image URLs |
| **Best For** | Production use | Quick testing |

---

## 🔍 How It Works

### With OneDrive Enabled:

```
1. Scrape product → Find image URL
   https://cdn.shopify.com/image.jpg

2. Download image → Temp storage
   /tmp/scraper_uploads/category/abc123_image.jpg

3. Upload to OneDrive → Your folder
   OneDrive/03. Scraped_data/abc123_image.jpg

4. Get shareable link
   https://onedrive.live.com/embed?...

5. Update product data
   product_image_url: "https://onedrive.live.com/..."

6. Clean up temp file
   Delete /tmp/scraper_uploads/...
```

### With OneDrive Disabled:

```
1. Scrape product → Find image URL
   https://cdn.shopify.com/image.jpg

2. Use original URL
   product_image_url: "https://cdn.shopify.com/image.jpg"

Done! (Much faster)
```

---

## ⚡ Performance Impact

### Single Product:
- **Without OneDrive:** 10-15 seconds
- **With OneDrive:** 30-45 seconds
- **Difference:** +20-30 seconds for image upload

### Batch (50 products):
- **Without OneDrive:** 3-5 minutes
- **With OneDrive:** 10-15 minutes
- **Difference:** +7-10 minutes for all uploads

---

## 🐛 Troubleshooting

### "OneDrive authentication failed"

**Cause:** Credentials expired or invalid

**Solution:**
1. Check credentials in `modules/onedrive_uploader.py`
2. Verify they match your Azure app
3. Test with: `python modules/onedrive_uploader.py`

### "Upload failed"

**Possible causes:**
1. Folder doesn't exist
2. No write permissions
3. Network timeout

**Solutions:**
1. Check `parent_folder_id` is correct
2. Verify Azure app has Files.ReadWrite permission
3. Try uploading manually to test

### "Images not uploading"

**Check:**
1. Is the checkbox checked? ☁️ Upload images to OneDrive
2. Did OneDrive initialize? Check logs for "✅ OneDrive integration enabled"
3. Any errors in logs? `tail -f data/logs/scraper.log`

---

## 📝 Logs

Watch OneDrive activity:

```bash
tail -f data/logs/scraper.log | grep -i onedrive
```

**Success looks like:**
```
✅ OneDrive integration enabled
📤 Uploading main image to OneDrive...
✅ Main image uploaded
📤 Uploading 5 gallery images...
✅ Uploaded 5 images
```

**Failure looks like:**
```
❌ OneDrive authentication failed: Invalid credentials
⚠️ OneDrive not configured - images will not be uploaded
⚠️ Image upload failed: Timeout
```

---

## 🎯 Recommendations

### For Development/Testing:
```
☐ Uncheck "Upload images to OneDrive"
Reason: Faster, no upload delays
```

### For Production:
```
☑ Check "Upload images to OneDrive"
Reason: Permanent, reliable image hosting
```

### For Batch Scraping:
```
Consider: Disable for first run (faster)
Then: Re-run with upload enabled for final data
```

---

## 🔐 Security Notes

### Current Setup:
- ⚠️ Credentials are in the code
- ⚠️ Anyone with access can see them

### Better Setup:
1. Use environment variables (`.env` file)
2. Add `.env` to `.gitignore`
3. Never commit credentials to git

```bash
# Create .env
echo "ONEDRIVE_TENANT_ID=your-id" > .env
echo "ONEDRIVE_CLIENT_ID=your-id" >> .env
echo "ONEDRIVE_CLIENT_SECRET=your-secret" >> .env

# Add to .gitignore
echo ".env" >> .gitignore
```

---

## 📚 Azure App Setup (If Needed)

If you need to create new credentials:

### 1. Register App in Azure

1. Go to https://portal.azure.com
2. Navigate to "Azure Active Directory"
3. Click "App registrations" → "New registration"
4. Name: "Product Scraper"
5. Supported account types: "Single tenant"
6. Click "Register"

### 2. Get Credentials

**Tenant ID:**
- Overview page → "Directory (tenant) ID"

**Client ID:**
- Overview page → "Application (client) ID"

**Client Secret:**
- "Certificates & secrets" → "New client secret"
- Copy the VALUE (not ID)

### 3. Set Permissions

1. "API permissions" → "Add a permission"
2. "Microsoft Graph" → "Application permissions"
3. Add: `Files.ReadWrite.All`
4. Click "Grant admin consent"

### 4. Get User ID and Folder ID

Use Microsoft Graph Explorer or existing scripts.

---

## ✅ Quick Checklist

Before using OneDrive:
- [ ] Credentials are configured
- [ ] Test upload works (`python modules/onedrive_uploader.py`)
- [ ] Checkbox is checked in UI
- [ ] Logs show "✅ OneDrive integration enabled"

If not using OneDrive:
- [ ] Uncheck "☁️ Upload images to OneDrive"
- [ ] Scraping will be faster
- [ ] Original image URLs will be used

---

## 🎉 Summary

**OneDrive is OPTIONAL!**

✅ **Enable it** for: Production, permanent links, reliable hosting  
❌ **Disable it** for: Testing, speed, development  

**Current status:** Pre-configured with your existing credentials from `config.py`!

Just check/uncheck the box in the UI! ☁️

---

Need help? Check logs: `tail -f data/logs/scraper.log`

