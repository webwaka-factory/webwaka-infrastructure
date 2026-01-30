# ID-1: Enterprise Deployment Automation

**Status:** 🟡 Authorized for Execution (Wave 3)

## Overview

This implementation provides a comprehensive Enterprise Deployment Automation system for self-hosted enterprise instances. It includes automated compile & deploy pipelines, update channel policy enforcement, version pinning, security patch management, and rollback capabilities.

## Project Structure

```
id1-enterprise-deployment-automation/
├── README.md                          # This file
├── src/                               # Source code
│   ├── core/                          # Core deployment engine
│   ├── policies/                      # Update channel policies
│   ├── versioning/                    # Version management and pinning
│   ├── security/                      # Security patch enforcement
│   ├── rollback/                      # Rollback mechanisms
│   └── api/                           # REST API services
├── tests/                             # Test suite
│   ├── unit/                          # Unit tests
│   ├── integration/                   # Integration tests
│   └── e2e/                           # End-to-end tests
├── docs/                              # Documentation
│   ├── adr/                           # Architecture Decision Records
│   ├── api/                           # API documentation
│   └── runbooks/                      # Operational runbooks
└── config/                            # Configuration files
```

## Key Components

### 1. Compile & Deploy Pipeline
- Automated manifest compilation
- Deployment orchestration
- Instance provisioning and configuration
- Health checks and validation

### 2. Update Channel Policy Enforcement
- **Auto-Update:** Automatically deploy new versions
- **Manual-Approval:** Require approval before deployment
- **Frozen:** Lock to specific versions, security patches only

### 3. Version Pinning
- Platform-level version pinning
- Suite-level version pinning
- Capability-level version pinning
- Dependency resolution and compatibility checking

### 4. Security Patch Enforcement
- Automatic detection of critical security patches
- Enforcement regardless of update channel policy
- Patch validation and testing
- Audit logging

### 5. Rollback Support
- Deployment manifest versioning
- Point-in-time rollback capability
- State preservation and recovery
- Rollback validation

## Quick Start

### Prerequisites
- Python 3.11+
- Docker (for containerized deployments)
- Git
- PostgreSQL (for state management)

### Installation

```bash
# Clone the repository
git clone https://github.com/webwakaagent1/webwaka.git
cd webwaka/implementations/id1-enterprise-deployment-automation

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -m src.core.db init

# Run migrations
python -m src.core.db migrate
```

### Configuration

Create a `.env` file with the following variables:

```env
DATABASE_URL=postgresql://user:password@localhost/deployment_db
API_PORT=8000
API_HOST=0.0.0.0
LOG_LEVEL=INFO
SECURITY_PATCH_CHECK_INTERVAL=3600
```

### Running the Service

```bash
# Start the deployment service
python -m src.api.server

# In another terminal, start the background workers
python -m src.core.workers
```

## API Endpoints

### Deployment Management
- `POST /api/v1/deployments` - Create new deployment
- `GET /api/v1/deployments/{id}` - Get deployment status
- `PUT /api/v1/deployments/{id}` - Update deployment
- `DELETE /api/v1/deployments/{id}` - Cancel deployment

### Policy Management
- `GET /api/v1/policies` - List update channel policies
- `POST /api/v1/policies` - Create policy
- `PUT /api/v1/policies/{id}` - Update policy
- `DELETE /api/v1/policies/{id}` - Delete policy

### Version Management
- `GET /api/v1/versions` - List available versions
- `POST /api/v1/versions/pin` - Pin version
- `DELETE /api/v1/versions/pin/{id}` - Unpin version
- `GET /api/v1/versions/compatibility` - Check version compatibility

### Rollback Operations
- `POST /api/v1/rollback` - Initiate rollback
- `GET /api/v1/rollback/{id}` - Get rollback status
- `GET /api/v1/rollback/history` - List rollback history

### Security Patches
- `GET /api/v1/security/patches` - List available patches
- `POST /api/v1/security/patches/apply` - Apply security patch
- `GET /api/v1/security/patches/status` - Get patch status

## Testing

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run with coverage
pytest --cov=src tests/
```

## Documentation

- **Architecture Decision Records:** See `docs/adr/`
- **API Documentation:** See `docs/api/`
- **Operational Runbooks:** See `docs/runbooks/`

## Contributing

All contributions must follow the mandatory invariants:
- **INV-011 (PaA Execution):** All work must be traceable to the execution prompt
- **INV-012 (Single-Repository Topology):** All work must be committed to this directory

## License

This project is part of the webwaka platform and follows the same licensing terms.

## Support

For issues, questions, or contributions, please open an issue in the main webwaka repository.
