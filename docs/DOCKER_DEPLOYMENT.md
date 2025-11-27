# Docker Deployment Guide: fantasma.mriveralanas.com

This guide uses Docker Compose for a simpler, more maintainable deployment.

---

## Prerequisites

- AWS account
- AWS CLI installed locally
- Domain: mriveralanas.com (with DNS access)
- Local development environment with this project

---

## Phase 0: AWS CLI Setup

### 0.1 Install AWS CLI (if needed)
```bash
# Check if installed
aws --version

# If not installed, follow: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
```

### 0.2 Create IAM User (DO NOT use root credentials)

**In AWS Console:**

1. Go to: https://console.aws.amazon.com/iam/home#/users
2. Click **"Create user"**
3. User name: `fantasma-deploy`
4. Click **"Next"**
5. Select **"Attach policies directly"**
6. Search and check both:
   - **`AmazonEC2FullAccess`**
   - **`AmazonRoute53FullAccess`**
7. Click **"Next"** → **"Create user"**
8. Click on the user **`fantasma-deploy`**
9. Go to **"Security credentials"** tab
10. Click **"Create access key"**
11. Select: **"Command Line Interface (CLI)"**
12. Check confirmation box → **"Next"** → **"Create access key"**
13. **Copy both keys** (Access key ID and Secret access key)

### 0.3 Configure AWS CLI

```bash
aws configure
```

Enter:
- **AWS Access Key ID**: [paste from step 0.2]
- **AWS Secret Access Key**: [paste from step 0.2]
- **Default region name**: `us-east-1` (or your preferred region)
- **Default output format**: `json`

### 0.4 Verify Configuration

```bash
aws sts get-caller-identity
```

Should show:
```json
{
    "UserId": "AIDA...",
    "Account": "891635012352",
    "Arn": "arn:aws:iam::891635012352:user/fantasma-deploy"
}
```

✅ AWS CLI is now configured!

### 0.5 Add Route53 Permission (if needed)

**If you created the user without Route53 permissions**, add them via console:

1. Go to: https://console.aws.amazon.com/iam/home#/users/fantasma-deploy
2. Click **"Add permissions"** → **"Attach policies directly"**
3. Search for and check: **`AmazonRoute53FullAccess`**
4. Click **"Next"** → **"Add permissions"**

Now you can use Route53 CLI commands.

---

## Phase 1: Create AWS Infrastructure

### 1.1 Create Security Group

**What it does:** Creates a firewall to control network access to your EC2 instance.

```bash
aws ec2 create-security-group \
  --group-name fantasma-sg \
  --description "Security group for Fantasma wine app" \
  --region us-east-1
```

**Expected output:**
```json
{
    "GroupId": "sg-0715fa34e3e06f2d2"
}
```

**Save the GroupId** - you'll need it for the next steps.

### 1.2 Add Security Group Rules

**What it does:** Opens ports in the firewall to allow SSH, HTTP, and HTTPS traffic.

#### Add SSH Rule (Port 22)
```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-0715fa34e3e06f2d2 \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0 \
  --region us-east-1
```

**Expected output:**
```json
{
    "Return": true,
    "SecurityGroupRules": [
        {
            "SecurityGroupRuleId": "sgr-0d9da9e526a31b193",
            "IpProtocol": "tcp",
            "FromPort": 22,
            "ToPort": 22
        }
    ]
}
```

#### Add HTTP Rule (Port 80)
```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-0715fa34e3e06f2d2 \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0 \
  --region us-east-1
```

**Expected output:**
```json
{
    "Return": true,
    "SecurityGroupRules": [
        {
            "SecurityGroupRuleId": "sgr-...",
            "IpProtocol": "tcp",
            "FromPort": 80,
            "ToPort": 80
        }
    ]
}
```

#### Add HTTPS Rule (Port 443)
```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-0715fa34e3e06f2d2 \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0 \
  --region us-east-1
```

**Expected output:**
```json
{
    "Return": true,
    "SecurityGroupRules": [
        {
            "SecurityGroupRuleId": "sgr-...",
            "IpProtocol": "tcp",
            "FromPort": 443,
            "ToPort": 443
        }
    ]
}
```

### 1.3 Create SSH Key Pair

**What it does:** Creates an SSH key pair for secure access to your EC2 instance.

```bash
aws ec2 create-key-pair \
  --key-name fantasma-key \
  --query 'KeyMaterial' \
  --output text \
  --region us-east-1 > ~/.ssh/fantasma-key.pem
```

**Set proper permissions:**
```bash
chmod 400 ~/.ssh/fantasma-key.pem
```

**Verify:**
```bash
ls -l ~/.ssh/fantasma-key.pem
# Should show: -r-------- (read-only for owner)
```

**Save this file!** You'll need `fantasma-key.pem` to SSH into your server.

### 1.4 Launch EC2 Instance

**What it does:** Creates a virtual server running Ubuntu 22.04.

#### Find the latest Ubuntu 22.04 AMI:
```bash
aws ec2 describe-images \
  --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
  --output text \
  --region us-east-1
```

**Result:** `ami-03deb8c961063af8c`

#### Launch the instance:
```bash
aws ec2 run-instances \
  --image-id ami-03deb8c961063af8c \
  --instance-type t2.small \
  --key-name fantasma-key \
  --security-group-ids sg-0715fa34e3e06f2d2 \
  --region us-east-1 \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=fantasma-wine-app}]'
```

**Result:** Instance ID: `i-0031951f1b9a33bdd`

#### Wait for instance to be running:
```bash
aws ec2 wait instance-running \
  --instance-ids i-0031951f1b9a33bdd \
  --region us-east-1
```

This command waits until the instance state is "running" (may take 1-2 minutes).

### 1.5 Allocate Elastic IP

**What it does:** Creates a permanent public IP address for your server.

#### Allocate the IP:
```bash
aws ec2 allocate-address \
  --domain vpc \
  --region us-east-1
```

**Result:**
```json
{
    "AllocationId": "eipalloc-091d030dda3704d65",
    "PublicIp": "35.168.238.72"
}
```

**Cost:** FREE while attached to a running instance.

#### Associate IP to instance:
```bash
aws ec2 associate-address \
  --instance-id i-0031951f1b9a33bdd \
  --allocation-id eipalloc-091d030dda3704d65 \
  --region us-east-1
```

**Your server's permanent IP:** `35.168.238.72`

### 1.6 Configure DNS

**What it does:** Points fantasma.mriveralanas.com to your server's IP address.

**Option A: Via AWS Console (Route53):**

1. Add Route53 permission first (see section 0.5 above)
2. Go to: https://console.aws.amazon.com/iam/home#/users/fantasma-deploy
3. Add **AmazonRoute53FullAccess** permission
4. Go to: https://console.aws.amazon.com/route53/v2/hostedzones
5. Click on **mriveralanas.com** hosted zone
6. Click **"Create record"**
7. Fill in:
   - **Record name:** fantasma
   - **Record type:** A
   - **Value:** 35.168.238.72
   - **TTL:** 300
8. Click **"Create records"**

**Option B: Via CLI (if you have Route53 permissions):**

First, verify your domain is in Route53:
```bash
aws route53 list-hosted-zones \
  --query "HostedZones[].Name" \
  --output text
```

**Result:** Should show `mriveralanas.com.`

Then, find your hosted zone ID:
```bash
aws route53 list-hosted-zones \
  --query "HostedZones[?Name=='mriveralanas.com.'].Id" \
  --output text
```

**Result:** `/hostedzone/Z10047232MZSEQSO8HYG4`

Then create the DNS record:
```bash
aws route53 change-resource-record-sets \
  --hosted-zone-id Z10047232MZSEQSO8HYG4 \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "fantasma.mriveralanas.com",
        "Type": "A",
        "TTL": 300,
        "ResourceRecords": [{"Value": "35.168.238.72"}]
      }
    }]
  }'
```

**Result:**
```json
{
    "ChangeInfo": {
        "Id": "/change/C018896818LJV7WCG8YRZ",
        "Status": "PENDING"
    }
}
```

**Wait 5-10 minutes for DNS to propagate**, then verify:
```bash
nslookup fantasma.mriveralanas.com
```

**Result:**
```
Server:         10.255.255.254
Address:        10.255.255.254#53

Non-authoritative answer:
Name:   fantasma.mriveralanas.com
Address: 35.168.238.72
```

✅ DNS is working! `fantasma.mriveralanas.com` now points to `35.168.238.72`

---

## Phase 2: Install Docker on EC2

### 2.1 Connect to EC2

**What it does:** SSH into your EC2 instance using the key pair we created.

```bash
ssh -i ~/.ssh/fantasma-key.pem ubuntu@fantasma.mriveralanas.com
```

If you get a "Host key verification" warning, type `yes` to continue.

### 2.2 Install Docker
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add ubuntu user to docker group
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Verify installation
docker --version
docker compose version

# Logout and login again for group changes
exit
ssh -i ~/.ssh/fantasma-key.pem ubuntu@fantasma.mriveralanas.com
```

### 2.3 Install Certbot (for SSL)
```bash
sudo apt install -y certbot
```

---

## Phase 3: Deploy Application

### 3.1 Create App Directory
```bash
mkdir -p ~/fantasma
cd ~/fantasma
```

### 3.2 Upload Project Files (FROM LOCAL MACHINE)
```bash
# On your local machine:
cd ~/projects/google_auto

# Upload backend
rsync -avz -e "ssh -i ~/.ssh/your-key.pem" \
  --exclude 'node_modules' \
  --exclude '.venv' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  backend/ \
  ubuntu@fantasma.mriveralanas.com:~/fantasma/backend/

# Upload frontend
rsync -avz -e "ssh -i ~/.ssh/your-key.pem" \
  --exclude 'node_modules' \
  --exclude 'dist' \
  frontend/ \
  ubuntu@fantasma.mriveralanas.com:~/fantasma/frontend/

# Upload docker configs
scp -i ~/.ssh/your-key.pem \
  docker-compose.yml \
  nginx-ssl.conf \
  ubuntu@fantasma.mriveralanas.com:~/fantasma/
```

### 3.3 Upload Credentials (SECURE)
```bash
# On your local machine:
scp -i ~/.ssh/your-key.pem \
  ~/projects/google_auto/backend/credentials.json \
  ubuntu@fantasma.mriveralanas.com:~/fantasma/backend/

scp -i ~/.ssh/your-key.pem \
  ~/projects/google_auto/backend/token.json \
  ubuntu@fantasma.mriveralanas.com:~/fantasma/backend/
```

---

## Phase 4: Get SSL Certificate (Before Starting Docker)

### 4.1 Get Certificate with Standalone Mode
```bash
# On EC2:
sudo certbot certonly --standalone -d fantasma.mriveralanas.com

# Follow prompts:
# - Enter email
# - Agree to terms
# - Certificate will be saved to /etc/letsencrypt/live/fantasma.mriveralanas.com/
```

### 4.2 Setup Auto-Renewal
```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot sets up automatic renewal via systemd timer
sudo systemctl status certbot.timer
```

---

## Phase 5: Start Application

### 5.1 Update docker-compose.yml
```bash
# On EC2:
cd ~/fantasma

# Make sure nginx-ssl.conf uses correct domain
cat nginx-ssl.conf | grep server_name
# Should show: server_name fantasma.mriveralanas.com;
```

### 5.2 Build and Start Containers
```bash
cd ~/fantasma

# Build images
docker compose build

# Start in detached mode
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

### 5.3 Verify Services
```bash
# Check backend
docker compose logs backend

# Check frontend
docker compose logs frontend

# Test backend health
curl http://localhost:5000/api/health
# Should return: {"status":"ok"}
```

---

## Phase 6: Verify Deployment

### 6.1 Test HTTP Access
Visit: http://fantasma.mriveralanas.com
(Should redirect to HTTPS)

### 6.2 Test HTTPS Access
Visit: https://fantasma.mriveralanas.com
- ✅ Should show secure lock icon
- ✅ App should load
- ✅ Can submit wine query

### 6.3 Test API
Open browser console on https://fantasma.mriveralanas.com
```javascript
fetch('/api/health').then(r => r.json()).then(console.log)
// Should show: {status: "ok"}
```

---

## Common Commands

### View Logs
```bash
# All services
docker compose logs -f

# Just backend
docker compose logs -f backend

# Just frontend
docker compose logs -f frontend

# Last 50 lines
docker compose logs --tail=50
```

### Restart Services
```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart backend
docker compose restart frontend
```

### Stop/Start
```bash
# Stop all
docker compose stop

# Start all
docker compose start

# Stop and remove containers (keeps images)
docker compose down

# Start again
docker compose up -d
```

### Update Code
```bash
# On LOCAL machine - upload new code:
rsync -avz -e "ssh -i ~/.ssh/your-key.pem" \
  --exclude 'node_modules' \
  backend/ \
  ubuntu@fantasma.mriveralanas.com:~/fantasma/backend/

# On EC2 - rebuild and restart:
cd ~/fantasma
docker compose build backend
docker compose up -d backend
```

### View Application Logs
```bash
# Session logs
docker compose exec backend cat session_log.json

# Feedback
docker compose exec backend python view_feedback.py
```

---

## Troubleshooting

### Backend won't start
```bash
docker compose logs backend
docker compose exec backend python -c "import flask; print(flask.__version__)"
```

### Frontend won't start
```bash
docker compose logs frontend
docker compose exec frontend nginx -t
```

### SSL certificate issues
```bash
# Check certificate
sudo certbot certificates

# Renew manually
sudo certbot renew --force-renewal

# After renewal, restart frontend
docker compose restart frontend
```

### Permission issues with credentials
```bash
# On EC2:
ls -la ~/fantasma/backend/*.json
# Should be readable by ubuntu user

# Fix if needed:
chmod 600 ~/fantasma/backend/credentials.json
chmod 600 ~/fantasma/backend/token.json
```

### Port conflicts
```bash
# Check what's using port 80/443
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443

# Stop conflicting services
sudo systemctl stop nginx  # If system nginx is running
```

---

## Updating the Application

### Backend Code Update
```bash
# LOCAL: Upload changes
rsync -avz -e "ssh -i ~/.ssh/your-key.pem" backend/ ubuntu@fantasma.mriveralanas.com:~/fantasma/backend/

# EC2: Rebuild and restart
cd ~/fantasma
docker compose build backend
docker compose up -d backend
```

### Frontend Code Update
```bash
# LOCAL: Upload changes
rsync -avz -e "ssh -i ~/.ssh/your-key.pem" frontend/ ubuntu@fantasma.mriveralanas.com:~/fantasma/frontend/

# EC2: Rebuild and restart
cd ~/fantasma
docker compose build frontend
docker compose up -d frontend
```

### Update Both
```bash
# LOCAL: Upload all
rsync -avz -e "ssh -i ~/.ssh/your-key.pem" \
  --exclude 'node_modules' --exclude '.venv' --exclude 'dist' \
  . ubuntu@fantasma.mriveralanas.com:~/fantasma/

# EC2: Rebuild everything
cd ~/fantasma
docker compose build
docker compose up -d
```

---

## Monitoring

### Resource Usage
```bash
# Container stats
docker stats

# Disk usage
docker system df
```

### Clean Up
```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Full cleanup
docker system prune -a
```

---

## Security Checklist

- [x] SSL certificate installed
- [x] HTTPS enforced (HTTP → HTTPS redirect)
- [x] Backend only accessible via nginx proxy
- [x] credentials.json and token.json not in git
- [x] Credentials mounted read-only in container
- [x] Firewall configured (Security Group)
- [x] SSL auto-renewal enabled

---

## Advantages of Docker Setup

✅ **Simple Updates**: `docker compose up -d` rebuilds and restarts
✅ **Isolated Environment**: No conflicts with system packages
✅ **Portable**: Works on any Docker host
✅ **Easy Rollback**: Keep old images, switch back if needed
✅ **Consistent**: Same environment local → production
✅ **No Systemd**: Docker handles service management

---

## Cost Estimate

- **EC2 t2.small**: ~$17/month
- **Elastic IP**: Free (while attached)
- **SSL Certificate**: Free (Let's Encrypt)
- **Total**: ~$17/month

Cheaper option: t2.micro ($8/month) - might be tight on memory for Docker

---

## Next Steps After Deployment

1. Monitor logs for first few days
2. Test all features (wine search, feedback, etc.)
3. Set up CloudWatch alarms (optional)
4. Configure automated backups of session/feedback logs
5. Update Google OAuth redirect URIs

**Your app will be live at:** https://fantasma.mriveralanas.com 🎉
