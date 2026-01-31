#!/bin/bash

################################################################################
# Partner Configuration Management Script
#
# This script manages configuration for partner-whitelabel instances.
#
# Usage: ./manage-config.sh <command> <partner-id> [options]
#
# Commands:
#   get     - Get current configuration
#   set     - Set configuration value
#   list    - List all configurations
#   validate - Validate configuration
#   backup  - Backup configuration
#   restore - Restore configuration from backup
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
    log_error "Usage: $0 <command> <partner-id> [options]"
    log_error "Commands: get, set, list, validate, backup, restore"
    exit 1
fi

COMMAND="$1"
PARTNER_ID="$2"
NAMESPACE="partner-${PARTNER_ID}"

# Get configuration from ConfigMap
get_config() {
    log_info "Retrieving configuration for partner: $PARTNER_ID"
    
    kubectl get configmap partner-config-${PARTNER_ID} \
        -n "${NAMESPACE}" \
        -o jsonpath='{.data.config}' 2>/dev/null || {
        log_error "Configuration not found for partner: $PARTNER_ID"
        exit 1
    }
}

# Set configuration value
set_config() {
    if [[ $# -lt 4 ]]; then
        log_error "Usage: $0 set <partner-id> <key> <value>"
        exit 1
    fi

    KEY="$3"
    VALUE="$4"

    log_info "Setting configuration: $KEY = $VALUE"

    # Get current config
    CURRENT_CONFIG=$(get_config)

    # Update config with new value
    UPDATED_CONFIG=$(echo "$CURRENT_CONFIG" | jq ".${KEY} = \"${VALUE}\"")

    # Update ConfigMap
    kubectl create configmap partner-config-${PARTNER_ID} \
        --from-literal=config="$UPDATED_CONFIG" \
        -n "${NAMESPACE}" \
        --dry-run=client -o yaml | kubectl apply -f -

    log_success "Configuration updated successfully"

    # Trigger deployment restart
    kubectl rollout restart deployment/webwaka-${PARTNER_ID} -n "${NAMESPACE}"
}

# List all configurations
list_configs() {
    log_info "Listing all partner configurations..."

    kubectl get configmap \
        -n "${NAMESPACE}" \
        -l partner="${PARTNER_ID}" \
        -o wide
}

# Validate configuration
validate_config() {
    log_info "Validating configuration for partner: $PARTNER_ID"

    CONFIG=$(get_config)

    # Check required fields
    REQUIRED_FIELDS=("partner_id" "environment" "features")
    for field in "${REQUIRED_FIELDS[@]}"; do
        if ! echo "$CONFIG" | jq -e ".${field}" > /dev/null 2>&1; then
            log_error "Missing required field: $field"
            exit 1
        fi
    done

    # Validate environment
    ENV=$(echo "$CONFIG" | jq -r '.environment')
    if ! [[ "$ENV" =~ ^(development|staging|production)$ ]]; then
        log_error "Invalid environment: $ENV"
        exit 1
    fi

    log_success "Configuration is valid"
}

# Backup configuration
backup_config() {
    log_info "Backing up configuration for partner: $PARTNER_ID"

    BACKUP_DIR="./backups/${PARTNER_ID}"
    mkdir -p "$BACKUP_DIR"

    BACKUP_FILE="${BACKUP_DIR}/config-$(date +%Y%m%d-%H%M%S).json"

    CONFIG=$(get_config)
    echo "$CONFIG" | jq '.' > "$BACKUP_FILE"

    log_success "Configuration backed up to: $BACKUP_FILE"
}

# Restore configuration from backup
restore_config() {
    if [[ $# -lt 3 ]]; then
        log_error "Usage: $0 restore <partner-id> <backup-file>"
        exit 1
    fi

    BACKUP_FILE="$3"

    if [[ ! -f "$BACKUP_FILE" ]]; then
        log_error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi

    log_info "Restoring configuration from: $BACKUP_FILE"

    CONFIG=$(cat "$BACKUP_FILE")

    # Update ConfigMap
    kubectl create configmap partner-config-${PARTNER_ID} \
        --from-literal=config="$CONFIG" \
        -n "${NAMESPACE}" \
        --dry-run=client -o yaml | kubectl apply -f -

    log_success "Configuration restored successfully"

    # Trigger deployment restart
    kubectl rollout restart deployment/webwaka-${PARTNER_ID} -n "${NAMESPACE}"
}

# Execute command
case "$COMMAND" in
    get)
        get_config
        ;;
    set)
        set_config "$@"
        ;;
    list)
        list_configs
        ;;
    validate)
        validate_config
        ;;
    backup)
        backup_config
        ;;
    restore)
        restore_config "$@"
        ;;
    *)
        log_error "Unknown command: $COMMAND"
        log_error "Available commands: get, set, list, validate, backup, restore"
        exit 1
        ;;
esac
