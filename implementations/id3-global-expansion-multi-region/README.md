# ID-3: Global Expansion & Multi-Region

**Status:** 🟡 Authorized for Execution (Wave 3)

## Overview

This implementation provides a comprehensive Global Expansion & Multi-Region system for deploying the webwaka platform across multiple AWS regions with configurable data residency, data classification enforcement, and cross-border access controls.

## Project Structure

```
id3-global-expansion-multi-region/
├── README.md                          # This file
├── src/                               # Source code
│   ├── core/                          # Core multi-region engine
│   ├── regions/                       # AWS region management
│   ├── residency/                     # Data residency modes
│   ├── classification/                # Data classification system
│   ├── access_control/                # Cross-border access controls
│   ├── api/                           # REST API services
│   └── models/                        # Data models
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

### 1. Multi-Region Deployment

- AWS region management and orchestration
- Region-specific configuration
- Cross-region replication strategies
- Health monitoring across regions

### 2. Configurable Data Residency

Five configurable data residency modes:

- **Single-Country:** All data remains in a single country
- **Regional:** Data stays within a geographic region
- **Hybrid:** Mix of local and regional data storage
- **Fully Sovereign:** Data follows strict sovereignty requirements
- **Client-Owned Sovereignty:** Client controls data location

### 3. Data Classification Enforcement

Five data classification levels:

- **Identity:** User identity and authentication data
- **Transactional:** Business transaction records
- **Operational:** System operational data
- **Content:** User-generated content
- **Analytical/Derived:** Aggregated and derived data

### 4. Cross-Border Access Controls

- Explicit access authorization
- Comprehensive audit logging
- Access request tracking
- Revocable access grants
- Compliance reporting

## Quick Start

### Prerequisites

- Python 3.11+
- AWS CLI configured with credentials
- PostgreSQL (for state management)
- Docker (optional, for containerized deployments)

### Installation

```bash
# Clone the repository
git clone https://github.com/webwakaagent1/webwaka.git
cd webwaka/implementations/id3-global-expansion-multi-region

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
DATABASE_URL=postgresql://user:password@localhost/multi_region_db
API_PORT=8000
API_HOST=0.0.0.0
LOG_LEVEL=INFO
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

### Running the Service

```bash
# Start the multi-region service
python -m src.api.server

# In another terminal, start background workers
python -m src.core.workers
```

## API Endpoints

### Region Management
- `GET /api/v1/regions` - List configured regions
- `POST /api/v1/regions` - Add new region
- `GET /api/v1/regions/{region_id}` - Get region details
- `PUT /api/v1/regions/{region_id}` - Update region
- `DELETE /api/v1/regions/{region_id}` - Remove region

### Data Residency
- `GET /api/v1/residency/modes` - List available residency modes
- `POST /api/v1/residency/policies` - Create residency policy
- `GET /api/v1/residency/policies/{policy_id}` - Get policy details
- `PUT /api/v1/residency/policies/{policy_id}` - Update policy
- `DELETE /api/v1/residency/policies/{policy_id}` - Delete policy

### Data Classification
- `GET /api/v1/classification/levels` - List classification levels
- `POST /api/v1/data/classify` - Classify data
- `GET /api/v1/data/{data_id}/classification` - Get data classification
- `PUT /api/v1/data/{data_id}/classification` - Update classification

### Cross-Border Access
- `POST /api/v1/access/request` - Request cross-border access
- `GET /api/v1/access/requests/{request_id}` - Get access request status
- `POST /api/v1/access/approve` - Approve access request
- `POST /api/v1/access/revoke` - Revoke access
- `GET /api/v1/access/audit` - Get access audit logs

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
