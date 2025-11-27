# Deployment Options

Choose your deployment method:

## 🐳 Docker (Recommended)

**File:** `DOCKER_DEPLOYMENT.md`

**Pros:**
- Simplest deployment
- Easy updates
- Isolated environment
- Portable

**Use this if:**
- You want the easiest deployment
- You're comfortable with Docker basics
- You want simple updates

**Time to deploy:** ~20-30 minutes

---

## 🔧 Manual Setup

**File:** `DEPLOYMENT.md`

**Pros:**
- More control
- Learn the stack deeply
- No Docker overhead

**Use this if:**
- You want to learn the internals
- You don't want Docker
- You need maximum control

**Time to deploy:** ~40-60 minutes

---

## Quick Comparison

| Feature | Docker | Manual |
|---------|--------|--------|
| Setup time | 20-30 min | 40-60 min |
| Updates | `docker compose up -d` | Manual restart services |
| Learning curve | Medium | Low |
| Flexibility | Medium | High |
| Maintenance | Easy | Medium |

---

## Local Development

See `WEB_APP.md` for running locally:

**Terminal 1:**
```bash
cd backend
source ../.venv/bin/activate
python app.py
```

**Terminal 2:**
```bash
cd frontend
npm run dev
```

Open: http://localhost:5173
