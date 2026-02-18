#!/bin/bash
set -e

# Hetzner Deployment Script for AI Pathway
# Usage: ./deploy-hetzner.sh [setup|deploy|logs|status]

SERVER_IP="95.216.199.47"
SERVER_USER="root"
APP_DIR="/opt/ai-pathway"
REPO_URL="https://github.com/ColaberryIntern/AI_Pathway.git"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

ssh_cmd() {
    ssh -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_IP}" "$1"
}

# Step 1: Install Docker and Docker Compose on the server
setup_server() {
    log_info "Setting up server at ${SERVER_IP}..."

    ssh_cmd "bash -s" << 'SETUP_EOF'
set -e

# Update system
apt-get update && apt-get upgrade -y

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
else
    echo "Docker already installed"
fi

# Install Docker Compose plugin if not present
if ! docker compose version &> /dev/null; then
    echo "Installing Docker Compose plugin..."
    apt-get install -y docker-compose-plugin
else
    echo "Docker Compose already installed"
fi

# Install git if not present
if ! command -v git &> /dev/null; then
    apt-get install -y git
fi

# Open firewall ports (if ufw is active)
if command -v ufw &> /dev/null && ufw status | grep -q "active"; then
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 22/tcp
    echo "Firewall rules updated"
fi

echo "Server setup complete!"
docker --version
docker compose version
SETUP_EOF

    log_info "Server setup complete!"
}

# Step 2: Deploy the application
deploy() {
    log_info "Deploying to ${SERVER_IP}..."

    # Check if .env exists locally
    if [ ! -f "backend/.env" ]; then
        log_error "backend/.env not found. Create it with your API keys first."
        exit 1
    fi

    ssh_cmd "bash -s" << DEPLOY_EOF
set -e

# Clone or update repo
if [ -d "${APP_DIR}" ]; then
    echo "Updating existing deployment..."
    cd ${APP_DIR}
    git fetch origin
    git reset --hard origin/main
else
    echo "Cloning repository..."
    git clone ${REPO_URL} ${APP_DIR}
    cd ${APP_DIR}
fi

# Create .env directory
mkdir -p ${APP_DIR}/backend
DEPLOY_EOF

    # Copy .env file to server (contains API keys - not in git)
    log_info "Copying .env file to server..."
    scp -o StrictHostKeyChecking=no backend/.env "${SERVER_USER}@${SERVER_IP}:${APP_DIR}/backend/.env"

    ssh_cmd "bash -s" << DEPLOY2_EOF
set -e
cd ${APP_DIR}

# Build and start containers
echo "Building containers..."
docker compose build --no-cache

echo "Starting services..."
docker compose up -d

# Wait for backend to be healthy
echo "Waiting for backend to start..."
for i in {1..30}; do
    if docker compose exec -T backend curl -s http://localhost:8080/api/health > /dev/null 2>&1; then
        echo "Backend is healthy!"
        break
    fi
    if [ \$i -eq 30 ]; then
        echo "Warning: Backend health check timed out, check logs with: docker compose logs backend"
    fi
    sleep 2
done

# Show status
docker compose ps
echo ""
echo "============================================"
echo "  AI Pathway deployed successfully!"
echo "  URL: http://${SERVER_IP}"
echo "============================================"
DEPLOY2_EOF

    log_info "Deployment complete!"
    log_info "Access the app at: http://${SERVER_IP}"
}

# Show logs
show_logs() {
    log_info "Showing logs from ${SERVER_IP}..."
    ssh_cmd "cd ${APP_DIR} && docker compose logs --tail=100 -f"
}

# Show status
show_status() {
    log_info "Status of services on ${SERVER_IP}..."
    ssh_cmd "cd ${APP_DIR} && docker compose ps && echo '' && docker compose logs --tail=5"
}

# Restart services
restart() {
    log_info "Restarting services on ${SERVER_IP}..."
    ssh_cmd "cd ${APP_DIR} && docker compose restart"
    log_info "Services restarted"
}

# Main
case "${1:-deploy}" in
    setup)
        setup_server
        ;;
    deploy)
        deploy
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    restart)
        restart
        ;;
    *)
        echo "Usage: $0 [setup|deploy|logs|status|restart]"
        echo "  setup   - Install Docker on server (run once)"
        echo "  deploy  - Build and deploy application"
        echo "  logs    - Tail application logs"
        echo "  status  - Show container status"
        echo "  restart - Restart all services"
        exit 1
        ;;
esac
