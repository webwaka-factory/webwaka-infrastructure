# Partner Whitelabel Deployment Guide

**Version:** 1.0.0  
**Date:** January 30, 2026  
**Status:** 🟢 Complete  
**Canonical Reference:** [ID-2: Partner Whitelabel Deployment](https://github.com/webwakaagent1/webwaka-governance/blob/main/docs/planning/wave4/PROMPT_ID-2_PARTNER_WHITELABEL.md)

---

## 1. Overview

The Partner Whitelabel Deployment system enables partners to deploy and manage their own branded instances of the WebWaka platform with minimal intervention from WebWaka. This guide provides comprehensive instructions for deploying, configuring, and managing partner instances.

**Key Capabilities:**
- ✅ Automated provisioning of partner infrastructure
- ✅ Custom branding configuration
- ✅ Configuration management system
- ✅ Automated update management

---

## 2. Architecture

### 2.1 System Components

```
┌─────────────────────────────────────────────┐
│     Partner Whitelabel Deployment System    │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  Provisioning System                │   │
│  │  - provision-partner.sh             │   │
│  │  - Terraform configuration          │   │
│  │  - Infrastructure setup             │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  Branding Configuration             │   │
│  │  - configure-branding.sh            │   │
│  │  - Logo, colors, domain             │   │
│  │  - Custom styling                   │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  Configuration Management           │   │
│  │  - manage-config.sh                 │   │
│  │  - Get, set, validate               │   │
│  │  - Backup, restore                  │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  Update Management                  │   │
│  │  - manage-updates.sh                │   │
│  │  - Check, apply, rollback           │   │
│  │  - Schedule updates                 │   │
│  └─────────────────────────────────────┘   │
│                                             │
└─────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────┐
│     Infrastructure Layer (AWS)              │
│  - EKS Cluster                              │
│  - RDS Database                             │
│  - S3 Storage                               │
│  - VPC & Networking                         │
└─────────────────────────────────────────────┘
```

### 2.2 Infrastructure Components

**Kubernetes (EKS):**
- EKS cluster for application deployment
- Auto-scaling node groups
- Network policies and security groups

**Database (RDS):**
- Aurora PostgreSQL for data storage
- Automated backups
- Multi-AZ deployment for production

**Storage (S3):**
- S3 bucket for partner data
- Versioning enabled
- Server-side encryption

**Networking:**
- VPC with public and private subnets
- Internet gateway for external access
- NAT gateway for private subnet egress

---

## 3. Prerequisites

### 3.1 Required Tools

```bash
# AWS CLI
aws --version  # >= 2.0

# Terraform
terraform --version  # >= 1.0

# Kubernetes CLI
kubectl version --client  # >= 1.27

# Docker
docker --version  # >= 20.0

# jq (JSON processor)
jq --version  # >= 1.6
```

### 3.2 AWS Credentials

```bash
# Configure AWS credentials
aws configure

# Verify credentials
aws sts get-caller-identity
```

### 3.3 IAM Permissions

Required IAM permissions:
- EKS cluster creation and management
- RDS database creation and management
- S3 bucket creation and management
- VPC and networking resources
- IAM role creation

---

## 4. Deploying a Partner Instance

### 4.1 Quick Start

```bash
# Navigate to the deployment directory
cd implementations/id2-partner-whitelabel

# Make scripts executable
chmod +x scripts/*.sh

# Provision a new partner instance
./scripts/provision-partner.sh partner-001 "Acme Corp" production
```

### 4.2 Step-by-Step Deployment

#### Step 1: Prepare Configuration

```bash
# Create partner configuration
PARTNER_ID="partner-001"
PARTNER_NAME="Acme Corp"
ENVIRONMENT="production"
```

#### Step 2: Run Provisioning Script

```bash
./scripts/provision-partner.sh $PARTNER_ID "$PARTNER_NAME" $ENVIRONMENT
```

The provisioning script will:
1. Validate inputs
2. Check prerequisites
3. Create partner configuration
4. Provision infrastructure with Terraform
5. Deploy application to Kubernetes
6. Configure update management
7. Update partner status
8. Generate deployment report

#### Step 3: Verify Deployment

```bash
# Check cluster status
aws eks describe-cluster --name cluster-${PARTNER_ID}

# Check deployment status
kubectl get deployment -n partner-${PARTNER_ID}

# Check services
kubectl get services -n partner-${PARTNER_ID}
```

#### Step 4: Access Partner Instance

```bash
# Get load balancer endpoint
kubectl get service webwaka-${PARTNER_ID} \
    -n partner-${PARTNER_ID} \
    -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

---

## 5. Custom Branding

### 5.1 Branding Configuration

Create a branding configuration file:

```json
{
  "logo_url": "https://example.com/logo.png",
  "primary_color": "#0066CC",
  "secondary_color": "#333333",
  "favicon_url": "https://example.com/favicon.ico",
  "custom_domain": "platform.acmecorp.com"
}
```

### 5.2 Applying Branding

```bash
# Apply branding configuration
./scripts/configure-branding.sh partner-001 branding.json
```

The script will:
1. Validate color formats
2. Update Kubernetes ConfigMap
3. Update deployment environment variables
4. Trigger deployment rollout

### 5.3 Branding Elements

| Element | Description | Format |
|---------|-------------|--------|
| **Logo** | Company logo | URL to image (PNG, SVG) |
| **Primary Color** | Main brand color | Hex color code (#RRGGBB) |
| **Secondary Color** | Accent color | Hex color code (#RRGGBB) |
| **Favicon** | Browser tab icon | URL to favicon.ico |
| **Custom Domain** | Partner's domain | CNAME to webwaka domain |

---

## 6. Configuration Management

### 6.1 Get Configuration

```bash
# Retrieve current configuration
./scripts/manage-config.sh get partner-001
```

### 6.2 Set Configuration

```bash
# Set a configuration value
./scripts/manage-config.sh set partner-001 features.mlas_enabled true
```

### 6.3 List Configurations

```bash
# List all configurations for a partner
./scripts/manage-config.sh list partner-001
```

### 6.4 Validate Configuration

```bash
# Validate partner configuration
./scripts/manage-config.sh validate partner-001
```

### 6.5 Backup Configuration

```bash
# Backup configuration
./scripts/manage-config.sh backup partner-001
```

### 6.6 Restore Configuration

```bash
# Restore from backup
./scripts/manage-config.sh restore partner-001 backups/partner-001/config-20240130-120000.json
```

---

## 7. Update Management

### 7.1 Check for Updates

```bash
# Check available updates
./scripts/manage-updates.sh check partner-001
```

### 7.2 Enable/Disable Auto-Updates

```bash
# Enable auto-updates
./scripts/manage-updates.sh enable partner-001

# Disable auto-updates
./scripts/manage-updates.sh disable partner-001
```

### 7.3 Schedule Updates

```bash
# Schedule update for specific date and time
./scripts/manage-updates.sh schedule partner-001 02:00 2024-02-15
```

### 7.4 Apply Updates

```bash
# Apply update immediately
./scripts/manage-updates.sh apply partner-001
```

### 7.5 Update Status

```bash
# Get update status
./scripts/manage-updates.sh status partner-001
```

### 7.6 Rollback Updates

```bash
# Rollback to previous version
./scripts/manage-updates.sh rollback partner-001
```

---

## 8. Update Channel Policy

The system supports three update channels:

| Channel | Description | Use Case |
|---------|-------------|----------|
| **stable** | Latest stable release | Production environments |
| **beta** | Pre-release versions | Staging environments |
| **edge** | Development versions | Development environments |

### 8.1 Setting Update Channel

```bash
# Set update channel
./scripts/manage-config.sh set partner-001 update_channel stable
```

### 8.2 Maintenance Windows

```bash
# Set maintenance window (UTC)
./scripts/manage-config.sh set partner-001 maintenance_window "02:00-04:00 UTC"
```

---

## 9. Monitoring and Troubleshooting

### 9.1 Check Deployment Status

```bash
# Check deployment status
kubectl get deployment webwaka-partner-001 -n partner-partner-001

# Check pod status
kubectl get pods -n partner-partner-001

# Check services
kubectl get services -n partner-partner-001
```

### 9.2 View Logs

```bash
# View deployment logs
kubectl logs deployment/webwaka-partner-001 -n partner-partner-001

# View logs from specific pod
kubectl logs pod-name -n partner-partner-001

# Stream logs in real-time
kubectl logs -f deployment/webwaka-partner-001 -n partner-partner-001
```

### 9.3 Describe Resources

```bash
# Describe deployment
kubectl describe deployment webwaka-partner-001 -n partner-partner-001

# Describe service
kubectl describe service webwaka-partner-001 -n partner-partner-001
```

### 9.4 Common Issues

**Issue: Pod not starting**
```bash
# Check pod events
kubectl describe pod pod-name -n partner-partner-001

# Check resource limits
kubectl top pod -n partner-partner-001
```

**Issue: Database connection failed**
```bash
# Verify database endpoint
aws rds describe-db-clusters --query 'DBClusters[?DBClusterIdentifier==`db-partner-001`]'

# Check security groups
aws ec2 describe-security-groups --filters Name=group-id,Values=sg-xxx
```

**Issue: Update failed**
```bash
# Check rollout status
kubectl rollout status deployment/webwaka-partner-001 -n partner-partner-001

# Rollback if needed
./scripts/manage-updates.sh rollback partner-001
```

---

## 10. Governance Compliance

### 10.1 INV-005: Partner-Led Operating Model

**Principle:** Partners have autonomy to manage their own instances.

**Implementation:**
- Partners can configure their own branding
- Partners can manage their own settings
- Partners have access to deployment reports
- Partners can schedule their own updates

### 10.2 INV-008: Update Policy as Governed Lifecycle

**Principle:** Updates follow a governed lifecycle with configurable policies.

**Implementation:**
- Update channels (stable, beta, edge)
- Maintenance windows
- Auto-update policies
- Rollback capabilities
- Notification system

### 10.3 INV-012v2: Multi-Repository Topology

**Principle:** All work is in the `webwaka-infrastructure` repository.

**Implementation:**
- All scripts in `/implementations/id2-partner-whitelabel/scripts/`
- All Terraform in `/implementations/id2-partner-whitelabel/terraform/`
- All configuration in `/implementations/id2-partner-whitelabel/config/`
- All documentation in `/implementations/id2-partner-whitelabel/docs/`

---

## 11. Security Best Practices

### 11.1 Access Control

```bash
# Limit access to partner namespace
kubectl create rolebinding partner-admin \
    --clusterrole=admin \
    --serviceaccount=partner-partner-001:default \
    -n partner-partner-001
```

### 11.2 Network Security

- VPC isolation per partner
- Security groups restrict access
- Network policies enforce communication rules
- TLS encryption for all traffic

### 11.3 Data Protection

- Encrypted storage at rest
- Encrypted data in transit
- Regular backups
- Disaster recovery procedures

### 11.4 Audit Logging

```bash
# Enable audit logging
kubectl logs -n kube-system -l component=kube-apiserver
```

---

## 12. Scaling and Performance

### 12.1 Auto-Scaling

```bash
# View auto-scaling configuration
kubectl get hpa -n partner-partner-001

# Create auto-scaling policy
kubectl autoscale deployment webwaka-partner-001 \
    --min=2 --max=10 \
    -n partner-partner-001
```

### 12.2 Resource Limits

```bash
# Check resource usage
kubectl top nodes
kubectl top pods -n partner-partner-001
```

### 12.3 Performance Optimization

- Enable caching
- Optimize database queries
- Use CDN for static assets
- Monitor and adjust resource limits

---

## 13. Disaster Recovery

### 13.1 Backup Strategy

```bash
# Backup database
aws rds create-db-snapshot \
    --db-cluster-identifier db-partner-001 \
    --db-cluster-snapshot-identifier db-partner-001-backup-$(date +%Y%m%d)
```

### 13.2 Restore Procedure

```bash
# Restore from snapshot
aws rds restore-db-cluster-from-snapshot \
    --db-cluster-identifier db-partner-001-restored \
    --snapshot-identifier db-partner-001-backup-20240130
```

### 13.3 Failover

```bash
# Trigger failover (for multi-AZ setup)
aws rds failover-db-cluster \
    --db-cluster-identifier db-partner-001
```

---

## 14. Maintenance

### 14.1 Regular Tasks

- Monitor resource usage
- Review logs and alerts
- Update security patches
- Test disaster recovery procedures
- Review and optimize costs

### 14.2 Scheduled Maintenance

```bash
# Schedule maintenance window
./scripts/manage-config.sh set partner-001 maintenance_window "02:00-04:00 UTC"
```

---

## 15. Support and Escalation

### 15.1 Troubleshooting Resources

- Check deployment logs
- Review Kubernetes events
- Verify AWS resources
- Consult documentation

### 15.2 Escalation Path

1. Check logs and events
2. Review configuration
3. Consult documentation
4. Contact WebWaka support

---

## 16. References

- [ID-2: Partner Whitelabel Deployment](https://github.com/webwakaagent1/webwaka-governance/blob/main/docs/planning/wave4/PROMPT_ID-2_PARTNER_WHITELABEL.md)
- [Terraform Documentation](https://www.terraform.io/docs)
- [Kubernetes Documentation](https://kubernetes.io/docs)
- [AWS EKS Documentation](https://docs.aws.amazon.com/eks)

---

**Document Version:** 1.0.0  
**Last Updated:** January 30, 2026  
**Status:** 🟢 Complete

---

**End of Partner Deployment Guide**
