# Deployment Directory

This directory contains all files and scripts needed to deploy the Fantasma wine app to production.

---

## Directory Structure

```
deployment/
├── scripts/
│   ├── setup-server.sh   # Initial server setup (Docker, Claude Code, etc.)
│   └── deploy.sh         # Deploy application updates
├── docker-compose.yml    # Docker container orchestration
├── nginx-ssl.conf        # Nginx web server configuration
└── README.md            # This file
```

---

## File Descriptions

### `nginx-ssl.conf`

**Purpose:** Configures nginx web server to handle incoming web traffic.

**What it does:**
- **HTTP Server (port 80):** Redirects all traffic to HTTPS for security
  - Exception: Allows Let's Encrypt verification for SSL certificate renewal
- **HTTPS Server (port 443):**
  - Uses SSL certificates from Let's Encrypt for encryption
  - Serves frontend files (Svelte app)
  - Routes API requests (`/api/`) to backend container (Flask on port 5000)
  - Configured for Server-Sent Events (SSE) streaming

**In simple terms:** This is the "front door" to your app. All web traffic hits nginx first, which serves the frontend and forwards API calls to the backend.

### `docker-compose.yml`

**Purpose:** Defines how to build and run the application containers.

**What it does:**
- Defines two services: `backend` and `frontend`
- Configures networking between containers
- Mounts volumes for credentials and SSL certificates
- Maps ports to host machine

### `scripts/setup-server.sh`

**Purpose:** Initial server setup - installs Docker, Claude Code, and all prerequisites.

**What it does:**
1. Updates system packages
2. Installs Docker and Docker Compose
3. Adds ubuntu user to docker group
4. Installs Certbot (for SSL certificates)
5. Installs Node.js (required for Claude Code)
6. Installs Claude Code CLI globally

**How to use:**
```bash
# SSH into server
ssh -i ~/.ssh/fantasma-key.pem ubuntu@fantasma.mriveralanas.com

# Upload and run setup script
# (From local machine)
scp -i ~/.ssh/fantasma-key.pem deployment/scripts/setup-server.sh ubuntu@fantasma.mriveralanas.com:~/
ssh -i ~/.ssh/fantasma-key.pem ubuntu@fantasma.mriveralanas.com "bash ~/setup-server.sh"
```

**After running:**
1. Logout and login again for Docker group changes
2. Configure Claude Code with API key: `claude-code config set api-key YOUR_API_KEY`
3. Verify: `claude-code --help`

**Note:** Only needs to be run once during initial server setup.

### `scripts/deploy.sh`

**Purpose:** Automates the code deployment process to the EC2 server.

**What it does:**
1. Uploads backend code to server (excluding virtual env, cache files)
2. Uploads frontend code to server (excluding node_modules, dist)
3. Uploads Docker configs (docker-compose.yml, nginx-ssl.conf)
4. Rebuilds Docker containers on the server
5. Restarts the application
6. Shows container status

**How to use:**
```bash
# From project root
./deployment/scripts/deploy.sh

# Or specify a custom SSH key
SSH_KEY=~/.ssh/my-key.pem ./deployment/scripts/deploy.sh
```

**Requirements:**
- SSH key must be at `~/.ssh/fantasma-key.pem` (or set `SSH_KEY` environment variable)
- Server must already have Docker installed
- Must be run from anywhere in the project (script auto-detects project root)

---

## Deployment Info

- **Domain:** fantasma.mriveralanas.com
- **Server IP:** 35.168.238.72
- **EC2 Instance:** i-0031951f1b9a33bdd
- **Security Group:** sg-0715fa34e3e06f2d2
- **SSH Key:** ~/.ssh/fantasma-key.pem

---

## Quick Reference

### SSH into server
```bash
ssh -i ~/.ssh/fantasma-key.pem ubuntu@fantasma.mriveralanas.com
```

### Initial server setup (one-time)
```bash
# Upload and run setup script
scp -i ~/.ssh/fantasma-key.pem deployment/scripts/setup-server.sh ubuntu@fantasma.mriveralanas.com:~/
ssh -i ~/.ssh/fantasma-key.pem ubuntu@fantasma.mriveralanas.com "bash ~/setup-server.sh"
```

### Deploy application updates
```bash
# From project root
./deployment/scripts/deploy.sh
```

### Configure Claude Code on server
```bash
# SSH into server first, then:
claude-code config set api-key YOUR_ANTHROPIC_API_KEY
```

---

## Documentation

Full deployment guide: `../docs/DOCKER_DEPLOYMENT.md`
