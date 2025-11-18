# 🚀 Git-Based Deployment to Cantabo with GitHub Actions

This guide shows you how to deploy your scraper using Git and GitHub Actions for automatic deployments.

## 📋 Prerequisites

- GitHub repository (public or private)
- SSH access to Cantabo server
- Python 3.8+ on server
- Basic Git knowledge

---

## 🔧 Step 1: Initial Server Setup (One-Time)

### 1.1 Connect to Cantabo Server
```bash
ssh username@cantabo-server-ip
```

### 1.2 Clone Your Repository
```bash
# Create application directory
mkdir -p ~/veefyed-scraper
cd ~/veefyed-scraper

# Clone your repository
git clone https://github.com/your-username/your-repo.git .
# OR for private repo:
git clone git@github.com:your-username/your-repo.git .
```

### 1.3 Set Up Python Environment
```bash
cd scraper
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 1.4 Create Required Directories
```bash
mkdir -p data/logs data/outputs
chmod -R 755 data
```

### 1.5 Create .env File
```bash
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

### 1.6 Make Deploy Script Executable
```bash
chmod +x deploy.sh
```

---

## 🔐 Step 2: Set Up SSH Key for GitHub Actions

### 2.1 Generate SSH Key on Server (if not exists)
```bash
# On Cantabo server
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions_deploy
```

### 2.2 Add Public Key to Server's Authorized Keys
```bash
# On Cantabo server
cat ~/.ssh/github_actions_deploy.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 2.3 Copy Private Key (for GitHub Secrets)
```bash
# On Cantabo server
cat ~/.ssh/github_actions_deploy
# Copy the entire output (starts with -----BEGIN OPENSSH PRIVATE KEY-----)
```

---

## 🔑 Step 3: Configure GitHub Secrets

### 3.1 Go to GitHub Repository Settings
1. Navigate to: `https://github.com/your-username/your-repo/settings/secrets/actions`
2. Click **"New repository secret"**

### 3.2 Add These Secrets:

| Secret Name | Value | Description |
|------------|-------|-------------|
| `CANTABO_HOST` | `your-server-ip` or `your-domain.com` | Server IP or domain |
| `CANTABO_USER` | `your-username` | SSH username |
| `CANTABO_SSH_KEY` | `-----BEGIN OPENSSH PRIVATE KEY-----...` | Private SSH key (entire content) |
| `CANTABO_PORT` | `22` | SSH port (default: 22) |

**Important:** 
- For `CANTABO_SSH_KEY`, paste the **entire private key** including:
  - `-----BEGIN OPENSSH PRIVATE KEY-----`
  - All the key content
  - `-----END OPENSSH PRIVATE KEY-----`

---

## ⚙️ Step 4: Set Up Supervisor (Process Manager)

### 4.1 Install Supervisor
```bash
sudo apt-get update
sudo apt-get install supervisor -y
```

### 4.2 Create Supervisor Config
```bash
# Copy the example config
cd ~/veefyed-scraper/scraper
cp supervisor.conf.example /tmp/supervisor_config_temp

# Edit with your username
sed "s/USERNAME/$USER/g" /tmp/supervisor_config_temp | sudo tee /etc/supervisor/conf.d/veefyed-scraper.conf

# Or manually edit:
sudo nano /etc/supervisor/conf.d/veefyed-scraper.conf
```

**Update these values:**
- Replace `USERNAME` with your actual username
- Update paths if different

### 4.3 Start Supervisor Service
```bash
# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Start the service
sudo supervisorctl start veefyed-scraper

# Check status
sudo supervisorctl status veefyed-scraper
```

---

## 🌐 Step 5: Set Up Nginx (Reverse Proxy)

### 5.1 Install Nginx
```bash
sudo apt-get install nginx -y
```

### 5.2 Create Nginx Config
```bash
# Copy the example config
cd ~/veefyed-scraper/scraper
cp nginx.conf.example /tmp/nginx_config_temp

# Edit with your username and domain
sed "s/USERNAME/$USER/g" /tmp/nginx_config_temp | sed "s/your-domain.com/your-actual-domain.com/g" | sudo tee /etc/nginx/sites-available/veefyed-scraper

# Or manually edit:
sudo nano /etc/nginx/sites-available/veefyed-scraper
```

**Update:**
- Replace `USERNAME` with your username
- Replace `your-domain.com` with your actual domain or IP

### 5.3 Enable Site
```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/veefyed-scraper /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### 5.4 Set Up SSL (Optional but Recommended)
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is set up automatically
```

---

## 🔥 Step 6: Configure Firewall

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

## 🚀 Step 7: Test Deployment

### 7.1 Test Locally on Server
```bash
cd ~/veefyed-scraper/scraper
source venv/bin/activate
python app.py
# Should see: "Starting Auto-Scraper AI Tool"
# Press Ctrl+C to stop
```

### 7.2 Test via Supervisor
```bash
sudo supervisorctl status veefyed-scraper
# Should show: veefyed-scraper RUNNING

# Check logs
tail -f ~/veefyed-scraper/scraper/data/logs/scraper.log
```

### 7.3 Test via Browser
- Visit: `http://your-domain.com` or `http://your-server-ip`
- Should see the scraper UI

---

## 🔄 Step 8: Automatic Deployments with GitHub Actions

### 8.1 How It Works

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Update scraper"
   git push origin main
   ```

2. **GitHub Actions Automatically:**
   - Checks out your code
   - Installs dependencies
   - Connects to Cantabo server via SSH
   - Pulls latest changes
   - Updates dependencies
   - Restarts the application
   - Verifies deployment

### 8.2 View Deployment Status

1. Go to: `https://github.com/your-username/your-repo/actions`
2. Click on the latest workflow run
3. See real-time deployment progress

### 8.3 Manual Deployment Trigger

You can also trigger deployment manually:
1. Go to: `https://github.com/your-username/your-repo/actions`
2. Click **"Deploy to Cantabo Server"**
3. Click **"Run workflow"**

---

## 📝 Step 9: Manual Deployment (Alternative)

If you need to deploy manually without GitHub Actions:

```bash
# SSH into server
ssh username@cantabo-server

# Run deployment script
cd ~/veefyed-scraper
./scraper/deploy.sh
```

Or manually:
```bash
cd ~/veefyed-scraper
git pull origin main
cd scraper
source venv/bin/activate
pip install -r requirements.txt
sudo supervisorctl restart veefyed-scraper
```

---

## 🐛 Troubleshooting

### GitHub Actions Deployment Fails

1. **Check SSH Connection:**
   ```bash
   # Test SSH key manually
   ssh -i ~/.ssh/github_actions_deploy username@cantabo-server
   ```

2. **Verify Secrets:**
   - Go to GitHub repo → Settings → Secrets
   - Ensure all secrets are set correctly
   - Check for extra spaces or newlines

3. **Check GitHub Actions Logs:**
   - Go to Actions tab in GitHub
   - Click on failed workflow
   - Check error messages

### Application Won't Start

1. **Check Supervisor Status:**
   ```bash
   sudo supervisorctl status veefyed-scraper
   ```

2. **Check Logs:**
   ```bash
   tail -f ~/veefyed-scraper/scraper/data/logs/scraper.log
   tail -f ~/veefyed-scraper/scraper/data/logs/scraper_error.log
   ```

3. **Check Port:**
   ```bash
   netstat -tulpn | grep 8000
   # If port is in use, change PORT in .env
   ```

### Nginx 502 Bad Gateway

1. **Check if app is running:**
   ```bash
   sudo supervisorctl status veefyed-scraper
   curl http://localhost:8000/health
   ```

2. **Check Nginx logs:**
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

3. **Restart services:**
   ```bash
   sudo supervisorctl restart veefyed-scraper
   sudo systemctl restart nginx
   ```

---

## 📊 Monitoring & Maintenance

### View Application Logs
```bash
tail -f ~/veefyed-scraper/scraper/data/logs/scraper.log
```

### Check Application Status
```bash
sudo supervisorctl status veefyed-scraper
```

### Restart Application
```bash
sudo supervisorctl restart veefyed-scraper
```

### Check Nginx Status
```bash
sudo systemctl status nginx
```

### View System Resources
```bash
# CPU and Memory
htop

# Disk Space
df -h

# Network
netstat -tulpn
```

---

## 🔒 Security Best Practices

1. **Keep .env Secure:**
   ```bash
   chmod 600 ~/veefyed-scraper/scraper/.env
   ```

2. **Use SSH Keys (not passwords):**
   ```bash
   # Already set up for GitHub Actions
   ```

3. **Regular Updates:**
   ```bash
   sudo apt-get update && sudo apt-get upgrade
   ```

4. **Monitor Logs:**
   ```bash
   tail -f ~/veefyed-scraper/scraper/data/logs/scraper.log
   ```

5. **Backup Important Data:**
   ```bash
   # Backup .env file
   cp ~/veefyed-scraper/scraper/.env ~/backup/.env.$(date +%Y%m%d)
   ```

---

## ✅ Deployment Checklist

- [ ] Repository cloned on server
- [ ] Python virtual environment created
- [ ] Dependencies installed
- [ ] .env file configured
- [ ] Directories created (data/logs, data/outputs)
- [ ] SSH key generated and added to GitHub Secrets
- [ ] Supervisor configured and running
- [ ] Nginx configured and running
- [ ] Firewall configured
- [ ] SSL certificate installed (optional)
- [ ] GitHub Actions workflow tested
- [ ] Application accessible via domain/IP
- [ ] Automatic deployment working

---

## 🎉 You're All Set!

### How to Deploy Updates:

**Option 1: Automatic (Recommended)**
```bash
# On your local machine
git add .
git commit -m "Your changes"
git push origin main
# GitHub Actions will automatically deploy!
```

**Option 2: Manual**
```bash
# SSH into server
ssh username@cantabo-server
cd ~/veefyed-scraper
./scraper/deploy.sh
```

### Access Your Application:
- **HTTP:** `http://your-domain.com` or `http://your-server-ip`
- **HTTPS:** `https://your-domain.com` (if SSL configured)

### Monitor Deployments:
- GitHub Actions: `https://github.com/your-username/your-repo/actions`
- Server Logs: `tail -f ~/veefyed-scraper/scraper/data/logs/scraper.log`

Happy deploying! 🚀

