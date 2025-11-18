# 📦 Batch Scraping Guide

Complete guide to scraping multiple products at once!

---

## 🎯 What is Batch Scraping?

Instead of scraping products one-by-one, batch scraping lets you:

✅ **Scrape entire collection/category pages** (e.g., `/collections/skincare`)  
✅ **Process 50-200 products** in one go  
✅ **Save time** - no manual URL entry for each product  
✅ **Get CSV + JSON** output for easy import  

---

## 🚀 How to Use

### Step 1: Enable Batch Mode

1. Open http://localhost:8000
2. Enter a **collection/category URL** (not a single product)
3. ✅ Check the box: **"📦 Batch Mode: Scrape ALL products on this page"**
4. Set max products (default: 50, max: 200)
5. Click **"📦 Run Batch Scraper"**

### Step 2: Wait for Results

The scraper will:
1. 🔍 Detect the platform
2. 📦 Find all products on the page
3. 🎯 Scrape each product
4. ☁️ Upload images to OneDrive
5. 💾 Save as JSON + CSV

### Step 3: Download

- **JSON**: All products with full data
- **CSV**: Spreadsheet format for easy viewing

---

## 📊 Example URLs

### Shopify Collections (Best Support)

```
https://betocosmetics.com/collections/skin-care
https://store.myshopify.com/collections/all
```

### Category Pages

```
https://www.dermstore.com/c/skin-care/
https://example.com/category/moisturizers
```

---

## ⚡ Performance

| Platform | Speed per Product | Max Recommended |
|----------|------------------|-----------------|
| **Shopify** | 2-3 seconds | 200 products |
| **Static HTML** | 3-5 seconds | 100 products |
| **JavaScript** | 5-10 seconds | 50 products |

**Total Time Examples:**
- 50 Shopify products: ~3-5 minutes
- 50 JS products: ~10-15 minutes
- 200 Shopify products: ~15-20 minutes

---

## 📋 Output Format

### JSON Output

```json
{
  "products": [
    {
      "product_name": "Vitamin C Serum",
      "brand_name": "BeautyBrand",
      "product_image_url": "https://onedrive.live.com/...",
      ...
    },
    {
      "product_name": "Hyaluronic Acid",
      ...
    }
  ],
  "count": 50
}
```

### CSV Output

Spreadsheet with columns:
- product_name
- brand_name
- category
- product_image_url
- ingredients
- ... (all 40+ fields)

---

## 🔍 Field Extraction Report

For each product, you'll see:

```
📊 Field Extraction Report
├─ Success Rate: 85%
├─ Extracted: ✅ 34/40 fields
├─ Missing: ❌ 6 fields
└─ Critical missing: (none)
```

### Field Categories:

**Critical** (must have):
- product_name
- product_description
- product_image_url
- brand_name
- category

**Important** (should have):
- ingredients
- use_instructions
- package_size
- barcode
- product_images

**Optional** (nice to have):
- skin_type
- skin_concerns
- benefits
- warnings
- rating

---

## ❌ Error Handling

### If a Product Fails

The batch continues! Failed products are reported:

```
⚠️ Failed Products (3)
├─ Product A: Image upload failed
├─ Product B: No product name found
└─ Product C: Page timeout
```

### Common Failures:

1. **Image Upload Failed**
   - OneDrive connection issue
   - Image URL invalid
   - **Solution**: Check OneDrive credentials

2. **No Product Name Found**
   - Selector mismatch
   - Page structure changed
   - **Solution**: Site needs custom pattern

3. **Page Timeout**
   - Site too slow
   - Anti-bot measures
   - **Solution**: Reduce max_products

---

## 💡 Tips for Best Results

### 1. Start Small
```
First run: 10 products
If successful: 50 products
Then: 100-200 products
```

### 2. Use Shopify When Possible
Shopify sites are fastest because they use JSON API.

### 3. Monitor Progress
Watch the logs:
```bash
tail -f data/logs/scraper.log
```

### 4. Check Output
After scraping, verify:
- CSV file opens correctly
- Images are OneDrive links
- Critical fields are filled

---

## 🎯 Use Cases

### 1. Initial Product Import
```
Scenario: Adding 100 products to your app
Solution: Batch scrape entire collection
Time saved: Hours!
```

### 2. Competitor Analysis
```
Scenario: Analyze competitor's product range
Solution: Scrape their category pages
Output: CSV for analysis
```

### 3. Price Monitoring
```
Scenario: Track prices over time
Solution: Schedule batch scrapes
Output: Historical data
```

### 4. Data Enrichment
```
Scenario: Fill missing product data
Solution: Batch scrape, merge with existing
Output: Complete product database
```

---

## 🔧 Advanced Options

### API Usage

```bash
curl -X POST "http://localhost:8000/api/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://store.com/collections/all",
    "scrape_all_products": true,
    "max_products": 100
  }'
```

### Python Script

```python
import requests

response = requests.post('http://localhost:8000/api/scrape', json={
    'url': 'https://store.com/collections/skincare',
    'scrape_all_products': True,
    'max_products': 50
})

job_id = response.json()['job_id']

# Poll for completion
while True:
    status = requests.get(f'http://localhost:8000/api/status/{job_id}')
    data = status.json()
    
    if data['status'] == 'completed':
        print(f"Scraped {data['products_scraped']} products!")
        break
    
    time.sleep(5)
```

---

## 📊 Batch vs Single

| Feature | Single Product | Batch Mode |
|---------|---------------|------------|
| **Input** | Product URL | Collection URL |
| **Output** | 1 JSON file | JSON + CSV |
| **Time** | 30 seconds | 5-20 minutes |
| **Images** | All uploaded | All uploaded |
| **Use Case** | Quick test | Bulk import |

---

## ⚠️ Limitations

### Current Limits:
- **Max products**: 200 per batch
- **Timeout**: 30 minutes per job
- **Memory**: ~2GB for large batches

### Not Yet Supported:
- Pagination across multiple pages (coming soon!)
- Scheduled/recurring scrapes (coming soon!)
- Direct Firestore upload (coming soon!)

---

## 🐛 Troubleshooting

### "No products found"

**Possible causes:**
1. URL is a single product, not a collection
2. Platform not fully supported for batch
3. Page structure unusual

**Solutions:**
1. Verify URL is a category/collection page
2. Try single product scrape first
3. Check logs for details

### "Batch scraping not supported"

**Cause:** Platform doesn't have batch scraper yet

**Solution:** 
- Shopify: ✅ Fully supported
- Selenium: ✅ Supported
- Others: ⚠️ Falls back to single product

### Slow performance

**Causes:**
1. Too many products
2. Slow website
3. Image uploads taking time

**Solutions:**
1. Reduce max_products
2. Disable OneDrive temporarily
3. Run during off-peak hours

---

## 📈 Future Enhancements

Coming soon:
- ✨ Multi-page pagination
- ✨ Scheduled batch scrapes
- ✨ Direct Firestore upload
- ✨ Parallel processing
- ✨ Resume failed batches

---

## ✅ Quick Checklist

Before batch scraping:
- [ ] URL is a collection/category page
- [ ] Platform is Shopify or JS-supported
- [ ] OneDrive is configured
- [ ] Started with small test (10 products)
- [ ] Enough disk space for images
- [ ] Stable internet connection

After batch scraping:
- [ ] Check products_scraped count
- [ ] Review failed_products list
- [ ] Verify CSV opens correctly
- [ ] Spot-check random products
- [ ] Images are OneDrive links
- [ ] Critical fields are filled

---

## 🎉 Success!

You can now scrape **50-200 products in minutes** instead of hours of manual work!

**Next steps:**
1. Import CSV to your database
2. Or use JSON for Firestore upload
3. Schedule regular updates
4. Monitor for changes

---

Happy batch scraping! 📦✨

