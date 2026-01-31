"""
Unit Tests for ID-3 Access Manager

Tests for AccessManager and cross-border access control.
Enforces INV-002 (Strict Tenant Isolation).
"""

import pytest
from datetime import datetime, timedelta

from src.access_control.access_manager import AccessManager
from src.models.access_control import AccessRequestStatus


class TestAccessManager:
    """Tests for AccessManager"""

    @pytest.mark.asyncio
    async def test_create_access_request(self, access_manager, sample_access_request):
        """Test creating an access request"""
        request = await access_manager.create_access_request(**sample_access_request)
        
        assert request.id is not None
        assert request.requester_id == "user-001"
        assert request.status == AccessRequestStatus.PENDING

    @pytest.mark.asyncio
    async def test_get_access_request(self, access_manager, sample_access_request):
        """Test getting an access request"""
        created = await access_manager.create_access_request(**sample_access_request)
        
        retrieved = access_manager.get_access_request(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id

    @pytest.mark.asyncio
    async def test_list_access_requests(self, access_manager, sample_access_request):
        """Test listing access requests"""
        await access_manager.create_access_request(**sample_access_request)
        
        requests = access_manager.list_access_requests()
        
        assert len(requests) >= 1

    @pytest.mark.asyncio
    async def test_list_access_requests_by_status(self, access_manager, sample_access_request):
        """Test listing access requests by status"""
        await access_manager.create_access_request(**sample_access_request)
        
        pending_requests = access_manager.list_access_requests(status=AccessRequestStatus.PENDING)
        
        assert all(r.status == AccessRequestStatus.PENDING for r in pending_requests)

    @pytest.mark.asyncio
    async def test_approve_access_request(self, access_manager, sample_access_request):
        """Test approving an access request"""
        request = await access_manager.create_access_request(**sample_access_request)
        
        grant = await access_manager.approve_access_request(request.id, "admin")
        
        assert grant is not None
        assert grant.user_id == request.requester_id
        
        # Verify request status updated
        updated_request = access_manager.get_access_request(request.id)
        assert updated_request.status == AccessRequestStatus.APPROVED

    @pytest.mark.asyncio
    async def test_reject_access_request(self, access_manager, sample_access_request):
        """Test rejecting an access request"""
        request = await access_manager.create_access_request(**sample_access_request)
        
        rejected = await access_manager.reject_access_request(
            request.id,
            "Policy violation"
        )
        
        assert rejected is not None
        assert rejected.status == AccessRequestStatus.REJECTED
        assert rejected.rejection_reason == "Policy violation"

    @pytest.mark.asyncio
    async def test_get_access_grant(self, access_manager, sample_access_request):
        """Test getting an access grant"""
        request = await access_manager.create_access_request(**sample_access_request)
        grant = await access_manager.approve_access_request(request.id, "admin")
        
        retrieved = access_manager.get_access_grant(grant.id)
        
        assert retrieved is not None
        assert retrieved.id == grant.id

    @pytest.mark.asyncio
    async def test_list_access_grants(self, access_manager, sample_access_request):
        """Test listing access grants"""
        request = await access_manager.create_access_request(**sample_access_request)
        await access_manager.approve_access_request(request.id, "admin")
        
        grants = access_manager.list_access_grants()
        
        assert len(grants) >= 1

    @pytest.mark.asyncio
    async def test_list_access_grants_by_user(self, access_manager, sample_access_request):
        """Test listing access grants by user"""
        request = await access_manager.create_access_request(**sample_access_request)
        await access_manager.approve_access_request(request.id, "admin")
        
        grants = access_manager.list_access_grants(user_id="user-001")
        
        assert all(g.user_id == "user-001" for g in grants)

    @pytest.mark.asyncio
    async def test_revoke_access_grant(self, access_manager, sample_access_request):
        """Test revoking an access grant"""
        request = await access_manager.create_access_request(**sample_access_request)
        grant = await access_manager.approve_access_request(request.id, "admin")
        
        revoked = await access_manager.revoke_access_grant(grant.id, "security-admin")
        
        assert revoked is not None
        assert revoked.revoked_at is not None
        assert revoked.revoked_by == "security-admin"


class TestCrossBorderAccessControl:
    """Tests for cross-border access control"""

    @pytest.mark.asyncio
    async def test_cross_border_request_us_to_eu(self, access_manager):
        """Test cross-border request from US to EU"""
        request = await access_manager.create_access_request(
            requester_id="user-001",
            data_id="data-001",
            source_region="us-east-1",
            target_region="eu-west-1",
            access_type="read",
            reason="Customer support"
        )
        
        assert request.source_region == "us-east-1"
        assert request.target_region == "eu-west-1"

    @pytest.mark.asyncio
    async def test_cross_border_request_eu_to_nigeria(self, access_manager):
        """Test cross-border request from EU to Nigeria"""
        request = await access_manager.create_access_request(
            requester_id="user-002",
            data_id="data-002",
            source_region="eu-west-1",
            target_region="af-west-1",
            access_type="read",
            reason="Business operation"
        )
        
        assert request.source_region == "eu-west-1"
        assert request.target_region == "af-west-1"

    @pytest.mark.asyncio
    async def test_same_region_access(self, access_manager):
        """Test same-region access request"""
        request = await access_manager.create_access_request(
            requester_id="user-003",
            data_id="data-003",
            source_region="af-west-1",
            target_region="af-west-1",
            access_type="read",
            reason="Local access"
        )
        
        assert request.source_region == request.target_region


class TestTenantIsolationInAccessManager:
    """Tests for tenant isolation in access manager (INV-002)"""

    @pytest.mark.asyncio
    async def test_tenant_a_requests_isolated(self, access_manager, tenant_a_config):
        """Test Tenant A requests are isolated"""
        request = await access_manager.create_access_request(
            requester_id=f"{tenant_a_config['tenant_id']}-user-001",
            data_id=f"{tenant_a_config['tenant_id']}-data-001",
            source_region=tenant_a_config["region"],
            target_region="eu-west-1",
            access_type="read",
            reason="Business need"
        )
        
        assert tenant_a_config["tenant_id"] in request.requester_id

    @pytest.mark.asyncio
    async def test_tenant_b_requests_isolated(self, access_manager, tenant_b_config):
        """Test Tenant B requests are isolated"""
        request = await access_manager.create_access_request(
            requester_id=f"{tenant_b_config['tenant_id']}-user-001",
            data_id=f"{tenant_b_config['tenant_id']}-data-001",
            source_region=tenant_b_config["region"],
            target_region="us-east-1",
            access_type="read",
            reason="Business need"
        )
        
        assert tenant_b_config["tenant_id"] in request.requester_id

    @pytest.mark.asyncio
    async def test_cross_tenant_access_prevented(self, access_manager, tenant_a_config, tenant_b_config):
        """Test cross-tenant access is properly tracked"""
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
        
        # Verify requests are separate
        assert request_a.id != request_b.id
        assert request_a.requester_id != request_b.requester_id
        assert request_a.data_id != request_b.data_id
