# 🐛 Debugging Guide

## Fixed Issues

### 1. **JavaScript Error: `downloadBtn is not defined`** ✅ FIXED
**Problem:** Reference to old `downloadBtn` variable that was removed during UI updates.

**Location:** `displayBatchResults()` function in `app.js`

**Fix:** Changed to use `downloadCSVBtn` with null check:
```javascript
// Before (broken)
downloadBtn.textContent = `📥 Download All (${count} products)`;

// After (fixed)
if (downloadCSVBtn) {
    downloadCSVBtn.textContent = `📊 Download Data (${count} products)`;
}
```

### 2. **Poor Error Display** ✅ FIXED
**Problem:** Errors showed generic messages without details.

**Fix:** Enhanced error handling throughout:
```javascript
// Before
showError('Error checking job status');

// After
showError('Error checking job status', error.message || error.toString());
```

**New Features:**
- "View Error Details" button
- Full error text in dedicated viewer
- Scrollable error display
- Better error messages with HTTP status codes

---

## 🔧 How to Debug Issues

### 1. **Check Browser Console**
```
F12 → Console tab
Look for red error messages
```

### 2. **Check Server Logs**
```bash
cd scraper
tail -f data/logs/scraper.log
```

### 3. **Check Network Tab**
```
F12 → Network tab
Look for failed requests (red status codes)
Check response details
```

### 4. **Test API Endpoints Directly**
```bash
# Test scraping endpoint
curl -X POST http://localhost:8000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","use_ai":true}'

# Check job status
curl http://localhost:8000/api/status/JOB_ID
```

---

## 🚨 Common Issues & Solutions

### Issue: "Error checking job status"
**Cause:** Network error or server not responding

**Solutions:**
1. Check if server is running: `python app.py`
2. Check URL is correct: `http://localhost:8000`
3. Check firewall/antivirus blocking connections

### Issue: "Failed to start scraping"
**Cause:** Invalid URL or server error

**Solutions:**
1. Check URL format (must include `http://` or `https://`)
2. Check server logs for detailed error
3. Try a simpler URL first (e.g., `https://google.com`)

### Issue: "No data extracted"
**Cause:** Website blocking or incompatible structure

**Solutions:**
1. Try different websites
2. Check if website requires JavaScript (use batch mode)
3. Check if website blocks scrapers

### Issue: Batch mode not working
**Cause:** Platform not supported for batch scraping

**Solutions:**
1. Try single product first
2. Check if URL is a collection/category page
3. Some platforms only support single product scraping

---

## 📊 Testing Checklist

### ✅ Basic Functionality
- [ ] Server starts without errors
- [ ] UI loads at `http://localhost:8000`
- [ ] Can enter URL and click "Run Scraper"
- [ ] Status updates appear
- [ ] Results show after completion

### ✅ Single Product Scraping
- [ ] Test with Shopify product URL
- [ ] Test with generic e-commerce URL
- [ ] Quick preview appears
- [ ] Can download CSV
- [ ] Can download images

### ✅ Batch Scraping
- [ ] Check "Batch Mode"
- [ ] Test with collection URL
- [ ] Multiple products appear in preview
- [ ] Can download batch CSV
- [ ] Can download batch images

### ✅ Error Handling
- [ ] Invalid URL shows error
- [ ] Network errors show details
- [ ] Server errors show details
- [ ] Can view full error details

---

## 🔍 Debug URLs for Testing

### Working URLs (for testing):
```
# Shopify (single product)
https://shop.glossier.com/products/olivia-rodrigo-solar-paint

# Shopify (collection - batch)
https://shop.glossier.com/collections/makeup

# Generic e-commerce
https://www.sephora.com/product/rare-beauty-soft-pinch-liquid-blush-P455967

# Simple test
https://example.com
```

### URLs that might fail (for error testing):
```
# Invalid URL
not-a-url

# Non-existent domain
https://this-domain-does-not-exist-12345.com

# Blocked by robots.txt
https://amazon.com/dp/B08N5WRWNW
```

---

## 📝 Error Codes Reference

### HTTP Status Codes
- **200**: Success
- **400**: Bad request (invalid URL/parameters)
- **404**: Not found (job ID doesn't exist)
- **500**: Server error (check logs)
- **502/503**: Server unavailable

### Custom Error Messages
- **"Error checking job status"**: Network/connection issue
- **"Failed to start scraping"**: Invalid request or server error
- **"No data extracted"**: Scraping succeeded but found no product data
- **"Platform not supported"**: Website type not supported for batch scraping

---

## 🛠️ Advanced Debugging

### Enable Debug Mode
```bash
# Set environment variable
export DEBUG=true
python app.py
```

### Check Dependencies
```bash
pip list | grep -E "(requests|beautifulsoup4|selenium|fastapi)"
```

### Test Individual Components
```bash
# Test OneDrive (should show error about credentials)
python modules/onedrive_uploader.py

# Test platform detection
python modules/platform_detector.py

# Test Shopify scraper
python modules/shopify_scraper.py
```

### Check File Permissions
```bash
ls -la data/
ls -la data/logs/
ls -la data/outputs/
```

---

## 🎯 Performance Monitoring

### Monitor Resource Usage
```bash
# CPU and memory
top -p $(pgrep -f "python app.py")

# Disk space
df -h data/

# Log file size
du -h data/logs/scraper.log
```

### Monitor Network
```bash
# Check port is listening
netstat -tlnp | grep :8000

# Check connections
ss -tuln | grep :8000
```

---

## 📞 Getting Help

### Information to Provide
1. **Error message** (full text)
2. **Browser console logs** (F12 → Console)
3. **Server logs** (`tail -20 data/logs/scraper.log`)
4. **URL being scraped**
5. **Steps to reproduce**

### Log Files Location
```
data/logs/scraper.log    # Main application logs
data/logs/app.log        # FastAPI logs
```

### Useful Commands
```bash
# Show recent errors
grep -i error data/logs/scraper.log | tail -10

# Show recent activity
tail -50 data/logs/scraper.log

# Clear logs (if too large)
> data/logs/scraper.log
```

---

**All major issues have been fixed!** 🎉

The scraper should now work properly with better error reporting.
