# Global Expansion & Multi-Region Operations Runbook

## Overview

This runbook provides operational guidance for managing the Global Expansion & Multi-Region system in production environments.

## Prerequisites

- Python 3.11+
- AWS CLI configured with credentials
- PostgreSQL database
- Docker (optional, for containerized deployments)

## Startup Procedures

### Starting the Service

```bash
# Navigate to the implementation directory
cd /home/ubuntu/webwaka/implementations/id3-global-expansion-multi-region

# Install dependencies
pip install -r requirements.txt

# Start the API server
python -m src.api.server
```

The API will be available at `http://localhost:8000` with documentation at `http://localhost:8000/docs`.

### Health Checks

Verify the service is running:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy", "service": "Global Expansion & Multi-Region API", "version": "1.0.0"}
```

## Common Operations

### Registering a New Region

To register a new AWS region:

```bash
curl -X POST http://localhost:8000/api/v1/regions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "EU West (Ireland)",
    "aws_region": "eu-west-1",
    "country_code": "IE",
    "data_center_location": "Dublin, Ireland",
    "availability_zones": ["eu-west-1a", "eu-west-1b", "eu-west-1c"]
  }'
```

### Creating a Residency Policy

Create a data residency policy for EU compliance:

```bash
curl -X POST http://localhost:8000/api/v1/residency/policies \
  -H "Content-Type: application/json" \
  -d '{
    "name": "GDPR Compliance Policy",
    "residency_mode": "regional",
    "policy_type": "mandatory",
    "allowed_regions": ["eu-west-1", "eu-central-1"]
  }'
```

### Classifying Data

Classify user data as identity data:

```bash
curl -X POST http://localhost:8000/api/v1/data/classify \
  -H "Content-Type: application/json" \
  -d '{
    "data_id": "user-profile-12345",
    "classification_level": "identity",
    "data_type": "user_profile",
    "sensitivity": "high",
    "pii_present": true,
    "encryption_required": true
  }'
```

### Requesting Cross-Border Access

Request access to data in another region:

```bash
curl -X POST http://localhost:8000/api/v1/access/request \
  -H "Content-Type: application/json" \
  -d '{
    "data_id": "data-456",
    "target_region": "eu-west-1",
    "access_type": "read",
    "reason": "Customer support investigation"
  }'
```

### Approving Access Requests

Approve a pending access request:

```bash
curl -X POST http://localhost:8000/api/v1/access/approve \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "access-req-001",
    "approved": true,
    "reason": "Approved for customer support"
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

### Region Registration Fails

**Problem:** Cannot register a new region

**Solution:**
1. Verify AWS credentials are configured
2. Check AWS region code is valid
3. Verify availability zones exist in the region
4. Check network connectivity to AWS

### Policy Enforcement Issues

**Problem:** Data residency policy not being enforced

**Solution:**
1. Verify policy is enabled
2. Check target region is in allowed regions
3. Review policy configuration
4. Check audit logs for enforcement decisions

### Access Control Issues

**Problem:** Cross-border access request rejected

**Solution:**
1. Verify access request is approved
2. Check access grant hasn't expired
3. Verify user has valid grant
4. Review audit logs for access decisions

## Maintenance Tasks

### Regular Backups

Backup the multi-region database daily:

```bash
pg_dump multi_region_db > multi_region_db_backup_$(date +%Y%m%d).sql
```

### Log Rotation

Implement log rotation for API logs:

```bash
# Add to crontab for daily rotation
0 0 * * * logrotate /etc/logrotate.d/multi-region
```

### Monitoring

Set up monitoring for:
- API response times
- Region health status
- Policy enforcement decisions
- Access request approval rates
- Audit log volume

### Performance Optimization

Monitor and optimize:
- Database query performance
- API endpoint response times
- Cross-region replication latency
- Access control check performance

## Disaster Recovery

### Service Recovery

If the service crashes:

1. Check service status: `systemctl status multi-region`
2. Review logs: `journalctl -u multi-region -n 50`
3. Restart service: `systemctl restart multi-region`
4. Verify recovery: `curl http://localhost:8000/health`

### Data Recovery

In case of data loss:

1. Restore from backup: `psql multi_region_db < multi_region_db_backup.sql`
2. Verify data integrity: Run consistency checks
3. Restart service: `systemctl restart multi-region`
4. Monitor for issues: Check logs and metrics

## Security Considerations

### Access Control

- Implement authentication for all API endpoints
- Use HTTPS in production
- Restrict API access to authorized networks
- Implement rate limiting

### Audit Logging

- Log all region operations
- Log all policy changes
- Log all data classifications
- Log all access requests and approvals
- Retain logs for compliance period

### Secret Management

- Store database credentials in environment variables
- Use secrets management system (e.g., HashiCorp Vault)
- Rotate credentials regularly
- Never commit secrets to version control

## Escalation Procedures

### Critical Issues

For critical region failures:

1. Immediate failover if safe to do so
2. Notify on-call engineer
3. Begin incident investigation
4. Document root cause
5. Implement preventive measures

### Compliance Violations

For compliance violations:

1. Isolate affected data
2. Notify compliance team
3. Begin forensic analysis
4. Document violation
5. Implement corrective measures

## Contact Information

- **On-Call Engineer:** See escalation policy
- **Compliance Team:** compliance@example.com
- **Database Administrator:** dba@example.com
- **AWS Support:** AWS Support Portal
