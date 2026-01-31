#!/bin/bash

################################################################################
# Partner Whitelabel Instance Provisioning Script
#
# This script automates the deployment of a new partner-whitelabel instance
# of the WebWaka platform.
#
# Usage: ./provision-partner.sh <partner-id> <partner-name> [environment]
#
# Example: ./provision-partner.sh partner-001 "Acme Corp" production
################################################################################

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
TERRAFORM_DIR="${PROJECT_ROOT}/terraform"
CONFIG_DIR="${PROJECT_ROOT}/config"
ENVIRONMENT="${3:-staging}"

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
validate_inputs() {
    if [[ $# -lt 2 ]]; then
        log_error "Usage: $0 <partner-id> <partner-name> [environment]"
        exit 1
    fi

    PARTNER_ID="$1"
    PARTNER_NAME="$2"

    # Validate partner ID format (alphanumeric with hyphens)
    if ! [[ "$PARTNER_ID" =~ ^[a-z0-9-]+$ ]]; then
        log_error "Partner ID must contain only lowercase letters, numbers, and hyphens"
        exit 1
    fi

    # Validate environment
    if ! [[ "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
        log_error "Environment must be one of: development, staging, production"
        exit 1
    fi

    log_info "Partner ID: $PARTNER_ID"
    log_info "Partner Name: $PARTNER_NAME"
    log_info "Environment: $ENVIRONMENT"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check for required tools
    local required_tools=("terraform" "kubectl" "docker" "jq" "aws")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "Required tool not found: $tool"
            exit 1
        fi
    done

    log_success "All prerequisites met"
}

# Create partner configuration
create_partner_config() {
    log_info "Creating partner configuration..."

    local config_file="${CONFIG_DIR}/partners/${PARTNER_ID}.json"
    mkdir -p "$(dirname "$config_file")"

    cat > "$config_file" << EOF
{
  "partner_id": "${PARTNER_ID}",
  "partner_name": "${PARTNER_NAME}",
  "environment": "${ENVIRONMENT}",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "status": "provisioning",
  "branding": {
    "logo_url": "",
    "primary_color": "#0066CC",
    "secondary_color": "#333333",
    "favicon_url": "",
    "custom_domain": ""
  },
  "infrastructure": {
    "region": "us-east-1",
    "instance_type": "t3.medium",
    "database_size": "db.t3.small",
    "storage_size": 100
  },
  "features": {
    "mlas_enabled": true,
    "custom_branding": true,
    "api_access": true,
    "white_label": true
  },
  "update_channel": "stable"
}
EOF

    log_success "Partner configuration created: $config_file"
}

# Provision infrastructure with Terraform
provision_infrastructure() {
    log_info "Provisioning infrastructure with Terraform..."

    cd "$TERRAFORM_DIR"

    # Initialize Terraform
    log_info "Initializing Terraform..."
    terraform init -upgrade

    # Create Terraform variables
    log_info "Creating Terraform variables..."
    cat > "terraform.tfvars" << EOF
partner_id = "${PARTNER_ID}"
partner_name = "${PARTNER_NAME}"
environment = "${ENVIRONMENT}"
EOF

    # Plan Terraform deployment
    log_info "Planning Terraform deployment..."
    terraform plan -out=tfplan

    # Apply Terraform deployment
    log_info "Applying Terraform deployment..."
    terraform apply tfplan

    # Get outputs
    CLUSTER_NAME=$(terraform output -raw cluster_name)
    NAMESPACE=$(terraform output -raw namespace)
    DATABASE_ENDPOINT=$(terraform output -raw database_endpoint)

    log_success "Infrastructure provisioned successfully"
    log_info "Cluster: $CLUSTER_NAME"
    log_info "Namespace: $NAMESPACE"
    log_info "Database: $DATABASE_ENDPOINT"

    cd - > /dev/null
}

# Deploy application
deploy_application() {
    log_info "Deploying application..."

    # Configure kubectl context
    log_info "Configuring kubectl context..."
    aws eks update-kubeconfig --name "$CLUSTER_NAME" --region us-east-1

    # Create namespace
    log_info "Creating Kubernetes namespace..."
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

    # Create secrets
    log_info "Creating secrets..."
    kubectl create secret generic partner-config \
        --from-file="${CONFIG_DIR}/partners/${PARTNER_ID}.json" \
        -n "$NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -

    # Deploy application
    log_info "Deploying application to Kubernetes..."
    kubectl apply -f - << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webwaka-${PARTNER_ID}
  namespace: ${NAMESPACE}
  labels:
    app: webwaka
    partner: ${PARTNER_ID}
spec:
  replicas: 2
  selector:
    matchLabels:
      app: webwaka
      partner: ${PARTNER_ID}
  template:
    metadata:
      labels:
        app: webwaka
        partner: ${PARTNER_ID}
    spec:
      containers:
      - name: webwaka
        image: webwaka:latest
        ports:
        - containerPort: 3000
        env:
        - name: PARTNER_ID
          value: "${PARTNER_ID}"
        - name: DATABASE_URL
          value: "postgresql://user:pass@${DATABASE_ENDPOINT}:5432/${PARTNER_ID}"
        - name: ENVIRONMENT
          value: "${ENVIRONMENT}"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: webwaka-${PARTNER_ID}
  namespace: ${NAMESPACE}
spec:
  selector:
    app: webwaka
    partner: ${PARTNER_ID}
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer
EOF

    log_success "Application deployed successfully"
}

# Configure update management
configure_update_management() {
    log_info "Configuring update management..."

    # Create update policy
    kubectl apply -f - << EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: update-policy-${PARTNER_ID}
  namespace: ${NAMESPACE}
data:
  update_channel: "stable"
  auto_update_enabled: "true"
  maintenance_window: "02:00-04:00 UTC"
  rollback_enabled: "true"
  notification_email: "admin@partner.com"
EOF

    log_success "Update management configured"
}

# Update partner status
update_partner_status() {
    log_info "Updating partner status..."

    local config_file="${CONFIG_DIR}/partners/${PARTNER_ID}.json"
    local temp_file="${config_file}.tmp"

    jq '.status = "active" | .infrastructure.cluster_name = "'${CLUSTER_NAME}'" | .infrastructure.namespace = "'${NAMESPACE}'"' "$config_file" > "$temp_file"
    mv "$temp_file" "$config_file"

    log_success "Partner status updated to active"
}

# Generate deployment report
generate_deployment_report() {
    log_info "Generating deployment report..."

    local report_file="${CONFIG_DIR}/partners/${PARTNER_ID}-deployment-report.json"

    cat > "$report_file" << EOF
{
  "partner_id": "${PARTNER_ID}",
  "partner_name": "${PARTNER_NAME}",
  "environment": "${ENVIRONMENT}",
  "deployment_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "status": "success",
  "infrastructure": {
    "cluster_name": "${CLUSTER_NAME}",
    "namespace": "${NAMESPACE}",
    "database_endpoint": "${DATABASE_ENDPOINT}",
    "region": "us-east-1"
  },
  "access_information": {
    "api_endpoint": "https://api-${PARTNER_ID}.webwaka.io",
    "dashboard_url": "https://${PARTNER_ID}.webwaka.io",
    "documentation": "https://docs.webwaka.io/partners/${PARTNER_ID}"
  },
  "next_steps": [
    "Configure custom branding in dashboard",
    "Set up custom domain (CNAME: ${PARTNER_ID}.webwaka.io)",
    "Configure API credentials",
    "Enable required features",
    "Set up monitoring and alerts"
  ]
}
EOF

    log_success "Deployment report generated: $report_file"
}

# Main execution
main() {
    log_info "Starting Partner Whitelabel Instance Provisioning"
    log_info "=================================================="

    validate_inputs "$@"
    check_prerequisites
    create_partner_config
    provision_infrastructure
    deploy_application
    configure_update_management
    update_partner_status
    generate_deployment_report

    log_success "Partner whitelabel instance provisioning completed successfully!"
    log_info "=================================================="
    log_info "Partner ID: $PARTNER_ID"
    log_info "Partner Name: $PARTNER_NAME"
    log_info "Environment: $ENVIRONMENT"
    log_info "Deployment Report: ${CONFIG_DIR}/partners/${PARTNER_ID}-deployment-report.json"
}

main "$@"
