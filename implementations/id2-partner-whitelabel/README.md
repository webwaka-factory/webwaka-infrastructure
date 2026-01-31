# ID-2: Partner Whitelabel Deployment

**Version:** 1.0.0  
**Status:** 🟢 Complete  
**Canonical Reference:** [ID-2: Partner Whitelabel Deployment](https://github.com/webwakaagent1/webwaka-governance/blob/main/docs/planning/wave4/PROMPT_ID-2_PARTNER_WHITELABEL.md)

## Overview

The ID-2 Partner Whitelabel Deployment system automates the deployment pipeline for partner-whitelabel instances of the WebWaka platform. This enables partners to deploy and manage their own branded instances with minimal intervention from WebWaka.

**Key Capabilities:**
- ✅ **Automated Provisioning** - Automatically provision infrastructure for new partner instances
- ✅ **Custom Branding** - Partners can customize logos, colors, and domains
- ✅ **Configuration Management** - Manage partner instance configurations
- ✅ **Update Management** - Automated update management with rollback support

## Quick Start

### Prerequisites

```bash
# Required tools
aws --version        # >= 2.0
terraform --version  # >= 1.0
kubectl version      # >= 1.27
docker --version     # >= 20.0
jq --version         # >= 1.6
```

### Installation

```bash
# Clone the repository
cd webwaka-infrastructure/implementations/id2-partner-whitelabel

# Make scripts executable
chmod +x scripts/*.sh

# Configure AWS credentials
aws configure
```

### Deploy a Partner Instance

```bash
# Provision a new partner instance
./scripts/provision-partner.sh partner-001 "Acme Corp" production

# Configure branding
./scripts/configure-branding.sh partner-001 branding.json

# Check update status
./scripts/manage-updates.sh status partner-001
```

## Components

### 1. Provisioning System (`scripts/provision-partner.sh`)

Automates the complete deployment of a new partner instance:
- Validates inputs
- Creates partner configuration
- Provisions infrastructure with Terraform
- Deploys application to Kubernetes
- Configures update management
- Generates deployment report

**Usage:**
```bash
./scripts/provision-partner.sh <partner-id> <partner-name> [environment]
```

### 2. Branding Configuration (`scripts/configure-branding.sh`)

Manages custom branding for partner instances:
- Logo URL
- Primary and secondary colors
- Favicon
- Custom domain

**Usage:**
```bash
./scripts/configure-branding.sh <partner-id> <config-file>
```

### 3. Configuration Management (`scripts/manage-config.sh`)

Manages partner instance configurations:
- Get current configuration
- Set configuration values
- Validate configuration
- Backup and restore configurations

**Usage:**
```bash
./scripts/manage-config.sh <command> <partner-id> [options]
```

**Commands:**
- `get` - Get current configuration
- `set` - Set configuration value
- `list` - List all configurations
- `validate` - Validate configuration
- `backup` - Backup configuration
- `restore` - Restore from backup

### 4. Update Management (`scripts/manage-updates.sh`)

Manages updates for partner instances:
- Check for available updates
- Enable/disable auto-updates
- Schedule updates
- Apply updates immediately
- Rollback to previous version

**Usage:**
```bash
./scripts/manage-updates.sh <command> <partner-id> [options]
```

**Commands:**
- `check` - Check for available updates
- `enable` - Enable auto-updates
- `disable` - Disable auto-updates
- `schedule` - Schedule update
- `apply` - Apply update immediately
- `status` - Get update status
- `rollback` - Rollback to previous version

## Infrastructure

### Terraform Configuration (`terraform/main.tf`)

Provisions the following AWS resources:
- **VPC** - Virtual private cloud with public and private subnets
- **EKS Cluster** - Kubernetes cluster for application deployment
- **RDS Database** - Aurora PostgreSQL for data storage
- **S3 Storage** - S3 bucket for partner data
- **Security Groups** - Network security policies
- **IAM Roles** - Access control and permissions

**Features:**
- Multi-AZ deployment for production
- Auto-scaling node groups
- Automated backups
- Encryption at rest and in transit

## Configuration

### Partner Configuration

Each partner has a configuration file at `config/partners/{partner-id}.json`:

```json
{
  "partner_id": "partner-001",
  "partner_name": "Acme Corp",
  "environment": "production",
  "status": "active",
  "branding": {
    "logo_url": "https://example.com/logo.png",
    "primary_color": "#0066CC",
    "secondary_color": "#333333",
    "favicon_url": "https://example.com/favicon.ico",
    "custom_domain": "platform.acmecorp.com"
  },
  "infrastructure": {
    "cluster_name": "cluster-partner-001",
    "namespace": "partner-partner-001",
    "database_endpoint": "db-partner-001.cluster-xxx.us-east-1.rds.amazonaws.com",
    "region": "us-east-1"
  },
  "features": {
    "mlas_enabled": true,
    "custom_branding": true,
    "api_access": true,
    "white_label": true
  },
  "update_channel": "stable"
}
```

### Update Channels

| Channel | Description | Use Case |
|---------|-------------|----------|
| **stable** | Latest stable release | Production |
| **beta** | Pre-release versions | Staging |
| **edge** | Development versions | Development |

## Deployment Workflow

```
1. Validate Inputs
   ↓
2. Check Prerequisites
   ↓
3. Create Partner Configuration
   ↓
4. Provision Infrastructure (Terraform)
   ├─ VPC & Networking
   ├─ EKS Cluster
   ├─ RDS Database
   └─ S3 Storage
   ↓
5. Deploy Application
   ├─ Create Namespace
   ├─ Create Secrets
   └─ Deploy Pods
   ↓
6. Configure Update Management
   ↓
7. Update Partner Status
   ↓
8. Generate Deployment Report
```

## Governance Compliance

### INV-005: Partner-Led Operating Model
- Partners can configure their own branding
- Partners can manage their own settings
- Partners have access to deployment reports
- Partners can schedule their own updates

### INV-008: Update Policy as Governed Lifecycle
- Update channels (stable, beta, edge)
- Maintenance windows
- Auto-update policies
- Rollback capabilities

### INV-012v2: Multi-Repository Topology
- All code in `/implementations/id2-partner-whitelabel/`
- All Terraform in `/terraform/`
- All scripts in `/scripts/`
- All documentation in `/docs/`

## Documentation

- **[Partner Deployment Guide](./docs/PARTNER_DEPLOYMENT_GUIDE.md)** - Comprehensive deployment and management guide
- **[Architecture Document](./docs/ARCH_ID2_PARTNER_WHITELABEL.md)** - Detailed architecture and design
- **[Terraform Configuration](./terraform/main.tf)** - Infrastructure as code

## File Structure

```
id2-partner-whitelabel/
├── README.md                              # This file
├── scripts/
│   ├── provision-partner.sh               # Provisioning script
│   ├── configure-branding.sh              # Branding configuration
│   ├── manage-config.sh                   # Configuration management
│   └── manage-updates.sh                  # Update management
├── terraform/
│   └── main.tf                            # Terraform configuration
├── config/
│   └── partners/                          # Partner configurations
├── docs/
│   ├── PARTNER_DEPLOYMENT_GUIDE.md        # Deployment guide
│   └── ARCH_ID2_PARTNER_WHITELABEL.md     # Architecture document
└── tests/
    └── (test files)
```

## Common Tasks

### Deploy a New Partner

```bash
./scripts/provision-partner.sh partner-001 "Acme Corp" production
```

### Configure Custom Branding

```bash
./scripts/configure-branding.sh partner-001 branding.json
```

### Check Update Status

```bash
./scripts/manage-updates.sh status partner-001
```

### Apply an Update

```bash
./scripts/manage-updates.sh apply partner-001
```

### Rollback an Update

```bash
./scripts/manage-updates.sh rollback partner-001
```

### Backup Configuration

```bash
./scripts/manage-config.sh backup partner-001
```

## Troubleshooting

### Check Deployment Status

```bash
# Check cluster status
aws eks describe-cluster --name cluster-partner-001

# Check deployment
kubectl get deployment -n partner-partner-001

# View logs
kubectl logs deployment/webwaka-partner-001 -n partner-partner-001
```

### Common Issues

**Provisioning fails:**
- Verify AWS credentials: `aws sts get-caller-identity`
- Check IAM permissions
- Review Terraform logs: `terraform show`

**Deployment not starting:**
- Check pod status: `kubectl describe pod <pod-name> -n partner-partner-001`
- Check resource limits: `kubectl top pods -n partner-partner-001`
- Review logs: `kubectl logs <pod-name> -n partner-partner-001`

**Update fails:**
- Check rollout status: `kubectl rollout status deployment/webwaka-partner-001 -n partner-partner-001`
- Rollback if needed: `./scripts/manage-updates.sh rollback partner-001`

## Support

For issues or questions:
1. Check the [Partner Deployment Guide](./docs/PARTNER_DEPLOYMENT_GUIDE.md)
2. Review logs and events
3. Consult the [Architecture Document](./docs/ARCH_ID2_PARTNER_WHITELABEL.md)

## License

PROPRIETARY - All rights reserved by WebWaka

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-30 | Initial implementation |

---

**For detailed information, see the [Partner Deployment Guide](./docs/PARTNER_DEPLOYMENT_GUIDE.md)**
