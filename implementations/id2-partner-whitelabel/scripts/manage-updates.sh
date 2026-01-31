#!/bin/bash

################################################################################
# Partner Update Management Script
#
# This script manages updates for partner-whitelabel instances.
# Integrates with the Update Channel Policy to manage updates.
#
# Usage: ./manage-updates.sh <command> <partner-id> [options]
#
# Commands:
#   check   - Check for available updates
#   enable  - Enable auto-updates
#   disable - Disable auto-updates
#   schedule - Schedule update
#   apply   - Apply update immediately
#   status  - Get update status
#   rollback - Rollback to previous version
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

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Validate inputs
if [[ $# -lt 2 ]]; then
    log_error "Usage: $0 <command> <partner-id> [options]"
    log_error "Commands: check, enable, disable, schedule, apply, status, rollback"
    exit 1
fi

COMMAND="$1"
PARTNER_ID="$2"
NAMESPACE="partner-${PARTNER_ID}"

# Check for available updates
check_updates() {
    log_info "Checking for available updates for partner: $PARTNER_ID"

    # Get current version
    CURRENT_VERSION=$(kubectl get deployment webwaka-${PARTNER_ID} \
        -n "${NAMESPACE}" \
        -o jsonpath='{.spec.template.spec.containers[0].image}' | cut -d':' -f2)

    log_info "Current version: $CURRENT_VERSION"

    # Check update channel
    UPDATE_CHANNEL=$(kubectl get configmap update-policy-${PARTNER_ID} \
        -n "${NAMESPACE}" \
        -o jsonpath='{.data.update_channel}' 2>/dev/null || echo "stable")

    log_info "Update channel: $UPDATE_CHANNEL"

    # Simulate checking for updates
    case "$UPDATE_CHANNEL" in
        stable)
            LATEST_VERSION="1.2.0"
            ;;
        beta)
            LATEST_VERSION="1.3.0-beta.1"
            ;;
        edge)
            LATEST_VERSION="1.4.0-edge.1"
            ;;
        *)
            LATEST_VERSION="$CURRENT_VERSION"
            ;;
    esac

    if [[ "$CURRENT_VERSION" == "$LATEST_VERSION" ]]; then
        log_success "Already on latest version: $LATEST_VERSION"
    else
        log_warning "New version available: $LATEST_VERSION"
        echo "Current: $CURRENT_VERSION"
        echo "Latest: $LATEST_VERSION"
    fi
}

# Enable auto-updates
enable_auto_updates() {
    log_info "Enabling auto-updates for partner: $PARTNER_ID"

    kubectl create configmap update-policy-${PARTNER_ID} \
        --from-literal=auto_update_enabled="true" \
        -n "${NAMESPACE}" \
        --dry-run=client -o yaml | kubectl apply -f -

    log_success "Auto-updates enabled"
}

# Disable auto-updates
disable_auto_updates() {
    log_info "Disabling auto-updates for partner: $PARTNER_ID"

    kubectl create configmap update-policy-${PARTNER_ID} \
        --from-literal=auto_update_enabled="false" \
        -n "${NAMESPACE}" \
        --dry-run=client -o yaml | kubectl apply -f -

    log_success "Auto-updates disabled"
}

# Schedule update
schedule_update() {
    if [[ $# -lt 3 ]]; then
        log_error "Usage: $0 schedule <partner-id> <time> [date]"
        log_error "Example: $0 schedule partner-001 02:00 2024-02-15"
        exit 1
    fi

    SCHEDULE_TIME="$3"
    SCHEDULE_DATE="${4:-$(date +%Y-%m-%d)}"

    log_info "Scheduling update for: $SCHEDULE_DATE at $SCHEDULE_TIME UTC"

    kubectl create configmap update-policy-${PARTNER_ID} \
        --from-literal=scheduled_update="true" \
        --from-literal=scheduled_time="${SCHEDULE_TIME}" \
        --from-literal=scheduled_date="${SCHEDULE_DATE}" \
        -n "${NAMESPACE}" \
        --dry-run=client -o yaml | kubectl apply -f -

    log_success "Update scheduled for $SCHEDULE_DATE at $SCHEDULE_TIME UTC"
}

# Apply update immediately
apply_update() {
    log_info "Applying update for partner: $PARTNER_ID"

    # Get current image
    CURRENT_IMAGE=$(kubectl get deployment webwaka-${PARTNER_ID} \
        -n "${NAMESPACE}" \
        -o jsonpath='{.spec.template.spec.containers[0].image}')

    # Get update channel
    UPDATE_CHANNEL=$(kubectl get configmap update-policy-${PARTNER_ID} \
        -n "${NAMESPACE}" \
        -o jsonpath='{.data.update_channel}' 2>/dev/null || echo "stable")

    # Determine new version
    case "$UPDATE_CHANNEL" in
        stable)
            NEW_VERSION="1.2.0"
            ;;
        beta)
            NEW_VERSION="1.3.0-beta.1"
            ;;
        edge)
            NEW_VERSION="1.4.0-edge.1"
            ;;
        *)
            NEW_VERSION="1.2.0"
            ;;
    esac

    NEW_IMAGE="${CURRENT_IMAGE%:*}:${NEW_VERSION}"

    log_info "Updating image from $CURRENT_IMAGE to $NEW_IMAGE"

    # Update deployment
    kubectl set image deployment/webwaka-${PARTNER_ID} \
        webwaka="$NEW_IMAGE" \
        -n "${NAMESPACE}"

    # Wait for rollout
    log_info "Waiting for rollout to complete..."
    kubectl rollout status deployment/webwaka-${PARTNER_ID} -n "${NAMESPACE}"

    log_success "Update applied successfully"
}

# Get update status
get_update_status() {
    log_info "Getting update status for partner: $PARTNER_ID"

    # Get current version
    CURRENT_VERSION=$(kubectl get deployment webwaka-${PARTNER_ID} \
        -n "${NAMESPACE}" \
        -o jsonpath='{.spec.template.spec.containers[0].image}' | cut -d':' -f2)

    # Get auto-update status
    AUTO_UPDATE=$(kubectl get configmap update-policy-${PARTNER_ID} \
        -n "${NAMESPACE}" \
        -o jsonpath='{.data.auto_update_enabled}' 2>/dev/null || echo "false")

    # Get update channel
    UPDATE_CHANNEL=$(kubectl get configmap update-policy-${PARTNER_ID} \
        -n "${NAMESPACE}" \
        -o jsonpath='{.data.update_channel}' 2>/dev/null || echo "stable")

    # Get maintenance window
    MAINTENANCE_WINDOW=$(kubectl get configmap update-policy-${PARTNER_ID} \
        -n "${NAMESPACE}" \
        -o jsonpath='{.data.maintenance_window}' 2>/dev/null || echo "02:00-04:00 UTC")

    echo "Partner: $PARTNER_ID"
    echo "Current Version: $CURRENT_VERSION"
    echo "Auto-Updates: $AUTO_UPDATE"
    echo "Update Channel: $UPDATE_CHANNEL"
    echo "Maintenance Window: $MAINTENANCE_WINDOW"
}

# Rollback to previous version
rollback_update() {
    log_info "Rolling back to previous version for partner: $PARTNER_ID"

    # Get rollback enabled status
    ROLLBACK_ENABLED=$(kubectl get configmap update-policy-${PARTNER_ID} \
        -n "${NAMESPACE}" \
        -o jsonpath='{.data.rollback_enabled}' 2>/dev/null || echo "true")

    if [[ "$ROLLBACK_ENABLED" != "true" ]]; then
        log_error "Rollback is not enabled for this partner"
        exit 1
    fi

    # Get previous version (simulate)
    PREVIOUS_VERSION="1.1.0"

    # Get current image
    CURRENT_IMAGE=$(kubectl get deployment webwaka-${PARTNER_ID} \
        -n "${NAMESPACE}" \
        -o jsonpath='{.spec.template.spec.containers[0].image}')

    NEW_IMAGE="${CURRENT_IMAGE%:*}:${PREVIOUS_VERSION}"

    log_info "Rolling back to version: $PREVIOUS_VERSION"

    # Update deployment
    kubectl set image deployment/webwaka-${PARTNER_ID} \
        webwaka="$NEW_IMAGE" \
        -n "${NAMESPACE}"

    # Wait for rollout
    log_info "Waiting for rollout to complete..."
    kubectl rollout status deployment/webwaka-${PARTNER_ID} -n "${NAMESPACE}"

    log_success "Rollback completed successfully"
}

# Execute command
case "$COMMAND" in
    check)
        check_updates
        ;;
    enable)
        enable_auto_updates
        ;;
    disable)
        disable_auto_updates
        ;;
    schedule)
        schedule_update "$@"
        ;;
    apply)
        apply_update
        ;;
    status)
        get_update_status
        ;;
    rollback)
        rollback_update
        ;;
    *)
        log_error "Unknown command: $COMMAND"
        log_error "Available commands: check, enable, disable, schedule, apply, status, rollback"
        exit 1
        ;;
esac
