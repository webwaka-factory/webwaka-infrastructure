"""
Integration Tests for ID-3 Residency Enforcement

Tests for data residency policy enforcement.
Enforces INV-007 (Data Residency as Declarative Governance).
"""

import pytest
from datetime import datetime

from src.residency.residency_manager import ResidencyManager
from src.residency.residency_enforcer import ResidencyEnforcer
from src.models.residency import ResidencyMode, ResidencyPolicyType


class TestResidencyPolicyEnforcement:
    """Tests for residency policy enforcement"""

    @pytest.mark.asyncio
    async def test_nigeria_single_country_enforcement(self, residency_manager, residency_enforcer, nigeria_residency_policy):
        """Test Nigeria single-country residency enforcement (INV-007)"""
        # Create policy
        policy = await residency_manager.create_policy(**nigeria_residency_policy)
        
        # Test valid region
        result = await residency_enforcer.enforce_residency(
            policy_id=policy.id,
            data_id="data-001",
            target_region="af-west-1"
        )
        
        assert result["allowed"] is True
        
    @pytest.mark.asyncio
    async def test_nigeria_cross_border_blocked(self, residency_manager, residency_enforcer, nigeria_residency_policy):
        """Test Nigeria data cannot leave country (INV-007)"""
        # Create policy
        policy = await residency_manager.create_policy(**nigeria_residency_policy)
        
        # Test invalid region
        result = await residency_enforcer.enforce_residency(
            policy_id=policy.id,
            data_id="data-001",
            target_region="us-east-1"
        )
        
        assert result["allowed"] is False

    @pytest.mark.asyncio
    async def test_eu_regional_enforcement(self, residency_manager, residency_enforcer, eu_residency_policy):
        """Test EU regional residency enforcement"""
        # Create policy
        policy = await residency_manager.create_policy(**eu_residency_policy)
        
        # Test valid EU region
        result = await residency_enforcer.enforce_residency(
            policy_id=policy.id,
            data_id="data-001",
            target_region="eu-west-1"
        )
        
        assert result["allowed"] is True

    @pytest.mark.asyncio
    async def test_eu_data_blocked_outside_eu(self, residency_manager, residency_enforcer, eu_residency_policy):
        """Test EU data cannot leave EU"""
        # Create policy
        policy = await residency_manager.create_policy(**eu_residency_policy)
        
        # Test non-EU region
        result = await residency_enforcer.enforce_residency(
            policy_id=policy.id,
            data_id="data-001",
            target_region="us-east-1"
        )
        
        assert result["allowed"] is False

    @pytest.mark.asyncio
    async def test_hybrid_residency_primary_region(self, residency_manager, residency_enforcer, hybrid_residency_policy):
        """Test hybrid residency primary region"""
        # Create policy
        policy = await residency_manager.create_policy(**hybrid_residency_policy)
        
        # Test primary region
        result = await residency_enforcer.enforce_residency(
            policy_id=policy.id,
            data_id="data-001",
            target_region="us-east-1"
        )
        
        assert result["allowed"] is True

    @pytest.mark.asyncio
    async def test_hybrid_residency_secondary_region(self, residency_manager, residency_enforcer, hybrid_residency_policy):
        """Test hybrid residency secondary region"""
        # Create policy
        policy = await residency_manager.create_policy(**hybrid_residency_policy)
        
        # Test secondary region
        result = await residency_enforcer.enforce_residency(
            policy_id=policy.id,
            data_id="data-001",
            target_region="eu-west-1"
        )
        
        assert result["allowed"] is True


class TestCrossBorderAccessEnforcement:
    """Tests for cross-border access enforcement"""

    @pytest.mark.asyncio
    async def test_same_region_access_allowed(self, residency_manager, residency_enforcer, nigeria_residency_policy):
        """Test same-region access is allowed"""
        policy = await residency_manager.create_policy(**nigeria_residency_policy)
        
        result = await residency_enforcer.check_cross_border_access(
            source_region="af-west-1",
            target_region="af-west-1",
            policy_id=policy.id
        )
        
        assert result["allowed"] is True

    @pytest.mark.asyncio
    async def test_mandatory_policy_blocks_cross_border(self, residency_manager, residency_enforcer, nigeria_residency_policy):
        """Test mandatory policy blocks cross-border access"""
        policy = await residency_manager.create_policy(**nigeria_residency_policy)
        
        result = await residency_enforcer.check_cross_border_access(
            source_region="af-west-1",
            target_region="us-east-1",
            policy_id=policy.id
        )
        
        assert result["allowed"] is False

    @pytest.mark.asyncio
    async def test_disabled_policy_blocks_access(self, residency_manager, residency_enforcer, nigeria_residency_policy):
        """Test disabled policy blocks access"""
        policy = await residency_manager.create_policy(**nigeria_residency_policy)
        
        # Disable policy
        await residency_manager.update_policy(policy.id, enabled=False)
        
        result = await residency_enforcer.check_cross_border_access(
            source_region="af-west-1",
            target_region="af-west-1",
            policy_id=policy.id
        )
        
        assert result["allowed"] is False

    @pytest.mark.asyncio
    async def test_nonexistent_policy_blocks_access(self, residency_enforcer):
        """Test nonexistent policy blocks access"""
        result = await residency_enforcer.check_cross_border_access(
            source_region="af-west-1",
            target_region="us-east-1",
            policy_id="nonexistent"
        )
        
        assert result["allowed"] is False


class TestResidencyModes:
    """Tests for different residency modes"""

    @pytest.mark.asyncio
    async def test_fully_sovereign_mode(self, residency_manager, residency_enforcer, sovereign_residency_policy):
        """Test fully sovereign residency mode"""
        policy = await residency_manager.create_policy(**sovereign_residency_policy)
        
        # Test sovereign region
        result = await residency_enforcer.enforce_residency(
            policy_id=policy.id,
            data_id="data-001",
            target_region="af-west-1"
        )
        
        assert result["allowed"] is True

    @pytest.mark.asyncio
    async def test_client_owned_sovereignty(self, residency_manager, residency_enforcer, client_sovereign_policy):
        """Test client-owned sovereignty mode"""
        policy = await residency_manager.create_policy(**client_sovereign_policy)
        
        # Test client-specified region
        result = await residency_enforcer.enforce_residency(
            policy_id=policy.id,
            data_id="data-001",
            target_region="af-west-1"
        )
        
        assert result["allowed"] is True
        
        # Test non-client-specified region
        result = await residency_enforcer.enforce_residency(
            policy_id=policy.id,
            data_id="data-001",
            target_region="us-east-1"
        )
        
        assert result["allowed"] is False


class TestNigeriaDataResidency:
    """Tests specifically for Nigeria data residency (INV-007)"""

    @pytest.mark.asyncio
    async def test_nigeria_data_stays_in_nigeria(self, residency_manager, residency_enforcer):
        """Test Nigeria data remains in Nigeria"""
        policy = await residency_manager.create_policy(
            name="Nigeria NDPR Compliance",
            residency_mode=ResidencyMode.SINGLE_COUNTRY,
            policy_type=ResidencyPolicyType.MANDATORY,
            description="NDPR requires data to stay in Nigeria",
            allowed_countries=["NG"],
            allowed_regions=["af-west-1"]
        )
        
        # Valid: Nigeria region
        result = await residency_enforcer.enforce_residency(
            policy_id=policy.id,
            data_id="nigeria-data-001",
            target_region="af-west-1"
        )
        assert result["allowed"] is True
        
        # Invalid: US region
        result = await residency_enforcer.enforce_residency(
            policy_id=policy.id,
            data_id="nigeria-data-001",
            target_region="us-east-1"
        )
        assert result["allowed"] is False
        
        # Invalid: EU region
        result = await residency_enforcer.enforce_residency(
            policy_id=policy.id,
            data_id="nigeria-data-001",
            target_region="eu-west-1"
        )
        assert result["allowed"] is False

    @pytest.mark.asyncio
    async def test_nigeria_cross_border_requires_approval(self, residency_manager, residency_enforcer):
        """Test Nigeria cross-border access requires explicit approval"""
        policy = await residency_manager.create_policy(
            name="Nigeria Strict Residency",
            residency_mode=ResidencyMode.SINGLE_COUNTRY,
            policy_type=ResidencyPolicyType.MANDATORY,
            allowed_regions=["af-west-1"]
        )
        
        result = await residency_enforcer.check_cross_border_access(
            source_region="af-west-1",
            target_region="eu-west-1",
            policy_id=policy.id
        )
        
        # Cross-border should require approval
        assert result["allowed"] is False
        assert "approval" in result.get("reason", "").lower()
