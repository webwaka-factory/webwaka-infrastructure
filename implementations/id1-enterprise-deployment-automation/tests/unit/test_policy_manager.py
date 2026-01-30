"""Unit tests for policy manager."""

import pytest

from src.policies.policy_manager import PolicyManager
from src.models.policy import PolicyType


@pytest.fixture
def policy_manager():
    """Create policy manager instance."""
    return PolicyManager()


@pytest.mark.asyncio
async def test_create_policy(policy_manager):
    """Test policy creation."""
    policy = await policy_manager.create_policy(
        instance_id="instance-001",
        policy_type=PolicyType.MANUAL_APPROVAL,
        description="Test policy"
    )
    
    assert policy.id is not None
    assert policy.instance_id == "instance-001"
    assert policy.policy_type == PolicyType.MANUAL_APPROVAL
    assert policy.description == "Test policy"
    assert policy.enabled is True


@pytest.mark.asyncio
async def test_get_policy(policy_manager):
    """Test retrieving policy."""
    created = await policy_manager.create_policy(
        instance_id="instance-001",
        policy_type=PolicyType.AUTO_UPDATE
    )
    
    retrieved = policy_manager.get_policy(created.id)
    
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.policy_type == PolicyType.AUTO_UPDATE


@pytest.mark.asyncio
async def test_get_instance_policy(policy_manager):
    """Test retrieving instance policy."""
    await policy_manager.create_policy(
        instance_id="instance-001",
        policy_type=PolicyType.FROZEN
    )
    
    policy = policy_manager.get_instance_policy("instance-001")
    
    assert policy is not None
    assert policy.instance_id == "instance-001"
    assert policy.policy_type == PolicyType.FROZEN


@pytest.mark.asyncio
async def test_update_policy(policy_manager):
    """Test policy update."""
    policy = await policy_manager.create_policy(
        instance_id="instance-001",
        policy_type=PolicyType.AUTO_UPDATE
    )
    
    updated = await policy_manager.update_policy(
        policy.id,
        enabled=False,
        description="Updated policy"
    )
    
    assert updated is not None
    assert updated.enabled is False
    assert updated.description == "Updated policy"


@pytest.mark.asyncio
async def test_delete_policy(policy_manager):
    """Test policy deletion."""
    policy = await policy_manager.create_policy(
        instance_id="instance-001",
        policy_type=PolicyType.MANUAL_APPROVAL
    )
    
    deleted = await policy_manager.delete_policy(policy.id)
    
    assert deleted is True
    
    retrieved = policy_manager.get_policy(policy.id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_list_policies(policy_manager):
    """Test listing policies."""
    await policy_manager.create_policy(
        instance_id="instance-001",
        policy_type=PolicyType.AUTO_UPDATE
    )
    
    await policy_manager.create_policy(
        instance_id="instance-002",
        policy_type=PolicyType.FROZEN
    )
    
    all_policies = policy_manager.list_policies()
    assert len(all_policies) == 2
    
    instance_policies = policy_manager.list_policies("instance-001")
    assert len(instance_policies) == 1
    assert instance_policies[0].instance_id == "instance-001"
