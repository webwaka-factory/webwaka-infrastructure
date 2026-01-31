#!/bin/bash

################################################################################
# Partner Branding Configuration Script
#
# This script manages custom branding for partner-whitelabel instances.
#
# Usage: ./configure-branding.sh <partner-id> <config-file>
#
# Example: ./configure-branding.sh partner-001 branding.json
################################################################################

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Validate inputs
if [[ $# -lt 2 ]]; then
    log_error "Usage: $0 <partner-id> <config-file>"
    exit 1
fi

PARTNER_ID="$1"
CONFIG_FILE="$2"

if [[ ! -f "$CONFIG_FILE" ]]; then
    log_error "Configuration file not found: $CONFIG_FILE"
    exit 1
fi

log_info "Configuring branding for partner: $PARTNER_ID"
log_info "Configuration file: $CONFIG_FILE"

# Parse configuration
LOGO_URL=$(jq -r '.logo_url // empty' "$CONFIG_FILE")
PRIMARY_COLOR=$(jq -r '.primary_color // "#0066CC"' "$CONFIG_FILE")
SECONDARY_COLOR=$(jq -r '.secondary_color // "#333333"' "$CONFIG_FILE")
FAVICON_URL=$(jq -r '.favicon_url // empty' "$CONFIG_FILE")
CUSTOM_DOMAIN=$(jq -r '.custom_domain // empty' "$CONFIG_FILE")

log_info "Logo URL: $LOGO_URL"
log_info "Primary Color: $PRIMARY_COLOR"
log_info "Secondary Color: $SECONDARY_COLOR"
log_info "Favicon URL: $FAVICON_URL"
log_info "Custom Domain: $CUSTOM_DOMAIN"

# Validate colors
if ! [[ "$PRIMARY_COLOR" =~ ^#[0-9A-Fa-f]{6}$ ]]; then
    log_error "Invalid primary color format: $PRIMARY_COLOR"
    exit 1
fi

if ! [[ "$SECONDARY_COLOR" =~ ^#[0-9A-Fa-f]{6}$ ]]; then
    log_error "Invalid secondary color format: $SECONDARY_COLOR"
    exit 1
fi

# Get cluster and namespace
CLUSTER_NAME="cluster-${PARTNER_ID}"
NAMESPACE="partner-${PARTNER_ID}"

log_info "Updating Kubernetes ConfigMap..."

# Create or update branding ConfigMap
kubectl create configmap branding-${PARTNER_ID} \
    --from-literal=logo_url="${LOGO_URL}" \
    --from-literal=primary_color="${PRIMARY_COLOR}" \
    --from-literal=secondary_color="${SECONDARY_COLOR}" \
    --from-literal=favicon_url="${FAVICON_URL}" \
    --from-literal=custom_domain="${CUSTOM_DOMAIN}" \
    -n "${NAMESPACE}" \
    --dry-run=client -o yaml | kubectl apply -f -

log_success "Branding ConfigMap updated"

# Update environment variables in deployment
log_info "Updating deployment with branding configuration..."

kubectl set env deployment/webwaka-${PARTNER_ID} \
    BRANDING_LOGO_URL="${LOGO_URL}" \
    BRANDING_PRIMARY_COLOR="${PRIMARY_COLOR}" \
    BRANDING_SECONDARY_COLOR="${SECONDARY_COLOR}" \
    BRANDING_FAVICON_URL="${FAVICON_URL}" \
    BRANDING_CUSTOM_DOMAIN="${CUSTOM_DOMAIN}" \
    -n "${NAMESPACE}"

log_success "Deployment updated with branding configuration"

# Trigger rollout
log_info "Triggering deployment rollout..."
kubectl rollout restart deployment/webwaka-${PARTNER_ID} -n "${NAMESPACE}"
kubectl rollout status deployment/webwaka-${PARTNER_ID} -n "${NAMESPACE}"

log_success "Branding configuration completed successfully"
log_info "Changes will be visible in 1-2 minutes"
