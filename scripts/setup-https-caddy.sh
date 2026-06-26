#!/bin/bash
# Stand up HTTPS for AI Pathway on the Hetzner box using Caddy (automatic
# Let's Encrypt). This is the prerequisite for SSO go-live: Auth0 (and every
# real IdP) rejects http:// callback URLs for non-localhost hosts.
#
# PREREQUISITE (manual, one-time): point a domain's DNS A record at
# 95.216.199.47 and wait for it to propagate. Caddy needs the domain to resolve
# to this host to obtain a certificate.
#
# Caddy terminates TLS on 443 and reverse-proxies to the existing frontend
# container on localhost:3000 (which already proxies /api to the backend). The
# raw http://...:3000 stays reachable; this just adds https://<domain>.
#
# Usage (run ON the server, or:  ssh root@95.216.199.47 'bash -s' < scripts/setup-https-caddy.sh <domain>):
#   bash setup-https-caddy.sh ai-pathway.example.com
set -euo pipefail

DOMAIN="${1:-}"
if [ -z "$DOMAIN" ]; then
  echo "usage: $0 <domain>  (DNS A record must already point at this server)"
  exit 1
fi

echo "[1/4] verifying $DOMAIN resolves to this host..."
RESOLVED="$(getent hosts "$DOMAIN" | awk '{print $1}' | head -1 || true)"
THIS_IP="$(curl -s ifconfig.me || echo unknown)"
echo "    $DOMAIN -> ${RESOLVED:-<none>} ; this host -> $THIS_IP"
if [ "$RESOLVED" != "$THIS_IP" ]; then
  echo "    WARN: DNS does not (yet) point here. Caddy cert issuance will fail until it does."
fi

echo "[2/4] installing Caddy (if absent)..."
if ! command -v caddy >/dev/null 2>&1; then
  apt-get install -y debian-keyring debian-archive-keyring apt-transport-https curl
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
  apt-get update && apt-get install -y caddy
fi

echo "[3/4] writing Caddyfile (reverse proxy $DOMAIN -> 127.0.0.1:3000)..."
cat > /etc/caddy/Caddyfile <<CADDY
$DOMAIN {
    reverse_proxy 127.0.0.1:3000
}
CADDY

echo "[4/4] reloading Caddy (obtains + renews the cert automatically)..."
systemctl enable caddy
systemctl restart caddy
sleep 3
systemctl --no-pager status caddy | head -5

cat <<NEXT

HTTPS setup attempted for https://$DOMAIN

Next steps to turn SSO on:
  1. In Auth0, set Allowed Callback URL  = https://$DOMAIN/api/auth/callback
                    Allowed Logout URL   = https://$DOMAIN/
                    Allowed Web Origins  = https://$DOMAIN
  2. In /opt/ai-pathway/backend/.env set:
       OIDC_ENABLED=true
       OIDC_ISSUER=https://<your-auth0-domain>
       OIDC_CLIENT_ID=...
       OIDC_CLIENT_SECRET=...
       OIDC_REDIRECT_URI=https://$DOMAIN/api/auth/callback
       SESSION_SECRET=...   (provided out of band)
  3. Add https://$DOMAIN to CORS_ORIGINS in backend/.env.
  4. docker compose up -d   (restart backend to pick up env)
  5. Verify: https://$DOMAIN/api/auth/status -> {"enabled": true}, then /api/auth/login
NEXT
