"""
ID-1 Enterprise Deployment Automation - Test Configuration

Shared fixtures and configuration for all tests.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any, List
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models.deployment import (
    Deployment, DeploymentStatus, DeploymentManifest,
    DeploymentRequest, DeploymentResponse
)
from src.models.policy import (
    UpdateChannelPolicy, PolicyType, PolicyUpdateRequest, PolicyResponse
)
from src.models.rollback import (
    RollbackRecord, RollbackStatus, ManifestVersion, RollbackHistory
)
from src.models.security import (
    SecurityPatch, PatchStatus, SeverityLevel
)
from src.models.version import (
    VersionPin, Version
)
from src.core.deployment_engine import DeploymentEngine
from src.core.validator import DeploymentValidator
from src.rollback.rollback_manager import RollbackManager
from src.policies.policy_manager import PolicyManager


@pytest.fixture
def sample_manifest() -> DeploymentManifest:
    """Create sample deployment manifest"""
    return DeploymentManifest(
        id="manifest-001",
        version="1.0.0",
        platform_version="2.0.0",
        suites={
            "commerce": "1.5.0",
            "mlas": "1.2.0",
            "transport": "1.0.0"
        },
        capabilities={
            "reporting": "1.0.0",
            "content_management": "1.1.0"
        },
        configuration={
            "environment": "production",
            "replicas": 3,
            "region": "af-west-1"  # Nigeria region (INV-007)
        },
        metadata={
            "created_by": "admin",
            "description": "Production deployment"
        }
    )


@pytest.fixture
def sample_deployment() -> Dict[str, Any]:
    """Create sample deployment data"""
    return {
        "id": "deploy-001",
        "manifest_id": "manifest-001",
        "instance_id": "instance-prod-01",
        "status": DeploymentStatus.PENDING,
        "created_at": datetime.utcnow(),
    }


@pytest.fixture
def sample_policy() -> UpdateChannelPolicy:
    """Create sample update channel policy"""
    return UpdateChannelPolicy(
        id="policy-001",
        instance_id="instance-prod-01",
        policy_type=PolicyType.MANUAL_APPROVAL,
        enabled=True,
        description="Production instance requires manual approval",
        approval_required_roles=["admin", "devops"],
        approval_timeout_hours=72
    )


@pytest.fixture
def sample_auto_update_policy() -> UpdateChannelPolicy:
    """Create sample auto-update policy"""
    return UpdateChannelPolicy(
        id="policy-002",
        instance_id="instance-dev-01",
        policy_type=PolicyType.AUTO_UPDATE,
        enabled=True,
        description="Development instance auto-updates",
        auto_update_schedule="0 2 * * *",  # 2 AM daily
        auto_update_maintenance_window={
            "start_hour": 2,
            "end_hour": 6,
            "timezone": "UTC"
        }
    )


@pytest.fixture
def sample_frozen_policy() -> UpdateChannelPolicy:
    """Create sample frozen policy"""
    return UpdateChannelPolicy(
        id="policy-003",
        instance_id="instance-stable-01",
        policy_type=PolicyType.FROZEN,
        enabled=True,
        description="Stable instance with frozen versions",
        frozen_versions={
            "platform": "1.9.0",
            "commerce": "1.4.0"
        },
        allow_security_patches=True
    )


@pytest.fixture
def sample_rollback() -> Dict[str, Any]:
    """Create sample rollback data"""
    return {
        "id": "rollback-001",
        "instance_id": "instance-prod-01",
        "from_manifest_id": "manifest-002",
        "to_manifest_id": "manifest-001",
        "status": RollbackStatus.PENDING,
        "reason": "Deployment caused performance issues",
        "initiated_by": "admin"
    }


@pytest.fixture
def sample_security_patch() -> Dict[str, Any]:
    """Create sample security patch data"""
    return {
        "id": "patch-001",
        "cve_ids": ["CVE-2024-0001"],
        "component_type": "platform",
        "component_name": "webwaka-platform",
        "affected_versions": ["1.0.0", "1.1.0", "1.2.0"],
        "patched_version": "1.2.1",
        "severity": SeverityLevel.CRITICAL,
        "description": "Fixes critical authentication bypass vulnerability",
        "release_date": datetime.utcnow(),
        "is_mandatory": True
    }


@pytest.fixture
def sample_version_pin() -> Dict[str, Any]:
    """Create sample version pin data"""
    return {
        "id": "pin-001",
        "instance_id": "instance-prod-01",
        "component_type": "suite",
        "component_name": "commerce",
        "pinned_version": "1.4.0",
        "reason": "Stable version for production"
    }


@pytest.fixture
def deployment_engine() -> DeploymentEngine:
    """Create deployment engine instance"""
    return DeploymentEngine()


@pytest.fixture
def rollback_manager() -> RollbackManager:
    """Create rollback manager instance"""
    return RollbackManager()


@pytest.fixture
def policy_manager() -> PolicyManager:
    """Create policy manager instance"""
    return PolicyManager()


@pytest.fixture
def nigeria_instance_config() -> Dict[str, Any]:
    """Create Nigeria-specific instance configuration (INV-007)"""
    return {
        "instance_id": "instance-ng-prod-01",
        "region": "af-west-1",
        "country_code": "NG",
        "data_center": "Lagos, Nigeria",
        "compliance_requirements": ["NDPR"],  # Nigeria Data Protection Regulation
        "currency": "NGN",
        "timezone": "Africa/Lagos"
    }


@pytest.fixture
def multi_region_manifests() -> List[DeploymentManifest]:
    """Create manifests for multi-region deployment"""
    return [
        DeploymentManifest(
            id="manifest-ng-001",
            version="1.0.0",
            platform_version="2.0.0",
            suites={"commerce": "1.5.0"},
            configuration={"region": "af-west-1", "country": "NG"}
        ),
        DeploymentManifest(
            id="manifest-us-001",
            version="1.0.0",
            platform_version="2.0.0",
            suites={"commerce": "1.5.0"},
            configuration={"region": "us-east-1", "country": "US"}
        ),
        DeploymentManifest(
            id="manifest-eu-001",
            version="1.0.0",
            platform_version="2.0.0",
            suites={"commerce": "1.5.0"},
            configuration={"region": "eu-west-1", "country": "EU"}
        )
    ]
