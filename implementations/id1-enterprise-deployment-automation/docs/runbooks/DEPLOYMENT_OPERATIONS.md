# Deployment Operations Runbook

## Overview

This runbook provides operational guidance for managing the Enterprise Deployment Automation system in production environments.

## Prerequisites

- Python 3.11+
- PostgreSQL database
- Docker (optional, for containerized deployments)
- Git access to the webwaka repository

## Startup Procedures

### Starting the Service

```bash
# Navigate to the implementation directory
cd /home/ubuntu/webwaka/implementations/id1-enterprise-deployment-automation

# Install dependencies
pip install -r requirements.txt

# Start the API server
python main.py
```

The API will be available at `http://localhost:8000` with documentation at `http://localhost:8000/docs`.

### Health Checks

Verify the service is running:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

## Common Operations

### Creating a Deployment

To create a new deployment:

```bash
curl -X POST http://localhost:8000/api/v1/deployments \
  -H "Content-Type: application/json" \
  -d '{
    "manifest_id": "manifest-001",
    "instance_id": "instance-prod-01",
    "dry_run": false,
    "skip_validation": false
  }'
```

### Monitoring Deployment Status

Check deployment progress:

```bash
curl http://localhost:8000/api/v1/deployments/deploy-001
```

### Setting Update Policies

Create a manual approval policy:

```bash
curl -X POST "http://localhost:8000/api/v1/policies?instance_id=instance-prod-01&policy_type=manual_approval&description=Production%20requires%20approval"
```

### Pinning Versions

Pin a suite version for compatibility:

```bash
curl -X POST "http://localhost:8000/api/v1/versions/pin?instance_id=instance-prod-01" \
  -H "Content-Type: application/json" \
  -d '{
    "component_type": "suite",
    "component_name": "commerce",
    "pinned_version": "1.5.0",
    "reason": "Compatibility with legacy system"
  }'
```

### Applying Security Patches

Apply a critical security patch:

```bash
curl -X POST "http://localhost:8000/api/v1/security/patches/apply?instance_id=instance-prod-01" \
  -H "Content-Type: application/json" \
  -d '{
    "patch_id": "patch-001",
    "dry_run": false,
    "force": false
  }'
```

### Initiating Rollback

Rollback to a previous version:

```bash
curl -X POST "http://localhost:8000/api/v1/rollback?instance_id=instance-prod-01" \
  -H "Content-Type: application/json" \
  -d '{
    "to_manifest_id": "manifest-001",
    "reason": "Deployment caused performance degradation",
    "dry_run": false,
    "skip_validation": false
  }'
```

## Troubleshooting

### Service Won't Start

**Problem:** API server fails to start

**Solution:**
1. Check Python version: `python --version`
2. Verify dependencies: `pip list`
3. Check logs for specific errors
4. Ensure port 8000 is available: `lsof -i :8000`

### Deployment Failures

**Problem:** Deployment fails with validation errors

**Solution:**
1. Check manifest validity: Verify all required fields are present
2. Check version compatibility: Use the compatibility endpoint
3. Review deployment logs: Check the deployment status endpoint
4. Verify instance connectivity: Ensure target instance is reachable

### Policy Enforcement Issues

**Problem:** Deployment blocked by policy

**Solution:**
1. Check active policy: `GET /api/v1/policies?instance_id={instance_id}`
2. Verify policy type: Ensure policy is appropriate for the deployment
3. Check maintenance windows: If auto-update, verify current time is in window
4. For manual approval policies: Obtain necessary approvals

### Version Compatibility Issues

**Problem:** Version compatibility check fails

**Solution:**
1. Check available versions: `GET /api/v1/versions`
2. Verify dependencies: Review component dependencies
3. Check version pins: `GET /api/v1/versions/pins/{instance_id}`
4. Review compatibility report: Use compatibility endpoint for details

## Maintenance Tasks

### Regular Backups

Backup the deployment database daily:

```bash
pg_dump deployment_db > deployment_db_backup_$(date +%Y%m%d).sql
```

### Log Rotation

Implement log rotation for API logs:

```bash
# Add to crontab for daily rotation
0 0 * * * logrotate /etc/logrotate.d/deployment-automation
```

### Monitoring

Set up monitoring for:
- API response times
- Deployment success rates
- Policy enforcement decisions
- Security patch application status
- Rollback operation success rates

### Performance Optimization

Monitor and optimize:
- Database query performance
- API endpoint response times
- Manifest compilation time
- Version compatibility checking

## Disaster Recovery

### Service Recovery

If the service crashes:

1. Check service status: `systemctl status deployment-automation`
2. Review logs: `journalctl -u deployment-automation -n 50`
3. Restart service: `systemctl restart deployment-automation`
4. Verify recovery: `curl http://localhost:8000/health`

### Data Recovery

In case of data loss:

1. Restore from backup: `psql deployment_db < deployment_db_backup.sql`
2. Verify data integrity: Run consistency checks
3. Restart service: `systemctl restart deployment-automation`
4. Monitor for issues: Check logs and metrics

## Security Considerations

### Access Control

- Implement authentication for all API endpoints
- Use HTTPS in production
- Restrict API access to authorized networks
- Implement rate limiting

### Audit Logging

- Log all deployment operations
- Log all policy changes
- Log all security patch applications
- Log all rollback operations
- Retain logs for compliance period

### Secret Management

- Store database credentials in environment variables
- Use secrets management system (e.g., HashiCorp Vault)
- Rotate credentials regularly
- Never commit secrets to version control

## Escalation Procedures

### Critical Issues

For critical deployment failures:

1. Immediate rollback if safe to do so
2. Notify on-call engineer
3. Begin incident investigation
4. Document root cause
5. Implement preventive measures

### Security Incidents

For security-related issues:

1. Isolate affected systems
2. Notify security team
3. Begin forensic analysis
4. Apply security patches immediately
5. Conduct post-incident review

## Contact Information

- **On-Call Engineer:** See escalation policy
- **Security Team:** security@example.com
- **Database Administrator:** dba@example.com
- **DevOps Team:** devops@example.com
