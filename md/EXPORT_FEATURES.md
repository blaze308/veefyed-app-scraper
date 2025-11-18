# 📦 Export Features Guide

Complete guide to the new export and image download features.

---

## ✨ New Features Overview

### 1. **Multiple Export Formats**
- ✅ **CSV** (Primary format - easy to open in Excel)
- ✅ **JSON** (Technical format - preserves all data types)

### 2. **Image Downloads**
- ✅ Download all product images as ZIP file
- ✅ Organized by website name
- ✅ Automatic folder structure

### 3. **Folder Organization**
- ✅ Each scraping session creates a website-specific folder
- ✅ Format: `{website-name}_{timestamp}/`
- ✅ Contains: `data.csv` and `images/` folder

---

## 🎯 How It Works

### Scraping Workflow

```
1. Enter URL → Run Scraper
2. Scraper collects:
   - Product data (all fields)
   - Main image URL
   - Gallery images URLs (up to 10)
3. Data is ready for export
```

### Export Options

After scraping completes, you'll see:

```
📊 Export Data
  [📥 Download CSV]  [📥 Download JSON]

🖼️ Export Images
  [📥 Download Images]
```

---

## 📊 Export Data

### CSV Format (Recommended)

**Best for:**
- Opening in Excel/Google Sheets
- Quick data review
- Sharing with team
- Importing to databases

**Contains:**
- All product fields in columns
- One row per product
- UTF-8 encoded (supports special characters)

**Example:**
```
product_name,brand_name,category,product_image_url,product_images
"Vitamin C Serum","SkinCare Pro","Skincare","https://...jpg","['https://...jpg','https://...jpg']"
```

### JSON Format

**Best for:**
- Technical integrations
- API imports
- Preserving complex data types
- Developer use

**Contains:**
- Nested data structures
- Arrays for multiple images
- All metadata included

---

## 🖼️ Export Images

### What Gets Downloaded

When you click **"Download Images"**:

1. **Server Process:**
   - Creates folder: `{website-name}_{timestamp}/`
   - Downloads all product images:
     - Main image (`product_image_url`)
     - Gallery images (`product_images` array)
   - Saves with descriptive names:
     - `{product-name}_0_{hash}.jpg` (main)
     - `{product-name}_1_{hash}.jpg` (gallery 1)
     - `{product-name}_2_{hash}.jpg` (gallery 2)
     - etc.
   - Creates ZIP file

2. **You Receive:**
   - `{website-name}_{timestamp}_images.zip`

3. **ZIP Contains:**
   ```
   images/
   ├── vitamin_c_serum_0_abc123.jpg
   ├── vitamin_c_serum_1_def456.jpg
   ├── vitamin_c_serum_2_ghi789.jpg
   ├── retinol_cream_0_jkl012.jpg
   └── retinol_cream_1_mno345.jpg
   ```

---

## 📁 Folder Structure

### Single Product Scrape

```
bleakmakeup_20251117_143025/
├── images/
│   ├── vitamin_c_serum_0_abc123.jpg   (main image)
│   ├── vitamin_c_serum_1_def456.jpg   (gallery image 1)
│   └── vitamin_c_serum_2_ghi789.jpg   (gallery image 2)
└── bleakmakeup_20251117_143025_images.zip
```

### Batch Product Scrape

```
bleakmakeup_20251117_143025/
├── images/
│   ├── product1_0_abc123.jpg
│   ├── product1_1_def456.jpg
│   ├── product1_2_ghi789.jpg
│   ├── product2_0_jkl012.jpg
│   ├── product2_1_mno345.jpg
│   ├── product3_0_pqr678.jpg
│   └── ... (up to 10 images per product)
└── bleakmakeup_20251117_143025_images.zip
```

---

## 🎨 Example Use Cases

### Use Case 1: Product Catalog Import

**Goal:** Import products to your database

**Steps:**
1. Scrape products (batch mode)
2. Download CSV
3. Download Images ZIP
4. Import CSV to database
5. Extract images to your CDN/storage
6. Map image paths in database

### Use Case 2: Product Verification

**Goal:** Review products before adding to app

**Steps:**
1. Scrape product (single mode)
2. Download CSV → Open in Excel
3. Review data fields
4. Download Images → Visual verification
5. Upload verified data to production

### Use Case 3: Bulk Image Collection

**Goal:** Collect all product images from a website

**Steps:**
1. Use batch mode on collection page
2. Set max products (e.g., 100)
3. Wait for scraping to complete
4. Download Images ZIP
5. Extract ZIP → Get organized images

---

## 🔧 Technical Details

### Image Download Process

```python
# For each product:
1. Download main image → images/product_0_{hash}.jpg
2. Download gallery images → images/product_1_{hash}.jpg, etc.
3. Save with unique hash (prevents duplicates)
4. Sanitize filenames (remove special chars)
5. Limit to 10 images per product (performance)
```

### Website Name Extraction

The folder/file names are based on the domain:

```
https://www.bleakmakeup.com/products/serum
   → bleakmakeup

https://shop.glossier.com/collections/all
   → shop

https://theordinary.com/en-us/product/xyz
   → theordinary
```

### CSV Format Details

- **Encoding:** UTF-8 (supports all languages)
- **Delimiter:** Comma (`,`)
- **Quote Character:** Double quote (`"`)
- **Line Ending:** LF (`\n`) or CRLF (`\r\n`)
- **Arrays:** JSON string format (e.g., `"['url1','url2']"`)

---

## ⚡ Performance

### Speed Estimates

| Operation | Single Product | Batch (50 products) |
|-----------|---------------|---------------------|
| **Scrape Data** | 5-10 sec | 2-5 min |
| **Generate CSV** | <1 sec | <1 sec |
| **Download Images** | 10-30 sec | 5-15 min |
| **Create ZIP** | <1 sec | 5-10 sec |

**Note:** Image download time depends on:
- Image sizes
- Number of images
- Internet speed
- Server response times

---

## 🎯 Best Practices

### 1. **Choose CSV for Regular Use**
- Easier to work with
- Opens directly in Excel
- Great for sharing

### 2. **Use JSON for Technical Integration**
- Better for APIs
- Preserves data types
- Easier to parse programmatically

### 3. **Download Images Separately**
- Don't wait for images if you just need data
- Download images only when needed
- Images are large (takes more time)

### 4. **Batch Scraping Tips**
- Start with small batches (10-20 products)
- Test the scraper on a few products first
- Use reasonable max_products values

### 5. **Image Organization**
- Extract ZIP to a dedicated folder
- Rename images if needed (already have product names)
- Use the hash in filename to prevent duplicates

---

## 📝 Field Mapping

### CSV Columns (Key Fields)

| Column | Description | Example |
|--------|-------------|---------|
| `product_name` | Product name | "Vitamin C Serum" |
| `brand_name` | Brand/vendor | "The Ordinary" |
| `product_description` | Full description | "A powerful antioxidant..." |
| `product_id` | Product identifier | "SCRP-ABC123" |
| `product_image_url` | Main image URL | "https://...jpg" |
| `product_images` | All images (JSON array) | "['https://1.jpg','https://2.jpg']" |
| `category` | Product category | "Skincare" |
| `subcategory` | Product subcategory | "Serums" |
| `ingredients` | Full ingredients list | "Water, Ascorbic Acid..." |
| `package_size` | Size/volume | "30ml" |
| `barcode` | Product barcode | "8809123456789" |
| `rating` | Product rating | "4.5" |
| `review_count` | Number of reviews | "1250" |

**Note:** CSV includes ALL 45+ fields from the Product model!

---

## 🐛 Troubleshooting

### "Failed to download images"

**Possible causes:**
1. No images found in scraped data
2. Image URLs are broken/invalid
3. Network timeout

**Solutions:**
1. Check product has images
2. Try scraping again
3. Check image URLs in CSV first

### "ZIP file is empty"

**Cause:** No images were successfully downloaded

**Solutions:**
1. Verify product has `product_images` data
2. Check image URLs are valid (open in browser)
3. Try downloading fewer products

### "CSV not opening correctly in Excel"

**Cause:** Encoding or special characters

**Solutions:**
1. Use Excel's "Import Data" feature
2. Select "UTF-8" encoding
3. Choose comma as delimiter

---

## 🚀 Future Enhancements (Not Yet Implemented)

### OneDrive Upload (Task 6 - Pending)

**Planned features:**
- Upload CSV directly to OneDrive
- Upload images folder to OneDrive
- Organize by website name in OneDrive
- Get shareable OneDrive links

**Status:** Requires OneDrive credentials renewal (see `FIX_ONEDRIVE.md`)

---

## 📊 Summary

### ✅ What Works Now

1. **Data Export:**
   - CSV download (primary)
   - JSON download (optional)
   - Both formats ready immediately after scraping

2. **Image Export:**
   - Download all images as ZIP
   - Organized by product name
   - Automatic folder structure
   - Website-based naming

3. **UI:**
   - Separate buttons for data and images
   - Clear labeling
   - Loading states
   - Success notifications

### ⏳ What's Coming (Task 6)

1. **OneDrive Integration:**
   - Upload data files to OneDrive
   - Upload images to OneDrive
   - Folder organization on cloud
   - Shareable links

---

## 🎉 Usage Example

### Complete Workflow:

```
1. Open scraper UI: http://localhost:8000
2. Enter URL: https://bleakmakeup.com/collections/serums
3. Check "Batch Mode" ☑
4. Set Max Products: 20
5. Click "Run Scraper" 🚀
6. Wait for completion (2-3 min)
7. Results appear:
   ✅ 20 products scraped
   📊 Export Data
      [📥 Download CSV] ← Click for Excel-ready data
      [📥 Download JSON] ← Click for technical format
   🖼️ Export Images
      [📥 Download Images] ← Click for ZIP (takes 5-10 min)
8. Receive files:
   - product_data_abc123.csv
   - product_images_abc123.zip
9. Extract ZIP → folder with 200+ images (20 products × 10 images)
10. Import CSV to database
11. Upload images to CDN
12. Done! ✅
```

---

**Need help? Check the logs:** `tail -f data/logs/scraper.log`

**Questions? See:**
- `README.md` - General usage
- `FIX_ONEDRIVE.md` - OneDrive setup
- `BATCH_SCRAPING_GUIDE.md` - Batch scraping tips

