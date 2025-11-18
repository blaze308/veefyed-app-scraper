# 🚀 Deploying Veefyed Scraper to Cantabo via SSH

This guide will walk you through deploying your scraper application to Cantabo server using SSH.

## 📋 Prerequisites

- SSH access to your Cantabo server
- Python 3.8+ installed on the server
- Basic knowledge of Linux commands
- Your scraper code ready to deploy

---

## 🔧 Step 1: Prepare Your Local Machine

### 1.1 Test Locally First
```bash
# Make sure everything works locally
cd scraper
python app.py
```

### 1.2 Create Deployment Package
```bash
# From your project root
cd scraper
tar -czf scraper-deploy.tar.gz \
    app.py \
    modules/ \
    templates/ \
    static/ \
    requirements.txt \
    config.py \
    *.md \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='data/logs/*' \
    --exclude='data/outputs/*'
```

---

## 📤 Step 2: Upload to Cantabo Server

### 2.1 Connect via SSH
```bash
# Replace with your actual Cantabo credentials
ssh username@cantabo-server-ip
# or
ssh username@your-domain.com
```

### 2.2 Create Application Directory
```bash
# Create directory for your app
mkdir -p ~/veefyed-scraper
cd ~/veefyed-scraper
```

### 2.3 Upload Files

**Option A: Using SCP (from your local machine)**
```bash
# From your local machine terminal
scp scraper-deploy.tar.gz username@cantabo-server-ip:~/veefyed-scraper/
```

**Option B: Using SFTP**
```bash
# Connect via SFTP
sftp username@cantabo-server-ip
cd veefyed-scraper
put scraper-deploy.tar.gz
exit
```

**Option C: Using Git (Recommended)**
```bash
# On Cantabo server
cd ~/veefyed-scraper
git clone https://github.com/your-username/your-repo.git .
# or if you have a private repo
git clone git@github.com:your-username/your-repo.git .
```

### 2.4 Extract Files
```bash
# On Cantabo server
cd ~/veefyed-scraper
tar -xzf scraper-deploy.tar.gz
# or if using git, files are already there
```

---

## 🐍 Step 3: Set Up Python Environment

### 3.1 Create Virtual Environment
```bash
cd ~/veefyed-scraper/scraper
python3 -m venv venv
source venv/bin/activate
```

### 3.2 Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.3 Install System Dependencies (if needed)
```bash
# For Selenium/Chrome
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver

# Or for headless Chrome
sudo apt-get install -y google-chrome-stable
```

---

## ⚙️ Step 4: Configure Environment

### 4.1 Create .env File
```bash
cd ~/veefyed-scraper/scraper
nano .env
```

Add your configuration:
```env
# OneDrive Configuration (if using)
ONEDRIVE_TENANT_ID=your-tenant-id
ONEDRIVE_CLIENT_ID=your-client-id
ONEDRIVE_CLIENT_SECRET=your-client-secret
ONEDRIVE_USER_ID=your-user-id
ONEDRIVE_PARENT_FOLDER=your-folder-id

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False
```

### 4.2 Create Required Directories
```bash
mkdir -p data/logs data/outputs
chmod -R 755 data
```

---

## 🚀 Step 5: Run the Application

### 5.1 Test Run
```bash
cd ~/veefyed-scraper/scraper
source venv/bin/activate
python app.py
```

### 5.2 Run in Background (Using nohup)
```bash
cd ~/veefyed-scraper/scraper
source venv/bin/activate
nohup python app.py > scraper.log 2>&1 &
```

### 5.3 Check if Running
```bash
# Check process
ps aux | grep python

# Check logs
tail -f scraper.log

# Check if port is listening
netstat -tulpn | grep 8000
# or
ss -tulpn | grep 8000
```

---

## 🔄 Step 6: Use Process Manager (Recommended)

### 6.1 Install Supervisor
```bash
sudo apt-get install supervisor
```

### 6.2 Create Supervisor Config
```bash
sudo nano /etc/supervisor/conf.d/veefyed-scraper.conf
```

Add this configuration:
```ini
[program:veefyed-scraper]
command=/home/username/veefyed-scraper/scraper/venv/bin/python /home/username/veefyed-scraper/scraper/app.py
directory=/home/username/veefyed-scraper/scraper
user=username
autostart=true
autorestart=true
stderr_logfile=/home/username/veefyed-scraper/scraper/data/logs/scraper_error.log
stdout_logfile=/home/username/veefyed-scraper/scraper/data/logs/scraper.log
environment=PATH="/home/username/veefyed-scraper/scraper/venv/bin"
```

### 6.3 Start with Supervisor
```bash
# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Start the service
sudo supervisorctl start veefyed-scraper

# Check status
sudo supervisorctl status veefyed-scraper

# View logs
sudo supervisorctl tail -f veefyed-scraper
```

---

## 🌐 Step 7: Set Up Reverse Proxy (Nginx)

### 7.1 Install Nginx
```bash
sudo apt-get install nginx
```

### 7.2 Create Nginx Config
```bash
sudo nano /etc/nginx/sites-available/veefyed-scraper
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or IP

    # Increase timeouts for long-running requests
    proxy_read_timeout 300s;
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Static files
    location /static {
        alias /home/username/veefyed-scraper/scraper/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 7.3 Enable Site
```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/veefyed-scraper /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### 7.4 Set Up SSL (Optional but Recommended)
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is set up automatically
```

---

## 🔒 Step 8: Firewall Configuration

### 8.1 Configure UFW (Ubuntu Firewall)
```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

---

## 📝 Step 9: Useful Commands

### Managing the Application

```bash
# View logs
tail -f ~/veefyed-scraper/scraper/data/logs/scraper.log

# Restart application (if using supervisor)
sudo supervisorctl restart veefyed-scraper

# Stop application
sudo supervisorctl stop veefyed-scraper

# Check application status
sudo supervisorctl status veefyed-scraper

# View real-time logs
sudo supervisorctl tail -f veefyed-scraper
```

### Updating the Application

```bash
# 1. Pull latest changes (if using git)
cd ~/veefyed-scraper
git pull origin main

# 2. Update dependencies
cd scraper
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 3. Restart application
sudo supervisorctl restart veefyed-scraper
```

### Monitoring

```bash
# Check if app is running
ps aux | grep python

# Check port usage
netstat -tulpn | grep 8000

# Check disk space
df -h

# Check memory usage
free -h

# Check application logs
tail -f ~/veefyed-scraper/scraper/data/logs/scraper.log
```

---

## 🐛 Troubleshooting

### Application Won't Start

1. **Check Python version:**
   ```bash
   python3 --version  # Should be 3.8+
   ```

2. **Check dependencies:**
   ```bash
   source venv/bin/activate
   pip list
   ```

3. **Check logs:**
   ```bash
   tail -f ~/veefyed-scraper/scraper/data/logs/scraper.log
   ```

4. **Check port availability:**
   ```bash
   netstat -tulpn | grep 8000
   # If port is in use, change PORT in .env or app.py
   ```

### 502 Bad Gateway Error

1. **Check if app is running:**
   ```bash
   sudo supervisorctl status veefyed-scraper
   ```

2. **Check Nginx error logs:**
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

3. **Restart services:**
   ```bash
   sudo supervisorctl restart veefyed-scraper
   sudo systemctl restart nginx
   ```

### Permission Issues

```bash
# Fix ownership
sudo chown -R username:username ~/veefyed-scraper

# Fix permissions
chmod -R 755 ~/veefyed-scraper/scraper
```

---

## 🔐 Security Best Practices

1. **Keep .env file secure:**
   ```bash
   chmod 600 .env
   ```

2. **Use strong passwords for SSH**

3. **Set up SSH key authentication:**
   ```bash
   # On local machine
   ssh-copy-id username@cantabo-server-ip
   ```

4. **Regular updates:**
   ```bash
   sudo apt-get update && sudo apt-get upgrade
   ```

5. **Monitor logs regularly:**
   ```bash
   tail -f ~/veefyed-scraper/scraper/data/logs/scraper.log
   ```

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Start app | `sudo supervisorctl start veefyed-scraper` |
| Stop app | `sudo supervisorctl stop veefyed-scraper` |
| Restart app | `sudo supervisorctl restart veefyed-scraper` |
| View logs | `tail -f ~/veefyed-scraper/scraper/data/logs/scraper.log` |
| Check status | `sudo supervisorctl status veefyed-scraper` |
| Restart Nginx | `sudo systemctl restart nginx` |
| Check Nginx status | `sudo systemctl status nginx` |

---

## ✅ Deployment Checklist

- [ ] Files uploaded to server
- [ ] Python virtual environment created
- [ ] Dependencies installed
- [ ] .env file configured
- [ ] Directories created (data/logs, data/outputs)
- [ ] Application tested locally on server
- [ ] Supervisor configured and running
- [ ] Nginx configured and running
- [ ] Firewall configured
- [ ] SSL certificate installed (optional)
- [ ] Application accessible via domain/IP
- [ ] Logs being written correctly

---

## 🎉 You're Done!

Your scraper should now be accessible at:
- **HTTP:** `http://your-domain.com` or `http://your-server-ip`
- **HTTPS:** `https://your-domain.com` (if SSL configured)

If you encounter any issues, check the logs first:
```bash
tail -f ~/veefyed-scraper/scraper/data/logs/scraper.log
```

Good luck! 🚀
