"""
End-to-End Tests for ID-3 Multi-Region Infrastructure

Complete workflow tests for multi-region deployment and data residency.
Enforces INV-002 (Strict Tenant Isolation) and INV-007 (Data Residency as Declarative Governance).
"""

import pytest
from datetime import datetime, timedelta

from src.residency.residency_manager import ResidencyManager
from src.residency.residency_enforcer import ResidencyEnforcer
from src.access_control.access_manager import AccessManager
from src.models.residency import ResidencyMode, ResidencyPolicyType
from src.models.access_control import AccessRequestStatus


class TestCompleteDataResidencyWorkflow:
    """Tests for complete data residency workflow"""

    @pytest.mark.asyncio
    async def test_nigeria_data_residency_workflow(self, residency_manager, residency_enforcer, access_manager):
        """Test complete Nigeria data residency workflow (INV-007)"""
        # Step 1: Create Nigeria residency policy
        policy = await residency_manager.create_policy(
            name="Nigeria NDPR Compliance",
            residency_mode=ResidencyMode.SINGLE_COUNTRY,
            policy_type=ResidencyPolicyType.MANDATORY,
            description="NDPR requires data to stay in Nigeria",
            allowed_countries=["NG"],
            allowed_regions=["af-west-1"]
        )
        
        # Step 2: Verify data can be stored in Nigeria
        result = await residency_enforcer.enforce_residency(
            policy_id=policy.id,
            data_id="nigeria-customer-data-001",
            target_region="af-west-1"
        )
        assert result["allowed"] is True
        
        # Step 3: Verify data cannot leave Nigeria
        result = await residency_enforcer.enforce_residency(
            policy_id=policy.id,
            data_id="nigeria-customer-data-001",
            target_region="us-east-1"
        )
        assert result["allowed"] is False
        
        # Step 4: Create cross-border access request (should require approval)
        request = await access_manager.create_access_request(
            requester_id="support-user-001",
            data_id="nigeria-customer-data-001",
            source_region="us-east-1",
            target_region="af-west-1",
            access_type="read",
            reason="Customer support investigation"
        )
        
        # Step 5: Verify request is pending
        assert request.status == AccessRequestStatus.PENDING

    @pytest.mark.asyncio
    async def test_eu_gdpr_compliance_workflow(self, residency_manager, residency_enforcer, access_manager):
        """Test EU GDPR compliance workflow"""
        # Step 1: Create EU residency policy
        policy = await residency_manager.create_policy(
            name="EU GDPR Compliance",
            residency_mode=ResidencyMode.REGIONAL,
            policy_type=ResidencyPolicyType.MANDATORY,
            description="GDPR requires data to stay in EU",
            allowed_regions=["eu-west-1", "eu-central-1", "eu-west-2"]
        )
        
        # Step 2: Verify data can be stored in EU regions
        for region in ["eu-west-1", "eu-central-1"]:
            result = await residency_enforcer.enforce_residency(
                policy_id=policy.id,
                data_id="eu-customer-data-001",
                target_region=region
            )
            assert result["allowed"] is True
        
        # Step 3: Verify data cannot leave EU
        result = await residency_enforcer.enforce_residency(
            policy_id=policy.id,
            data_id="eu-customer-data-001",
            target_region="us-east-1"
        )
        assert result["allowed"] is False


class TestMultiTenantWorkflow:
    """Tests for multi-tenant workflow (INV-002)"""

    @pytest.mark.asyncio
    async def test_complete_tenant_isolation_workflow(self, residency_manager, access_manager, tenant_a_config, tenant_b_config):
        """Test complete tenant isolation workflow"""
        # Step 1: Create tenant-specific policies
        policy_a = await residency_manager.create_policy(
            name=f"{tenant_a_config['tenant_id']}-policy",
            residency_mode=ResidencyMode.SINGLE_COUNTRY,
            policy_type=ResidencyPolicyType.MANDATORY,
            allowed_regions=["us-east-1"]
        )
        
        policy_b = await residency_manager.create_policy(
            name=f"{tenant_b_config['tenant_id']}-policy",
            residency_mode=ResidencyMode.REGIONAL,
            policy_type=ResidencyPolicyType.MANDATORY,
            allowed_regions=["eu-west-1"]
        )
        
        # Step 2: Create access requests for each tenant
        request_a = await access_manager.create_access_request(
            requester_id=f"{tenant_a_config['tenant_id']}-user-001",
            data_id=f"{tenant_a_config['tenant_id']}-data-001",
            source_region="us-east-1",
            target_region="us-east-1",
            access_type="read",
            reason="Internal access"
        )
        
        request_b = await access_manager.create_access_request(
            requester_id=f"{tenant_b_config['tenant_id']}-user-001",
            data_id=f"{tenant_b_config['tenant_id']}-data-001",
            source_region="eu-west-1",
            target_region="eu-west-1",
            access_type="read",
            reason="Internal access"
        )
        
        # Step 3: Approve requests
        grant_a = await access_manager.approve_access_request(request_a.id, "admin-a")
        grant_b = await access_manager.approve_access_request(request_b.id, "admin-b")
        
        # Step 4: Verify grants are isolated
        assert grant_a.user_id != grant_b.user_id
        assert grant_a.data_id != grant_b.data_id
        
        # Step 5: Verify tenant A cannot access tenant B data
        grants_a = access_manager.list_access_grants(user_id=f"{tenant_a_config['tenant_id']}-user-001")
        assert all(tenant_a_config['tenant_id'] in g.data_id for g in grants_a)


class TestCrossBorderAccessWorkflow:
    """Tests for cross-border access workflow"""

    @pytest.mark.asyncio
    async def test_cross_border_access_approval_workflow(self, residency_manager, residency_enforcer, access_manager):
        """Test cross-border access approval workflow"""
        # Step 1: Create residency policy
        policy = await residency_manager.create_policy(
            name="Regional Policy",
            residency_mode=ResidencyMode.REGIONAL,
            policy_type=ResidencyPolicyType.MANDATORY,
            allowed_regions=["us-east-1", "us-west-2"]
        )
        
        # Step 2: Create cross-border access request
        request = await access_manager.create_access_request(
            requester_id="user-001",
            data_id="data-001",
            source_region="eu-west-1",
            target_region="us-east-1",
            access_type="read",
            reason="Business operation"
        )
        
        assert request.status == AccessRequestStatus.PENDING
        
        # Step 3: Approve request
        grant = await access_manager.approve_access_request(request.id, "admin")
        
        assert grant is not None
        assert grant.user_id == "user-001"
        
        # Step 4: Verify request status updated
        updated_request = access_manager.get_access_request(request.id)
        assert updated_request.status == AccessRequestStatus.APPROVED

    @pytest.mark.asyncio
    async def test_cross_border_access_rejection_workflow(self, access_manager):
        """Test cross-border access rejection workflow"""
        # Step 1: Create cross-border access request
        request = await access_manager.create_access_request(
            requester_id="user-001",
            data_id="sensitive-data-001",
            source_region="af-west-1",
            target_region="us-east-1",
            access_type="export",
            reason="Data export request"
        )
        
        # Step 2: Reject request
        rejected = await access_manager.reject_access_request(
            request.id,
            "Data export not allowed for this data classification"
        )
        
        assert rejected.status == AccessRequestStatus.REJECTED
        assert rejected.rejection_reason is not None

    @pytest.mark.asyncio
    async def test_access_grant_revocation_workflow(self, access_manager):
        """Test access grant revocation workflow"""
        # Step 1: Create and approve request
        request = await access_manager.create_access_request(
            requester_id="user-001",
            data_id="data-001",
            source_region="us-east-1",
            target_region="eu-west-1",
            access_type="read",
            reason="Temporary access"
        )
        
        grant = await access_manager.approve_access_request(request.id, "admin")
        
        # Step 2: Revoke grant
        revoked = await access_manager.revoke_access_grant(grant.id, "security-admin")
        
        assert revoked.revoked_at is not None
        assert revoked.revoked_by == "security-admin"


class TestNigeriaFirstDeployment:
    """Tests for Nigeria-first deployment scenarios (INV-007)"""

    @pytest.mark.asyncio
    async def test_nigeria_deployment_with_data_residency(self, residency_manager, residency_enforcer, access_manager, nigeria_region):
        """Test Nigeria deployment with data residency enforcement"""
        # Step 1: Create Nigeria-specific policy
        policy = await residency_manager.create_policy(
            name="Nigeria First Deployment",
            residency_mode=ResidencyMode.FULLY_SOVEREIGN,
            policy_type=ResidencyPolicyType.MANDATORY,
            description="Complete data sovereignty in Nigeria",
            sovereign_country="NG",
            allowed_regions=["af-west-1"]
        )
        
        # Step 2: Verify Nigeria region is valid
        result = await residency_enforcer.enforce_residency(
            policy_id=policy.id,
            data_id="nigeria-business-data",
            target_region="af-west-1"
        )
        assert result["allowed"] is True
        
        # Step 3: Verify all other regions are blocked
        for region in ["us-east-1", "eu-west-1", "ap-southeast-1"]:
            result = await residency_enforcer.enforce_residency(
                policy_id=policy.id,
                data_id="nigeria-business-data",
                target_region=region
            )
            assert result["allowed"] is False

    @pytest.mark.asyncio
    async def test_nigeria_multi_tenant_deployment(self, residency_manager, access_manager):
        """Test Nigeria multi-tenant deployment"""
        # Create policies for multiple Nigerian tenants
        tenant_policies = []
        
        for i in range(3):
            policy = await residency_manager.create_policy(
                name=f"Nigeria Tenant {i+1}",
                residency_mode=ResidencyMode.SINGLE_COUNTRY,
                policy_type=ResidencyPolicyType.MANDATORY,
                allowed_regions=["af-west-1"]
            )
            tenant_policies.append(policy)
        
        # Verify all policies enforce Nigeria residency
        assert len(tenant_policies) == 3
        assert all(p.residency_mode == ResidencyMode.SINGLE_COUNTRY for p in tenant_policies)
        assert all("af-west-1" in p.allowed_regions for p in tenant_policies)
