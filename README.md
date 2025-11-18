# 🔍 Auto-Scraper AI Tool

Intelligent web scraper for extracting product data from e-commerce websites. Built specifically for the Veefyed skincare product verification app.

## 📋 Overview

This tool automatically generates scraping logic based on URL patterns and AI-assisted detection. It extracts structured product data that matches the Veefyed mobile app's Product model, including:

- Product details (name, description, ID)
- Brand and category information
- Images and pricing
- Ingredients and skincare-specific data
- Ratings and reviews
- And 40+ more fields

## 🎯 Features

- **AI-Assisted Pattern Detection**: Automatically identifies the best scraping pattern
- **Multiple Pattern Support**: Pre-configured patterns for Amazon, Shopify, and generic e-commerce sites
- **Web UI**: Simple, beautiful interface for running scrapes
- **RESTful API**: Full FastAPI backend with automatic documentation
- **Background Processing**: Non-blocking scraping with job tracking
- **Export Options**: Download results as JSON or CSV
- **Pattern Library**: Extensible pattern system for different website types

## 🏗️ Project Structure

```
scraper/
├── app.py                      # Main FastAPI application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── data/
│   ├── scripts_raw/           # Historical scraping scripts (for training)
│   ├── outputs/               # Scraped data output files
│   └── logs/                  # Application logs
├── modules/
│   ├── pattern_library.json   # Scraping pattern definitions
│   ├── scraper_engine.py      # Core scraping engine
│   ├── url_matcher.py         # URL to pattern matcher
│   └── ai_pattern_detector.py # AI-based pattern detection
├── templates/
│   └── index.html             # Web UI template
└── static/
    ├── css/
    │   └── style.css          # UI styles
    └── js/
        └── app.js             # Frontend JavaScript
```

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. **Navigate to the scraper directory:**
   ```bash
   cd scraper
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment (optional):**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```
   
   Or using uvicorn:
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Open the web interface:**
   - Navigate to: http://localhost:8000
   - API docs: http://localhost:8000/docs

## 💻 Usage

### Web Interface

1. Open http://localhost:8000
2. Enter a product URL (e.g., https://example.com/product/vitamin-c-serum)
3. (Optional) Select a specific pattern or let AI auto-detect
4. Click "Run Scraper"
5. Wait for results and download JSON

### API Usage

**Scrape a URL:**

```bash
curl -X POST "http://localhost:8000/api/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/product/serum",
    "use_ai": true
  }'
```

**Check job status:**

```bash
curl "http://localhost:8000/api/status/{job_id}"
```

**Download results:**

```bash
curl "http://localhost:8000/api/download/{job_id}" -o product.json
```

**Analyze URL without scraping:**

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/product/serum"}'
```

## 📊 Product Data Fields

The scraper extracts data matching the Veefyed Product model:

**Basic Fields:**
- `product_name`, `product_description`, `product_id`
- `brand_name`, `category`, `subcategory`
- `package_size`, `barcode`, `barcode_type`

**Images:**
- `product_image_url` (main image)
- `product_images` (array of additional images)

**Skincare-Specific:**
- `skin_type`, `skin_concerns`, `benefits`
- `key_ingredients` (1-5 fields)
- `ingredients` (full list)
- `use_instructions`, `warnings`, `precautions`

**Metadata:**
- `rating`, `review_count`
- `stock_quantity`, `is_active`
- `country_of_origin`
- `verification_status`, `verification_date`

## 🎨 Available Patterns

1. **ecommerce_skincare** - General skincare e-commerce sites
2. **amazon_products** - Amazon product pages
3. **shopify_store** - Shopify-based stores
4. **generic_ecommerce** - Fallback for any e-commerce site

## 🧠 AI Pattern Detection

The AI detector analyzes:
- URL structure and domain
- HTML content patterns (if available)
- Common selector patterns
- Historical scraping data

Confidence scoring helps determine reliability.

## 📝 Adding Custom Patterns

Edit `modules/pattern_library.json`:

```json
{
  "my_custom_pattern": {
    "description": "Pattern for MyStore.com",
    "selectors": {
      "product_name": ["h1.product-title", ".product-name"],
      "price": [".product-price", ".price"],
      "product_image_url": ["img.main-image"]
    },
    "libraries": ["requests", "beautifulsoup4"],
    "requires_js": false
  }
}
```

## 🔧 Configuration

Edit `config.py` or set environment variables:

```python
# Scraping
REQUEST_TIMEOUT = 30          # Request timeout in seconds
MAX_RETRIES = 3              # Retry failed requests
RATE_LIMIT = 10              # Requests per minute

# AI
AI_ENABLED = True            # Enable AI pattern detection
AI_CONFIDENCE_THRESHOLD = 0.5 # Minimum confidence score

# Jobs
JOB_RETENTION_HOURS = 24     # Keep job data for 24 hours
MAX_CONCURRENT_JOBS = 5      # Max simultaneous scraping jobs
```

## 📁 Output Files

Scraped data is saved to `data/outputs/` as:
- **JSON**: `product_YYYYMMDD_HHMMSS_jobid.json`
- **CSV**: Available via API or manual export

## 🐛 Troubleshooting

**Scraping fails:**
- Check if URL is a valid product page
- Try a different pattern manually
- Check logs in `data/logs/app.log`

**No data extracted:**
- Website may have changed structure
- Try analyzing URL first to check confidence
- Website may require JavaScript rendering

**Dependencies issues:**
- Make sure Python 3.7+ is installed
- Run `pip install -r requirements.txt` again
- Use a virtual environment

## 📚 API Documentation

Full API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔒 Security Considerations

- Rate limiting prevents abuse
- Blocked domains list for social media sites
- Input validation on all URLs
- CORS configured for local development
- No credentials stored in code

## 📈 5-Day Implementation Plan

This tool follows the structured 5-day plan:

- **Day 1**: Data collection (scripts_raw folder)
- **Day 2**: Script analysis
- **Day 3**: Pattern library creation ✓
- **Day 4**: Base scraper engine ✓
- **Day 5**: AI integration + Web UI ✓

## 🤝 Contributing

To add training data for better AI detection:

1. Place historical scraping scripts in `data/scripts_raw/`
2. Run analysis to extract patterns
3. Update `ai_training_data.json`

## 📄 License

Built for Veefyed - Internal Use Only

## 🆘 Support

For issues or questions:
- Check logs in `data/logs/`
- Review API documentation at `/docs`
- Inspect network requests in browser DevTools

## 🎯 Next Steps

1. **Add historical scripts** to `data/scripts_raw/` for better AI
2. **Customize patterns** in `pattern_library.json` for your sites
3. **Configure rate limits** based on your needs
4. **Set up monitoring** for production use
5. **Export to Firestore** for direct mobile app integration

---

Built with ❤️ for Veefyed Skincare Product Verification

