# 🪟 Windows Installation Guide

Quick guide to fix common Windows installation issues.

## ✅ Quick Fix (Recommended)

Run this command to install without pandas (pandas is optional):

```bash
pip install fastapi uvicorn[standard] requests beautifulsoup4 lxml jinja2 pydantic python-dotenv
```

This installs everything you need for the scraper to work!

## 🚀 Then Start the App

```bash
python app.py
```

Open: http://localhost:8000

---

## 📋 Alternative: Full Installation with Requirements

If you want to use the requirements.txt file:

```bash
pip install -r requirements.txt
```

This should now work without pandas build issues.

---

## ❓ If You Still Get Errors

### Issue: `lxml` won't install

**Solution:** Install pre-built wheel
```bash
pip install lxml --only-binary :all:
```

### Issue: Need pandas for CSV export

**Option 1:** Install pre-built pandas
```bash
pip install pandas --only-binary :all:
```

**Option 2:** Install Visual Studio Build Tools
1. Download: https://visualstudio.microsoft.com/downloads/
2. Install "Desktop development with C++"
3. Then run: `pip install pandas`

### Issue: Python not found

Make sure Python 3.7+ is installed:
```bash
python --version
```

If not, download from: https://www.python.org/downloads/

---

## 🎯 Minimal Installation (Just to Test)

Install only what's absolutely required:

```bash
pip install fastapi uvicorn requests beautifulsoup4 lxml
```

Then run:
```bash
uvicorn app:app --reload
```

---

## ✅ Verify Installation

Test if everything works:

```bash
python -c "import fastapi, uvicorn, requests, bs4, lxml; print('All dependencies installed!')"
```

If you see "All dependencies installed!" - you're good to go! 🎉

---

## 🆘 Still Having Issues?

### Try using a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn requests beautifulsoup4 lxml jinja2 pydantic python-dotenv

# Run app
python app.py
```

### Use conda (if you have Anaconda):

```bash
conda create -n scraper python=3.11
conda activate scraper
pip install fastapi uvicorn requests beautifulsoup4 lxml jinja2 pydantic python-dotenv
python app.py
```

---

## 📝 What Each Package Does

- **fastapi** - Web framework for the API
- **uvicorn** - Web server to run FastAPI
- **requests** - Makes HTTP requests to websites
- **beautifulsoup4** - Parses HTML to extract data
- **lxml** - Fast HTML parser (used by beautifulsoup4)
- **jinja2** - Template engine for the web UI
- **pydantic** - Data validation
- **python-dotenv** - Environment variables (optional)
- **pandas** - CSV export (OPTIONAL - not required)

---

## 🎉 Success!

Once installed, start the scraper:

```bash
python app.py
```

Then open your browser to: **http://localhost:8000**

You should see the Auto-Scraper UI! 🚀

