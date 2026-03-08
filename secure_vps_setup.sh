#!/bin/bash
set -e

echo "========================================="
echo " 1. Setting up 4GB Swap File (Crucial for 2GB RAM)"
echo "========================================="
if [ ! -f /swapfile ]; then
    sudo fallocate -l 4G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    sudo sysctl vm.swappiness=10
    echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
else
    echo "Swap already configured."
fi

echo "========================================="
echo " 2. Hardening SSH (Disabling Password Auth)"
echo "========================================="
sudo sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication no/g' /etc/ssh/sshd_config
sudo sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/g' /etc/ssh/sshd_config
sudo systemctl restart sshd || sudo systemctl restart ssh

echo "========================================="
echo " 3. Configuring Strict Firewall (UFW)"
echo "========================================="
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
# We intentionally DO NOT allow port 81 from the outside
sudo ufw --force enable

echo "========================================="
echo " 4. Installing Docker Engine"
echo "========================================="
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sudo sh
else
    echo "Docker already installed."
fi
sudo usermod -aG docker $USER

echo "========================================="
echo " 5. Setting up Shared Network (The 'Hallway')"
echo "========================================="
sudo docker network create public-proxy || true

echo "========================================="
echo " 6. Deploying SECURE Nginx Proxy Manager"
echo "========================================="
mkdir -p ~/npm-setup && cd ~/npm-setup
cat << 'EOF' > docker-compose.yml
version: '3.8'
services:
  app:
    image: 'jc21/nginx-proxy-manager:latest'
    restart: unless-stopped
    ports:
      - '80:80'
      - '443:443'
      - '127.0.0.1:81:81' # 🔒 SECURED: Only local access allowed
    volumes:
      - ./npm-data:/data
      - ./npm-letsencrypt:/etc/letsencrypt
    networks:
      - public-proxy

networks:
  public-proxy:
    external: true
EOF

sudo docker compose up -d

echo "========================================="
echo "✅ Server Setup & Hardening Complete!"
echo "========================================="
