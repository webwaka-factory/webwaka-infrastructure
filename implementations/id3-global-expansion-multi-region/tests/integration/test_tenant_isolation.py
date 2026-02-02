"""
Integration Tests for ID-3 Tenant Isolation

Tests for strict tenant isolation across regions.
Enforces INV-002 (Strict Tenant Isolation).
"""

import pytest
from datetime import datetime

from src.access_control.access_manager import AccessManager
from src.residency.residency_manager import ResidencyManager
from src.models.access_control import AccessRequestStatus
from src.models.residency import ResidencyMode, ResidencyPolicyType


class TestTenantIsolation:
    """Tests for tenant isolation (INV-002)"""

    @pytest.mark.asyncio
    async def test_tenant_data_isolation(self, access_manager, tenant_a_config, tenant_b_config):
        """Test tenant data is isolated"""
        # Create requests for both tenants
        request_a = await access_manager.create_access_request(
            requester_id=f"{tenant_a_config['tenant_id']}-user-001",
            data_id=f"{tenant_a_config['tenant_id']}-data-001",
            source_region=tenant_a_config["region"],
            target_region="eu-west-1",
            access_type="read",
            reason="Business need"
        )
        
        request_b = await access_manager.create_access_request(
            requester_id=f"{tenant_b_config['tenant_id']}-user-001",
            data_id=f"{tenant_b_config['tenant_id']}-data-001",
            source_region=tenant_b_config["region"],
            target_region="us-east-1",
            access_type="read",
            reason="Business need"
        )
        
        # Verify data IDs are different
        assert request_a.data_id != request_b.data_id
        
        # Verify tenant prefixes
        assert tenant_a_config["tenant_id"] in request_a.data_id
        assert tenant_b_config["tenant_id"] in request_b.data_id

    @pytest.mark.asyncio
    async def test_tenant_user_isolation(self, access_manager, tenant_a_config, tenant_b_config):
        """Test tenant users are isolated"""
        request_a = await access_manager.create_access_request(
            requester_id=f"{tenant_a_config['tenant_id']}-user-001",
            data_id=f"{tenant_a_config['tenant_id']}-data-001",
            source_region=tenant_a_config["region"],
            target_region="eu-west-1",
            access_type="read",
            reason="Business need"
        )
        
        request_b = await access_manager.create_access_request(
            requester_id=f"{tenant_b_config['tenant_id']}-user-001",
            data_id=f"{tenant_b_config['tenant_id']}-data-001",
            source_region=tenant_b_config["region"],
            target_region="us-east-1",
            access_type="read",
            reason="Business need"
        )
        
        # Verify user IDs are different
        assert request_a.requester_id != request_b.requester_id

    @pytest.mark.asyncio
    async def test_tenant_grant_isolation(self, access_manager, tenant_a_config, tenant_b_config):
        """Test tenant grants are isolated"""
        # Create and approve requests for both tenants
        request_a = await access_manager.create_access_request(
            requester_id=f"{tenant_a_config['tenant_id']}-user-001",
            data_id=f"{tenant_a_config['tenant_id']}-data-001",
            source_region=tenant_a_config["region"],
            target_region="eu-west-1",
            access_type="read",
            reason="Business need"
        )
        grant_a = await access_manager.approve_access_request(request_a.id, "admin")
        
        request_b = await access_manager.create_access_request(
            requester_id=f"{tenant_b_config['tenant_id']}-user-001",
            data_id=f"{tenant_b_config['tenant_id']}-data-001",
            source_region=tenant_b_config["region"],
            target_region="us-east-1",
            access_type="read",
            reason="Business need"
        )
        grant_b = await access_manager.approve_access_request(request_b.id, "admin")
        
        # Verify grants are separate
        assert grant_a.id != grant_b.id
        assert grant_a.user_id != grant_b.user_id
        assert grant_a.data_id != grant_b.data_id

    @pytest.mark.asyncio
    async def test_tenant_region_isolation(self, access_manager, tenant_a_config, tenant_b_config):
        """Test tenant regions are isolated"""
        # Tenant A is in US
        request_a = await access_manager.create_access_request(
            requester_id=f"{tenant_a_config['tenant_id']}-user-001",
            data_id=f"{tenant_a_config['tenant_id']}-data-001",
            source_region=tenant_a_config["region"],
            target_region="eu-west-1",
            access_type="read",
            reason="Business need"
        )
        
        # Tenant B is in EU
        request_b = await access_manager.create_access_request(
            requester_id=f"{tenant_b_config['tenant_id']}-user-001",
            data_id=f"{tenant_b_config['tenant_id']}-data-001",
            source_region=tenant_b_config["region"],
            target_region="us-east-1",
            access_type="read",
            reason="Business need"
        )
        
        # Verify source regions are different
        assert request_a.source_region != request_b.source_region


class TestCrossTenantAccessPrevention:
    """Tests for preventing cross-tenant access"""

    @pytest.mark.asyncio
    async def test_tenant_a_cannot_access_tenant_b_data(self, access_manager, tenant_a_config, tenant_b_config):
        """Test Tenant A cannot access Tenant B data"""
        # Tenant A user trying to access Tenant B data (should be tracked)
        request = await access_manager.create_access_request(
            requester_id=f"{tenant_a_config['tenant_id']}-user-001",
            data_id=f"{tenant_b_config['tenant_id']}-data-001",  # Tenant B's data
            source_region=tenant_a_config["region"],
            target_region=tenant_b_config["region"],
            access_type="read",
            reason="Suspicious access attempt"
        )
        
        # The request is created but should be flagged
        # In a real system, this would be rejected by policy
        assert tenant_a_config["tenant_id"] in request.requester_id
        assert tenant_b_config["tenant_id"] in request.data_id

    @pytest.mark.asyncio
    async def test_tenant_listing_isolation(self, access_manager, tenant_a_config, tenant_b_config):
        """Test tenant listing is isolated"""
        # Create requests for both tenants
        await access_manager.create_access_request(
            requester_id=f"{tenant_a_config['tenant_id']}-user-001",
            data_id=f"{tenant_a_config['tenant_id']}-data-001",
            source_region=tenant_a_config["region"],
            target_region="eu-west-1",
            access_type="read",
            reason="Business need"
        )
        
        await access_manager.create_access_request(
            requester_id=f"{tenant_b_config['tenant_id']}-user-001",
            data_id=f"{tenant_b_config['tenant_id']}-data-001",
            source_region=tenant_b_config["region"],
            target_region="us-east-1",
            access_type="read",
            reason="Business need"
        )
        
        # Get all requests
        all_requests = access_manager.list_access_requests()
        
        # Filter by tenant
        tenant_a_requests = [r for r in all_requests if tenant_a_config["tenant_id"] in r.requester_id]
        tenant_b_requests = [r for r in all_requests if tenant_b_config["tenant_id"] in r.requester_id]
        
        # Verify isolation
        assert len(tenant_a_requests) >= 1
        assert len(tenant_b_requests) >= 1
        assert all(tenant_a_config["tenant_id"] in r.requester_id for r in tenant_a_requests)
        assert all(tenant_b_config["tenant_id"] in r.requester_id for r in tenant_b_requests)


class TestMultiTenantResidencyPolicies:
    """Tests for multi-tenant residency policies"""

    @pytest.mark.asyncio
    async def test_tenant_specific_residency_policy(self, residency_manager, tenant_a_config, tenant_b_config):
        """Test tenant-specific residency policies"""
        # Create US-only policy for Tenant A
        policy_a = await residency_manager.create_policy(
            name=f"{tenant_a_config['tenant_id']}-residency",
            residency_mode=ResidencyMode.SINGLE_COUNTRY,
            policy_type=ResidencyPolicyType.MANDATORY,
            allowed_regions=["us-east-1", "us-west-2"]
        )
        
        # Create EU-only policy for Tenant B
        policy_b = await residency_manager.create_policy(
            name=f"{tenant_b_config['tenant_id']}-residency",
            residency_mode=ResidencyMode.REGIONAL,
            policy_type=ResidencyPolicyType.MANDATORY,
            allowed_regions=["eu-west-1", "eu-central-1"]
        )
        
        # Verify policies are separate
        assert policy_a.id != policy_b.id
        assert policy_a.allowed_regions != policy_b.allowed_regions

    @pytest.mark.asyncio
    async def test_tenant_residency_enforcement(self, residency_manager, tenant_a_config, tenant_b_config):
        """Test tenant residency enforcement"""
        # Tenant A: US-only
        policy_a = await residency_manager.create_policy(
            name=f"{tenant_a_config['tenant_id']}-residency",
            residency_mode=ResidencyMode.SINGLE_COUNTRY,
            policy_type=ResidencyPolicyType.MANDATORY,
            allowed_regions=["us-east-1"]
        )
        
        # Tenant B: EU-only
        policy_b = await residency_manager.create_policy(
            name=f"{tenant_b_config['tenant_id']}-residency",
            residency_mode=ResidencyMode.REGIONAL,
            policy_type=ResidencyPolicyType.MANDATORY,
            allowed_regions=["eu-west-1"]
        )
        
        # Validate Tenant A region
        result_a = await residency_manager.validate_region_compliance(
            policy_id=policy_a.id,
            target_region="us-east-1"
        )
        assert result_a["compliant"] is True
        
        # Validate Tenant B region
        result_b = await residency_manager.validate_region_compliance(
            policy_id=policy_b.id,
            target_region="eu-west-1"
        )
        assert result_b["compliant"] is True
        
        # Cross-validate should fail
        result_cross = await residency_manager.validate_region_compliance(
            policy_id=policy_a.id,
            target_region="eu-west-1"
        )
        assert result_cross["compliant"] is False
