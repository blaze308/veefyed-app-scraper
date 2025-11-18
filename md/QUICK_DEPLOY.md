# ⚡ Quick Deploy Guide - Git + GitHub Actions

## 🎯 One-Time Setup (5 minutes)

### 1. On Cantabo Server:
```bash
# Clone repo
mkdir -p ~/veefyed-scraper && cd ~/veefyed-scraper
git clone https://github.com/your-username/your-repo.git .

# Setup Python
cd scraper
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create directories
mkdir -p data/logs data/outputs

# Create .env file
nano .env  # Add your configuration

# Generate SSH key for GitHub Actions
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions_deploy -N ""
cat ~/.ssh/github_actions_deploy.pub >> ~/.ssh/authorized_keys

# Copy private key (you'll need this for GitHub)
cat ~/.ssh/github_actions_deploy
```

### 2. On GitHub:
1. Go to: `https://github.com/your-username/your-repo/settings/secrets/actions`
2. Add secrets:
   - `CANTABO_HOST`: Your server IP/domain
   - `CANTABO_USER`: Your SSH username
   - `CANTABO_SSH_KEY`: Paste the private key from step 1
   - `CANTABO_PORT`: `22` (or your SSH port)

### 3. Setup Supervisor:
```bash
# On server
cd ~/veefyed-scraper/scraper
sed "s/USERNAME/$USER/g" supervisor.conf.example | sudo tee /etc/supervisor/conf.d/veefyed-scraper.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start veefyed-scraper
```

### 4. Setup Nginx:
```bash
# On server
cd ~/veefyed-scraper/scraper
sed "s/USERNAME/$USER/g" nginx.conf.example | sed "s/your-domain.com/YOUR-DOMAIN/g" | sudo tee /etc/nginx/sites-available/veefyed-scraper
sudo ln -s /etc/nginx/sites-available/veefyed-scraper /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🚀 Deploy Updates (Automatic!)

Just push to GitHub:
```bash
git add .
git commit -m "Update scraper"
git push origin main
```

GitHub Actions will automatically deploy! 🎉

---

## 📋 Useful Commands

```bash
# Check status
sudo supervisorctl status veefyed-scraper

# View logs
tail -f ~/veefyed-scraper/scraper/data/logs/scraper.log

# Restart manually
sudo supervisorctl restart veefyed-scraper

# Manual deploy
cd ~/veefyed-scraper && ./scraper/deploy.sh
```

---

## ✅ Done!

Your app is live at: `http://your-domain.com`

