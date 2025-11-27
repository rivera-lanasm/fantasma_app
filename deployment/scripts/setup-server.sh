#!/bin/bash
# Server setup script - installs Docker, Claude Code, and prerequisites

set -e  # Exit on error

echo "🚀 Setting up server for Fantasma deployment"

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
rm get-docker.sh

# Add ubuntu user to docker group
echo "👤 Adding ubuntu user to docker group..."
sudo usermod -aG docker ubuntu

# Install Docker Compose
echo "🐳 Installing Docker Compose plugin..."
sudo apt install docker-compose-plugin -y

# Verify Docker installation
echo "✅ Verifying Docker installation..."
docker --version
docker compose version

# Install Certbot (for SSL certificates)
echo "🔒 Installing Certbot..."
sudo apt install -y certbot

# Install Claude Code
echo "🤖 Installing Claude Code..."

# Install Node.js (required for Claude Code)
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install Claude Code via npm
echo "📦 Installing Claude Code CLI..."
sudo npm install -g @anthropic-ai/claude-code

# Verify Claude Code installation
echo "✅ Verifying Claude Code installation..."
claude-code --version || echo "⚠️  Claude Code installed but needs API key configuration"

echo ""
echo "✅ Server setup complete!"
echo ""
echo "⚠️  IMPORTANT NEXT STEPS:"
echo "1. Logout and login again for Docker group changes:"
echo "   exit"
echo "   ssh -i ~/.ssh/fantasma-key.pem ubuntu@fantasma.mriveralanas.com"
echo ""
echo "2. Configure Claude Code with your API key:"
echo "   claude-code config set api-key YOUR_API_KEY"
echo ""
echo "3. Verify Claude Code works:"
echo "   claude-code --help"
