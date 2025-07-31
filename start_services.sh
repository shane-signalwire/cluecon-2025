#!/bin/bash
set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Change to app directory
cd /app

# Source environment variables
if [[ ! -f .env ]]; then
    error "Environment file .env not found!"
    exit 1
fi
source .env

# Validate required environment variables
REQUIRED_VARS=("NGROK_TOKEN" "SIGNALWIRE_SPACE" "SW_PROJECT_ID" "SW_REST_API_TOKEN" "AGENT_PROMPT_FILE")
for var in "${REQUIRED_VARS[@]}"; do
    if [[ -z "${!var:-}" ]]; then
        error "Required environment variable $var is not set!"
        exit 1
    fi
done

# Function to cleanup background processes
cleanup() {
    log "Cleaning up background processes..."
    jobs -p | xargs -r kill 2>/dev/null || true
    wait
}

# Set up cleanup trap
trap cleanup EXIT INT TERM

# Setup ngrok
log "Setting up ngrok tunnel..."
ngrok authtoken "$NGROK_TOKEN" > /dev/null 2>&1 || {
    error "Failed to set ngrok auth token"
    exit 1
}

# Start ngrok tunnel
log "Starting ngrok tunnel on port 8080..."
ngrok http 8080 --log=stdout > /tmp/ngrok.log 2>&1 &
NGROK_PID=$!

# Wait for ngrok to be ready
log "Waiting for ngrok to initialize..."
for i in {1..30}; do
    if curl -s localhost:4040/api/tunnels >/dev/null 2>&1; then
        break
    fi
    if [[ $i -eq 30 ]]; then
        error "Ngrok failed to start after 30 seconds"
        exit 1
    fi
    sleep 1
done

# Get ngrok URL
NGROK_URL=$(curl -s localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url // empty')
if [[ -z "$NGROK_URL" ]]; then
    error "Failed to get ngrok URL"
    exit 1
fi
export NGROK_URL
success "Ngrok tunnel established: $NGROK_URL"

# Setup Python environment
log "Setting up Python environment..."
if [[ ! -d venv ]]; then
    python3 -m venv venv
fi
source ./venv/bin/activate

# Install dependencies
log "Installing Python dependencies..."
pip install --quiet --no-cache-dir -r requirements.txt

# Start Flask app
log "Starting Flask application..."
python3 app.py > /tmp/flask.log 2>&1 &
FLASK_PID=$!

# Wait for Flask to be ready
log "Waiting for Flask to initialize..."
for i in {1..30}; do
    if curl -s localhost:8080 >/dev/null 2>&1; then
        break
    fi
    if [[ $i -eq 30 ]]; then
        error "Flask failed to start after 30 seconds"
        exit 1
    fi
    sleep 1
done
success "Flask application is running"

# Generate authentication credentials
log "Generating authentication credentials..."
AUTH_PASSWORD=$(openssl rand -hex 16)

# Create agent configuration
log "Creating agent configuration..."
cat > /app/config.json << EOF
{
  "service": {
    "name": "max-electric-agent",
    "host": "\${HOST|0.0.0.0}",
    "port": "\${PORT|3000}"
  },
  "security": {
    "ssl_enabled": "\${SSL_ENABLED|false}",
    "ssl_cert_path": "\${SSL_CERT|/etc/ssl/cert.pem}",
    "ssl_key_path": "\${SSL_KEY|/etc/ssl/key.pem}",
    "auth": {
      "basic": {
        "enabled": true,
        "user": "\${AUTH_USER|signalwire}",
        "password": "${AUTH_PASSWORD}"
      },
      "bearer": {
        "enabled": "\${BEARER_ENABLED|false}",
        "token": "\${BEARER_TOKEN}"
      }
    },
    "allowed_hosts": ["\${PRIMARY_HOST}", "\${SECONDARY_HOST|localhost}"],
    "cors_origins": "\${CORS_ORIGINS|*}",
    "rate_limit": "\${RATE_LIMIT|60}"
  }
}
EOF

# Start agent service
log "Starting agent service..."
python3 $AGENT_PROMPT_FILE > /tmp/agent.log 2>&1 &
AGENT_PID=$!

# Wait for agent to be ready
log "Waiting for agent service to initialize..."
for i in {1..30}; do
    if curl -s localhost:3000 >/dev/null 2>&1; then
        break
    fi
    if [[ $i -eq 30 ]]; then
        error "Agent service failed to start after 30 seconds"
        exit 1
    fi
    sleep 1
done
success "Agent service is running"

# Update SWML webhook
log "Updating SWML webhook configuration..."
BASE_NGROK_URL="${NGROK_URL#https://}"
PRIMARY_REQUEST_URL="https://signalwire:${AUTH_PASSWORD}@${BASE_NGROK_URL}/agent"

if python3 resource.py "$PRIMARY_REQUEST_URL" > /tmp/webhook.log 2>&1; then
    success "SWML webhook updated successfully"
else
    warn "Failed to update SWML webhook (check /tmp/webhook.log)"
fi

# Display startup information
echo
echo "=================================="
echo "🎉 Max Electric Services Started!"
echo "=================================="
echo "Frontend URL: $NGROK_URL"
echo "Agent Auth Password: $AUTH_PASSWORD"
echo "Webhook URL: $PRIMARY_REQUEST_URL"
echo
echo "Log files:"
echo "  - Ngrok: /tmp/ngrok.log"
echo "  - Flask: /tmp/flask.log"
echo "  - Agent: /tmp/agent.log"
echo "  - Webhook: /tmp/webhook.log"
echo "=================================="

# Monitor services
log "Monitoring services... (Press Ctrl+C to stop)"
while true; do
    # Check if services are still running
    if ! kill -0 $FLASK_PID 2>/dev/null; then
        error "Flask service died!"
        exit 1
    fi
    
    if ! kill -0 $AGENT_PID 2>/dev/null; then
        error "Agent service died!"
        exit 1
    fi
    
    if ! kill -0 $NGROK_PID 2>/dev/null; then
        error "Ngrok tunnel died!"
        exit 1
    fi
    
    sleep 30
done 