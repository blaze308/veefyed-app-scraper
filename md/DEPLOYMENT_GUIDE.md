# 🚀 Deployment Guide - Swiss Army Knife Scraper

Complete guide to deploy your intelligent scraper to production.

---

## 📋 Prerequisites

- [ ] Python 3.7+ installed
- [ ] Chrome browser installed
- [ ] OneDrive credentials (from config.py)
- [ ] Server access (if deploying remotely)

---

## 🏠 Local Development

### 1. Install Dependencies

```bash
cd scraper
pip install -r requirements.txt
```

### 2. Test Components

**Test Platform Detector:**
```bash
python modules/platform_detector.py
```

**Test OneDrive:**
```bash
python modules/onedrive_uploader.py
```

**Test Shopify Scraper:**
```bash
python modules/shopify_scraper.py
```

### 3. Run Application

```bash
python app.py
```

Visit: http://localhost:8000

---

## 🖥️ Production Deployment

### Option 1: Linux Server (Recommended)

#### Step 1: Setup Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3 python3-pip python3-venv -y

# Install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f -y
```

#### Step 2: Deploy Code

```bash
# Create directory
sudo mkdir -p /opt/auto_scraper
cd /opt/auto_scraper

# Upload your scraper folder
# (Use SCP, Git, or file transfer)

# Set permissions
sudo chown -R $USER:$USER /opt/auto_scraper
```

#### Step 3: Create Virtual Environment

```bash
cd /opt/auto_scraper/scraper
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Step 4: Create Systemd Service

```bash
sudo nano /etc/systemd/system/autoscraper.service
```

**Add this content:**

```ini
[Unit]
Description=Auto-Scraper Swiss Army Knife
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/opt/auto_scraper/scraper
Environment="PATH=/opt/auto_scraper/scraper/venv/bin"
ExecStart=/opt/auto_scraper/scraper/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Step 5: Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable autoscraper
sudo systemctl start autoscraper
sudo systemctl status autoscraper
```

#### Step 6: Setup Nginx Reverse Proxy

```bash
sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/autoscraper
```

**Add this content:**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Increase timeout for long scraping jobs
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

**Enable and restart:**

```bash
sudo ln -s /etc/nginx/sites-available/autoscraper /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

### Option 2: Docker Deployment

#### Step 1: Create Dockerfile

```dockerfile
FROM python:3.11-slim

# Install Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Step 2: Create docker-compose.yml

```yaml
version: '3.8'

services:
  autoscraper:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ONEDRIVE_TENANT_ID=${ONEDRIVE_TENANT_ID}
      - ONEDRIVE_CLIENT_ID=${ONEDRIVE_CLIENT_ID}
      - ONEDRIVE_CLIENT_SECRET=${ONEDRIVE_CLIENT_SECRET}
      - ONEDRIVE_USER_ID=${ONEDRIVE_USER_ID}
      - ONEDRIVE_PARENT_FOLDER=${ONEDRIVE_PARENT_FOLDER}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    shm_size: '2gb'  # Selenium needs shared memory
```

#### Step 3: Deploy

```bash
docker-compose up -d
docker-compose logs -f
```

---

### Option 3: Cloud Deployment (AWS/Azure/GCP)

#### AWS EC2

1. Launch Ubuntu EC2 instance (t2.medium or larger)
2. Open port 8000 in security group
3. Follow Linux Server steps above

#### Azure App Service

```bash
az webapp up --name autoscraper --resource-group mygroup --runtime PYTHON:3.11
```

#### Google Cloud Run

```bash
gcloud run deploy autoscraper --source . --platform managed
```

---

## 🔒 Security Setup

### 1. Environment Variables

Never commit credentials! Use environment variables:

```bash
# Create .env file
cat > .env << EOF
ONEDRIVE_TENANT_ID=your-tenant-id
ONEDRIVE_CLIENT_ID=your-client-id
ONEDRIVE_CLIENT_SECRET=your-secret
ONEDRIVE_USER_ID=your-user-id
ONEDRIVE_PARENT_FOLDER=your-folder-id
EOF

# Make it readable only by owner
chmod 600 .env
```

### 2. Add Authentication (Optional)

For production, add API key authentication:

```python
# In app.py
from fastapi.security import APIKeyHeader

API_KEY = os.getenv("API_KEY", "change-me-in-production")
api_key_header = APIKeyHeader(name="X-API-Key")

@app.post("/api/scrape")
async def scrape_url(request: ScrapeRequest, 
                     api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    # ... rest of code
```

### 3. Rate Limiting

```bash
pip install slowapi
```

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/scrape")
@limiter.limit("10/minute")
async def scrape_url(request: Request, ...):
    ...
```

---

## 📊 Monitoring

### 1. Logs

```bash
# View logs
tail -f data/logs/scraper.log

# Rotate logs
sudo apt install logrotate
```

Create `/etc/logrotate.d/autoscraper`:

```
/opt/auto_scraper/scraper/data/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### 2. Health Checks

```bash
# Check if service is running
curl http://localhost:8000/health

# Monitor with systemd
sudo systemctl status autoscraper
```

### 3. Performance Monitoring

Add to `app.py`:

```python
import time
from fastapi import Request

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.2f}s")
    return response
```

---

## 🔄 Updates & Maintenance

### Update Code

```bash
cd /opt/auto_scraper/scraper
git pull  # or upload new files
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart autoscraper
```

### Clean Old Data

```bash
# Clean old outputs (keep last 7 days)
find data/outputs -name "*.json" -mtime +7 -delete

# Clean temp files
rm -rf /tmp/scraper_uploads/*
```

### Backup

```bash
# Backup configuration
tar -czf backup-$(date +%Y%m%d).tar.gz scraper/

# Backup to S3 (optional)
aws s3 cp backup-$(date +%Y%m%d).tar.gz s3://my-bucket/backups/
```

---

## 🐛 Troubleshooting

### Service won't start

```bash
# Check logs
sudo journalctl -u autoscraper -n 50

# Check permissions
ls -la /opt/auto_scraper/scraper

# Test manually
cd /opt/auto_scraper/scraper
source venv/bin/activate
python app.py
```

### Chrome/Selenium issues

```bash
# Check Chrome version
google-chrome --version

# Update ChromeDriver
pip install --upgrade undetected-chromedriver

# Test Selenium
python modules/selenium_scraper.py
```

### Port already in use

```bash
# Find what's using port 8000
sudo lsof -i :8000

# Kill the process
sudo kill -9 PID
```

---

## ✅ Post-Deployment Checklist

- [ ] Service is running (`sudo systemctl status autoscraper`)
- [ ] Web UI is accessible (http://your-server:8000)
- [ ] API docs work (http://your-server:8000/docs)
- [ ] Test scrape completes successfully
- [ ] OneDrive upload works
- [ ] Logs are being written
- [ ] Nginx proxy works (if using)
- [ ] Firewall/security group allows traffic
- [ ] SSL certificate installed (if using HTTPS)
- [ ] Monitoring is active
- [ ] Backups are scheduled

---

## 📞 Support

**Check Logs:**
```bash
sudo journalctl -u autoscraper -f
tail -f data/logs/scraper.log
```

**Test Components:**
```bash
python modules/platform_detector.py
python modules/onedrive_uploader.py
```

**API Health:**
```bash
curl http://localhost:8000/health
```

---

🎉 **Your intelligent scraper is now deployed!**

