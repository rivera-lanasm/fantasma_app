#!/bin/bash
# Simple deployment helper script

set -e  # Exit on error

# Get project root (two levels up from this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Configuration
EC2_HOST="fantasma.mriveralanas.com"
EC2_USER="ubuntu"
SSH_KEY="${SSH_KEY:-~/.ssh/fantasma-key.pem}"
REMOTE_DIR="~/fantasma"

echo "🚀 Deploying to ${EC2_HOST}"
echo "📁 Project root: ${PROJECT_ROOT}"

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ SSH key not found at: $SSH_KEY"
    echo "Set SSH_KEY environment variable or update deploy.sh"
    exit 1
fi

# Upload backend
echo "📦 Uploading backend..."
rsync -avz -e "ssh -i $SSH_KEY" \
    --exclude 'node_modules' \
    --exclude '.venv' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude 'session_log.json' \
    --exclude 'feedback_log.json' \
    ${PROJECT_ROOT}/backend/ \
    ${EC2_USER}@${EC2_HOST}:${REMOTE_DIR}/backend/

# Upload frontend
echo "📦 Uploading frontend..."
rsync -avz -e "ssh -i $SSH_KEY" \
    --exclude 'node_modules' \
    --exclude 'dist' \
    ${PROJECT_ROOT}/frontend/ \
    ${EC2_USER}@${EC2_HOST}:${REMOTE_DIR}/frontend/

# Upload docker configs
echo "📦 Uploading Docker configs..."
scp -i "$SSH_KEY" \
    ${PROJECT_ROOT}/deployment/docker-compose.yml \
    ${PROJECT_ROOT}/deployment/nginx-ssl.conf \
    ${EC2_USER}@${EC2_HOST}:${REMOTE_DIR}/

# Rebuild and restart on EC2
echo "🔨 Rebuilding containers on EC2..."
ssh -i "$SSH_KEY" ${EC2_USER}@${EC2_HOST} << 'EOF'
    cd ~/fantasma
    docker compose build
    docker compose up -d
    echo "✅ Deployment complete!"
    echo ""
    echo "📊 Container status:"
    docker compose ps
EOF

echo ""
echo "🎉 Done! Visit https://${EC2_HOST}"
