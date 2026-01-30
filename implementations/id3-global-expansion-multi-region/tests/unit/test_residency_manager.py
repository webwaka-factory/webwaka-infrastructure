"""Unit tests for residency manager."""

import pytest
from src.residency.residency_manager import ResidencyManager
from src.models.residency import ResidencyMode, ResidencyPolicyType


@pytest.fixture
def manager():
    """Create residency manager instance."""
    return ResidencyManager()


@pytest.mark.asyncio
async def test_create_policy(manager):
    """Test policy creation."""
    policy = await manager.create_policy(
        name="EU Data Residency",
        residency_mode=ResidencyMode.REGIONAL,
        policy_type=ResidencyPolicyType.MANDATORY,
        allowed_regions=["eu-west-1", "eu-central-1"]
    )
    
    assert policy.id == "policy-001"
    assert policy.name == "EU Data Residency"
    assert policy.residency_mode == ResidencyMode.REGIONAL
    assert policy.enabled is True


@pytest.mark.asyncio
async def test_get_policy(manager):
    """Test retrieving policy."""
    created = await manager.create_policy(
        name="EU Data Residency",
        residency_mode=ResidencyMode.REGIONAL
    )
    
    retrieved = manager.get_policy(created.id)
    
    assert retrieved is not None
    assert retrieved.id == created.id


@pytest.mark.asyncio
async def test_list_policies(manager):
    """Test listing policies."""
    await manager.create_policy(
        name="EU Data Residency",
        residency_mode=ResidencyMode.REGIONAL
    )
    
    await manager.create_policy(
        name="US Data Residency",
        residency_mode=ResidencyMode.REGIONAL
    )
    
    policies = manager.list_policies()
    assert len(policies) == 2


@pytest.mark.asyncio
async def test_validate_region_compliance(manager):
    """Test region compliance validation."""
    policy = await manager.create_policy(
        name="EU Data Residency",
        residency_mode=ResidencyMode.REGIONAL,
        allowed_regions=["eu-west-1", "eu-central-1"]
    )
    
    result = await manager.validate_region_compliance(policy.id, "eu-west-1")
    
    assert result["compliant"] is True
    assert result["target_region"] == "eu-west-1"


@pytest.mark.asyncio
async def test_validate_region_non_compliance(manager):
    """Test region non-compliance validation."""
    policy = await manager.create_policy(
        name="EU Data Residency",
        residency_mode=ResidencyMode.REGIONAL,
        allowed_regions=["eu-west-1", "eu-central-1"]
    )
    
    result = await manager.validate_region_compliance(policy.id, "us-east-1")
    
    assert result["compliant"] is False
