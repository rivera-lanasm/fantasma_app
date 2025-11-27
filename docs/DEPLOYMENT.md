# Deployment Guide: fantasma.mriveralanas.com

## Prerequisites
- AWS account with EC2 access
- Domain: mriveralanas.com (DNS access)
- Local: Project ready to deploy

---

## Phase 1: EC2 Setup

### 1.1 Launch EC2 Instance
- **AMI**: Ubuntu 22.04 LTS
- **Instance Type**: t2.micro (free tier)
- **Storage**: 20GB gp3
- **Security Group**: Create new
  - SSH (22): Your IP only
  - HTTP (80): 0.0.0.0/0
  - HTTPS (443): 0.0.0.0/0
- **Key Pair**: Create/select SSH key
- **Elastic IP**: Allocate and associate (so IP doesn't change)

### 1.2 Note Your Info
```
EC2 Public IP: ___.___.___.___
SSH Key: ~/.ssh/your-key.pem
```

---

## Phase 2: Domain Configuration

### 2.1 Add DNS Record
In your DNS provider (Route53/Cloudflare/etc):
```
Type: A
Name: fantasma
Value: [Your EC2 Elastic IP]
TTL: 300
```

### 2.2 Verify DNS
```bash
# Wait 5-10 minutes, then test:
nslookup fantasma.mriveralanas.com
# Should return your EC2 IP
```

---

## Phase 3: Server Setup

### 3.1 Connect to EC2
```bash
ssh -i ~/.ssh/your-key.pem ubuntu@fantasma.mriveralanas.com
```

### 3.2 Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python, Node, Nginx, Certbot
sudo apt install -y python3.11 python3.11-venv python3-pip nginx certbot python3-certbot-nginx nodejs npm git

# Verify versions
python3.11 --version
node --version
nginx -v
```

### 3.3 Create App Directory
```bash
sudo mkdir -p /var/www/fantasma
sudo chown ubuntu:ubuntu /var/www/fantasma
cd /var/www/fantasma
```

---

## Phase 4: Deploy Backend

### 4.1 Upload Backend Code
On your LOCAL machine:
```bash
cd ~/projects/google_auto
rsync -avz -e "ssh -i ~/.ssh/your-key.pem" \
  backend/ \
  ubuntu@fantasma.mriveralanas.com:/var/www/fantasma/backend/
```

### 4.2 Setup Python Environment on EC2
```bash
ssh -i ~/.ssh/your-key.pem ubuntu@fantasma.mriveralanas.com

cd /var/www/fantasma/backend
python3.11 -m venv venv
source venv/bin/activate
pip install flask flask-cors google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-docx pandas openpyxl
```

### 4.3 Upload Credentials (SECURE)
On LOCAL machine:
```bash
# DO NOT commit these files to git!
scp -i ~/.ssh/your-key.pem \
  ~/projects/google_auto/backend/credentials.json \
  ubuntu@fantasma.mriveralanas.com:/var/www/fantasma/backend/

scp -i ~/.ssh/your-key.pem \
  ~/projects/google_auto/backend/token.json \
  ubuntu@fantasma.mriveralanas.com:/var/www/fantasma/backend/
```

### 4.4 Create Systemd Service
On EC2:
```bash
sudo nano /etc/systemd/system/fantasma-backend.service
```

Add:
```ini
[Unit]
Description=Fantasma Wine Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/var/www/fantasma/backend
Environment="PATH=/var/www/fantasma/backend/venv/bin"
ExecStart=/var/www/fantasma/backend/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4.5 Start Backend Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable fantasma-backend
sudo systemctl start fantasma-backend
sudo systemctl status fantasma-backend  # Should show "active (running)"
```

---

## Phase 5: Deploy Frontend

### 5.1 Update Frontend Config (LOCAL)
Edit `frontend/src/App.svelte`:
```javascript
// Change this line:
const response = await fetch('http://localhost:5000/api/generate-sheet', {

// To this:
const response = await fetch('/api/generate-sheet', {
```

Also update feedback endpoint:
```javascript
const response = await fetch('/api/feedback', {
```

### 5.2 Build Frontend (LOCAL)
```bash
cd ~/projects/google_auto/frontend
npm run build
```

### 5.3 Upload Build to EC2 (LOCAL)
```bash
rsync -avz -e "ssh -i ~/.ssh/your-key.pem" \
  dist/ \
  ubuntu@fantasma.mriveralanas.com:/var/www/fantasma/frontend/
```

---

## Phase 6: Configure Nginx

### 6.1 Create Nginx Config (ON EC2)
```bash
sudo nano /etc/nginx/sites-available/fantasma
```

Add:
```nginx
server {
    listen 80;
    server_name fantasma.mriveralanas.com;

    # Frontend
    location / {
        root /var/www/fantasma/frontend;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:5000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 6.2 Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/fantasma /etc/nginx/sites-enabled/
sudo nginx -t  # Test config
sudo systemctl restart nginx
```

### 6.3 Test HTTP Access
Visit: http://fantasma.mriveralanas.com
(Should load the app, but without HTTPS yet)

---

## Phase 7: Add SSL (HTTPS)

### 7.1 Get SSL Certificate
```bash
sudo certbot --nginx -d fantasma.mriveralanas.com
```

Follow prompts:
- Enter email
- Agree to terms
- Redirect HTTP to HTTPS: Yes

### 7.2 Verify HTTPS
Visit: https://fantasma.mriveralanas.com
(Should show secure lock icon)

### 7.3 Auto-renewal
```bash
sudo certbot renew --dry-run  # Test auto-renewal
```

---

## Phase 8: Update Google OAuth

### 8.1 Add Production Redirect URI
Go to: https://console.cloud.google.com/apis/credentials

Click your OAuth client, add:
- `https://fantasma.mriveralanas.com`

Save and download new credentials.json if needed.

---

## Maintenance Commands

### Check Backend Status
```bash
sudo systemctl status fantasma-backend
sudo journalctl -u fantasma-backend -f  # Live logs
```

### Update Backend Code
```bash
# On LOCAL:
rsync -avz -e "ssh -i ~/.ssh/your-key.pem" \
  backend/ \
  ubuntu@fantasma.mriveralanas.com:/var/www/fantasma/backend/

# On EC2:
sudo systemctl restart fantasma-backend
```

### Update Frontend
```bash
# On LOCAL:
cd frontend
npm run build
rsync -avz -e "ssh -i ~/.ssh/your-key.pem" \
  dist/ \
  ubuntu@fantasma.mriveralanas.com:/var/www/fantasma/frontend/
```

### View Backend Logs
```bash
# On EC2:
cd /var/www/fantasma/backend
cat session_log.json | python -m json.tool  # Pretty print logs
python view_logs.py  # View all sessions
python view_feedback.py  # View user feedback
```

---

## Security Checklist

- [ ] SSH key-only access (disable password auth)
- [ ] Firewall enabled (ufw)
- [ ] credentials.json and token.json not in git
- [ ] HTTPS enabled
- [ ] Backend runs on localhost only (not exposed)
- [ ] Regular system updates
- [ ] SSL auto-renewal working

---

## Troubleshooting

**Backend won't start:**
```bash
sudo journalctl -u fantasma-backend -n 50
```

**Nginx errors:**
```bash
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

**Can't connect to backend:**
```bash
curl http://localhost:5000/api/health
```

**SSL issues:**
```bash
sudo certbot certificates
sudo certbot renew --force-renewal
```
