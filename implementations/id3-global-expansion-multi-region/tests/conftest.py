"""
ID-3 Global Expansion Multi-Region - Test Configuration

Shared fixtures and configuration for all tests.
Enforces INV-002 (Strict Tenant Isolation) and INV-007 (Data Residency as Declarative Governance).
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any, List
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models.region import Region, RegionStatus, RegionConfig
from src.models.residency import (
    ResidencyPolicy, ResidencyMode, ResidencyPolicyType
)
from src.models.access_control import (
    AccessRequest, AccessGrant, AccessRequestStatus, AccessAuditLog
)
from src.residency.residency_manager import ResidencyManager
from src.residency.residency_enforcer import ResidencyEnforcer
from src.access_control.access_manager import AccessManager


@pytest.fixture
def residency_manager() -> ResidencyManager:
    """Create residency manager instance"""
    return ResidencyManager()


@pytest.fixture
def access_manager() -> AccessManager:
    """Create access manager instance"""
    return AccessManager()


@pytest.fixture
def residency_enforcer(residency_manager) -> ResidencyEnforcer:
    """Create residency enforcer instance"""
    return ResidencyEnforcer(residency_manager)


@pytest.fixture
def nigeria_region() -> Region:
    """Create Nigeria region configuration (INV-007)"""
    return Region(
        id="region-af-west-1",
        name="Africa West (Nigeria)",
        aws_region="af-west-1",
        country_code="NG",
        status=RegionStatus.ACTIVE,
        config=RegionConfig(
            aws_region="af-west-1",
            country_code="NG",
            data_center_location="Lagos, Nigeria",
            availability_zones=["af-west-1a", "af-west-1b"],
            replication_targets=[]
        )
    )


@pytest.fixture
def eu_region() -> Region:
    """Create EU region configuration"""
    return Region(
        id="region-eu-west-1",
        name="EU West (Ireland)",
        aws_region="eu-west-1",
        country_code="IE",
        status=RegionStatus.ACTIVE,
        config=RegionConfig(
            aws_region="eu-west-1",
            country_code="IE",
            data_center_location="Dublin, Ireland",
            availability_zones=["eu-west-1a", "eu-west-1b", "eu-west-1c"],
            replication_targets=["eu-central-1"]
        )
    )


@pytest.fixture
def us_region() -> Region:
    """Create US region configuration"""
    return Region(
        id="region-us-east-1",
        name="US East (N. Virginia)",
        aws_region="us-east-1",
        country_code="US",
        status=RegionStatus.ACTIVE,
        config=RegionConfig(
            aws_region="us-east-1",
            country_code="US",
            data_center_location="Virginia, USA",
            availability_zones=["us-east-1a", "us-east-1b", "us-east-1c"],
            replication_targets=["us-west-2"]
        )
    )


@pytest.fixture
def nigeria_residency_policy() -> Dict[str, Any]:
    """Create Nigeria data residency policy (INV-007)"""
    return {
        "name": "Nigeria Data Residency",
        "residency_mode": ResidencyMode.SINGLE_COUNTRY,
        "policy_type": ResidencyPolicyType.MANDATORY,
        "description": "Data must remain within Nigeria (NDPR compliance)",
        "allowed_countries": ["NG"],
        "allowed_regions": ["af-west-1"]
    }


@pytest.fixture
def eu_residency_policy() -> Dict[str, Any]:
    """Create EU data residency policy (GDPR)"""
    return {
        "name": "EU Data Residency",
        "residency_mode": ResidencyMode.REGIONAL,
        "policy_type": ResidencyPolicyType.MANDATORY,
        "description": "Data must remain within EU (GDPR compliance)",
        "allowed_countries": ["IE", "DE", "FR", "NL"],
        "allowed_regions": ["eu-west-1", "eu-central-1", "eu-west-2"]
    }


@pytest.fixture
def hybrid_residency_policy() -> Dict[str, Any]:
    """Create hybrid residency policy"""
    return {
        "name": "Hybrid Residency",
        "residency_mode": ResidencyMode.HYBRID,
        "policy_type": ResidencyPolicyType.PREFERRED,
        "description": "Primary in US, secondary in EU",
        "primary_region": "us-east-1",
        "secondary_regions": ["eu-west-1", "eu-central-1"]
    }


@pytest.fixture
def sovereign_residency_policy() -> Dict[str, Any]:
    """Create fully sovereign residency policy"""
    return {
        "name": "Fully Sovereign",
        "residency_mode": ResidencyMode.FULLY_SOVEREIGN,
        "policy_type": ResidencyPolicyType.MANDATORY,
        "description": "Complete data sovereignty in Nigeria",
        "sovereign_country": "NG",
        "allowed_regions": ["af-west-1"]
    }


@pytest.fixture
def client_sovereign_policy() -> Dict[str, Any]:
    """Create client-owned sovereignty policy"""
    return {
        "name": "Client Sovereignty",
        "residency_mode": ResidencyMode.CLIENT_OWNED_SOVEREIGNTY,
        "policy_type": ResidencyPolicyType.MANDATORY,
        "description": "Client specifies allowed regions",
        "client_specified_regions": ["af-west-1", "eu-west-1"]
    }


@pytest.fixture
def sample_access_request() -> Dict[str, Any]:
    """Create sample cross-border access request"""
    return {
        "requester_id": "user-001",
        "data_id": "data-001",
        "source_region": "us-east-1",
        "target_region": "eu-west-1",
        "access_type": "read",
        "reason": "Customer support investigation"
    }


@pytest.fixture
def tenant_a_config() -> Dict[str, Any]:
    """Create Tenant A configuration (INV-002)"""
    return {
        "tenant_id": "tenant-a",
        "name": "Acme Corporation",
        "region": "us-east-1",
        "data_classification": "confidential",
        "residency_policy": "us-only"
    }


@pytest.fixture
def tenant_b_config() -> Dict[str, Any]:
    """Create Tenant B configuration (INV-002)"""
    return {
        "tenant_id": "tenant-b",
        "name": "Beta Industries",
        "region": "eu-west-1",
        "data_classification": "restricted",
        "residency_policy": "eu-only"
    }


@pytest.fixture
def multi_region_setup() -> List[Dict[str, Any]]:
    """Create multi-region setup for testing"""
    return [
        {
            "region_id": "af-west-1",
            "name": "Nigeria",
            "country": "NG",
            "compliance": ["NDPR"]
        },
        {
            "region_id": "eu-west-1",
            "name": "Ireland",
            "country": "IE",
            "compliance": ["GDPR"]
        },
        {
            "region_id": "us-east-1",
            "name": "US East",
            "country": "US",
            "compliance": ["SOC2", "HIPAA"]
        }
    ]
