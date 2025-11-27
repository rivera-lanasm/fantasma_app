# Fantasma Wine Tasting Sheet Generator

Automated web application to generate wine tasting sheets and price lists from Google Sheets data.

## Overview

This tool allows you to:
- Search for wines by producer name or cuvee
- Generate formatted tasting sheets (Word documents)
- Generate price lists with standard and discount pricing
- Automatically upload generated documents to Google Drive with timestamped versioning

**Tech Stack:**
- **Backend:** Python/Flask with Google Drive API integration
- **Frontend:** Svelte
- **Deployment:** Docker + nginx on AWS EC2
- **Domain:** https://fantasma.mriveralanas.com

---

## Project Structure

```
google_auto/
├── backend/              # Flask API + Google Drive integration
│   ├── app.py            # Main Flask application
│   ├── generate_selected_wines.py  # Document generation
│   ├── search_and_generate.py      # Wine search logic
│   └── templates/        # Word document templates
├── frontend/             # Svelte web interface
├── deployment/           # Deployment configurations
│   ├── scripts/          # Deployment bash scripts
│   ├── docker-compose.yml
│   └── nginx-ssl.conf
├── docs/                 # Documentation
│   ├── DOCKER_DEPLOYMENT.md  # Full deployment guide
│   ├── WEB_APP.md            # Local development guide
│   └── ...
└── .claude/              # Claude Code configurations
```

---

## Quick Start

### Local Development

See **[docs/WEB_APP.md](docs/WEB_APP.md)** for detailed setup instructions.

**Terminal 1 - Backend:**
```bash
cd backend
source ../.venv/bin/activate
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Open: http://localhost:5173

### Deploy to Production

See **[deployment/README.md](deployment/README.md)** for deployment instructions.

```bash
./deployment/scripts/deploy.sh
```

---

## Documentation

- **[docs/WEB_APP.md](docs/WEB_APP.md)** - Local development setup
- **[docs/DOCKER_DEPLOYMENT.md](docs/DOCKER_DEPLOYMENT.md)** - Full AWS deployment guide
- **[deployment/README.md](deployment/README.md)** - Deployment quick reference

---

## Google OAuth Setup

The application requires Google OAuth credentials to access Google Drive.

**Quick steps:**
1. Create Google Cloud Project
2. Enable Google Drive API
3. Create OAuth Desktop App credentials
4. Download `credentials.json` to `backend/`
5. Run `backend/test_auth.py` for one-time authorization

See **[docs/WEB_APP.md](docs/WEB_APP.md)** for detailed OAuth setup instructions.

---

## Usage

### Web Interface
1. Visit https://fantasma.mriveralanas.com (or http://localhost:5173 locally)
2. Enter wine search query (e.g., "both scopa and realce")
3. Click "Generate Tasting Sheet"
4. Generated documents uploaded to Google Drive automatically

### Query Examples
- `both scopa` - All wines from Scopa producer
- `both scopa and realce` - All wines from both producers
- Handles typos and partial matches

---

## Features

✅ Natural language wine search
✅ Automatic tasting sheet generation
✅ Price list generation with standard/discount pricing
✅ Timestamped document versioning (YYYY-MM-DD_vN)
✅ Real-time generation feedback via SSE streaming
✅ User feedback collection
✅ Session logging
✅ Secure HTTPS deployment with Let's Encrypt SSL

---

## Production Deployment

**Live at:** https://fantasma.mriveralanas.com

**Infrastructure:**
- AWS EC2 (t2.small, Ubuntu 22.04)
- Docker + Docker Compose
- Nginx reverse proxy with SSL
- Route53 DNS

See **[docs/DOCKER_DEPLOYMENT.md](docs/DOCKER_DEPLOYMENT.md)** for complete deployment guide.

