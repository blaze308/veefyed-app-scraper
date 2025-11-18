# 🚀 Quick Start Guide

Get the Auto-Scraper running in 3 minutes!

## Step 1: Install Dependencies

```bash
cd scraper
pip install -r requirements.txt
```

## Step 2: Run the Application

```bash
python app.py
```

Or:

```bash
uvicorn app:app --reload
```

## Step 3: Open the UI

Open your browser to:
```
http://localhost:8000
```

## Step 4: Scrape Your First Product

1. Enter a product URL (try an Amazon or skincare product page)
2. Click "Run Scraper"
3. Wait for results
4. Download the JSON file

## 🎯 Test URLs

Try these example URLs:

**Amazon:**
```
https://www.amazon.com/dp/B08XYZ123
```

**General Skincare:**
```
https://www.beautycounter.com/products/serum
```

**Shopify Store:**
```
https://yourstore.myshopify.com/products/moisturizer
```

## 📖 Next Steps

- Read the full [README.md](README.md)
- Check API docs at http://localhost:8000/docs
- Customize patterns in `modules/pattern_library.json`
- Add historical scripts to `data/scripts_raw/` for better AI

## ❓ Troubleshooting

**"Module not found" error:**
```bash
pip install -r requirements.txt
```

**Port 8000 already in use:**
```bash
uvicorn app:app --port 8001
```

**No data extracted:**
- Try a different URL
- Check if it's a valid product page
- Try manual pattern selection

## 🎨 Features to Try

1. ✅ Auto-detect pattern
2. 🧠 Analyze URL before scraping
3. 📥 Download results as JSON
4. 👁️ View extracted data
5. 📊 Check recent jobs

---

**That's it! You're ready to scrape!** 🎉

