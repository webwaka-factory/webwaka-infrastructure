"""
Unit Tests for ID-3 Access Control Models

Tests for AccessRequest, AccessGrant, and AccessAuditLog models.
Enforces INV-002 (Strict Tenant Isolation).
"""

import pytest
from datetime import datetime, timedelta

from src.models.access_control import (
    AccessRequest, AccessGrant, AccessRequestStatus, AccessAuditLog
)


class TestAccessRequest:
    """Tests for AccessRequest model"""

    def test_create_access_request(self, sample_access_request):
        """Test creating an access request"""
        request = AccessRequest(
            id="access-req-001",
            **sample_access_request
        )
        
        assert request.id == "access-req-001"
        assert request.requester_id == "user-001"
        assert request.data_id == "data-001"
        assert request.status == AccessRequestStatus.PENDING

    def test_access_request_regions(self, sample_access_request):
        """Test access request regions"""
        request = AccessRequest(
            id="access-req-001",
            **sample_access_request
        )
        
        assert request.source_region == "us-east-1"
        assert request.target_region == "eu-west-1"

    def test_access_request_reason(self, sample_access_request):
        """Test access request reason"""
        request = AccessRequest(
            id="access-req-001",
            **sample_access_request
        )
        
        assert request.reason == "Customer support investigation"


class TestAccessRequestStatus:
    """Tests for AccessRequestStatus enum"""

    def test_access_request_status_values(self):
        """Test access request status values"""
        assert AccessRequestStatus.PENDING.value == "pending"
        assert AccessRequestStatus.APPROVED.value == "approved"
        assert AccessRequestStatus.REJECTED.value == "rejected"
        assert AccessRequestStatus.EXPIRED.value == "expired"
        assert AccessRequestStatus.REVOKED.value == "revoked"

    def test_access_request_status_transitions(self, sample_access_request):
        """Test access request status transitions"""
        request = AccessRequest(
            id="access-req-001",
            **sample_access_request
        )
        
        # Pending -> Approved
        request.status = AccessRequestStatus.APPROVED
        assert request.status == AccessRequestStatus.APPROVED
        
        # Can also be rejected
        request.status = AccessRequestStatus.REJECTED
        assert request.status == AccessRequestStatus.REJECTED


class TestAccessGrant:
    """Tests for AccessGrant model"""

    def test_create_access_grant(self, sample_access_request):
        """Test creating an access grant"""
        grant = AccessGrant(
            id="grant-001",
            request_id="access-req-001",
            user_id=sample_access_request["requester_id"],
            data_id=sample_access_request["data_id"],
            source_region=sample_access_request["source_region"],
            target_region=sample_access_request["target_region"],
            access_type=sample_access_request["access_type"]
        )
        
        assert grant.id == "grant-001"
        assert grant.user_id == "user-001"
        assert grant.access_type == "read"

    def test_access_grant_expiration(self, sample_access_request):
        """Test access grant expiration"""
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        grant = AccessGrant(
            id="grant-001",
            request_id="access-req-001",
            user_id=sample_access_request["requester_id"],
            data_id=sample_access_request["data_id"],
            source_region=sample_access_request["source_region"],
            target_region=sample_access_request["target_region"],
            access_type=sample_access_request["access_type"],
            expires_at=expires_at
        )
        
        assert grant.expires_at is not None
        assert grant.expires_at > datetime.utcnow()

    def test_access_grant_revocation(self, sample_access_request):
        """Test access grant revocation"""
        grant = AccessGrant(
            id="grant-001",
            request_id="access-req-001",
            user_id=sample_access_request["requester_id"],
            data_id=sample_access_request["data_id"],
            source_region=sample_access_request["source_region"],
            target_region=sample_access_request["target_region"],
            access_type=sample_access_request["access_type"]
        )
        
        # Revoke grant
        grant.revoked_at = datetime.utcnow()
        grant.revoked_by = "admin"
        
        assert grant.revoked_at is not None
        assert grant.revoked_by == "admin"


class TestAccessAuditLog:
    """Tests for AccessAuditLog model"""

    def test_create_audit_log(self):
        """Test creating an audit log entry"""
        log = AccessAuditLog(
            id="audit-001",
            user_id="user-001",
            action="access",
            data_id="data-001",
            source_region="us-east-1",
            target_region="eu-west-1",
            status="success"
        )
        
        assert log.id == "audit-001"
        assert log.action == "access"
        assert log.status == "success"

    def test_audit_log_with_details(self):
        """Test audit log with details"""
        log = AccessAuditLog(
            id="audit-001",
            user_id="user-001",
            action="request",
            data_id="data-001",
            source_region="us-east-1",
            target_region="eu-west-1",
            status="success",
            details={
                "request_id": "access-req-001",
                "reason": "Customer support"
            },
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )
        
        assert log.details["request_id"] == "access-req-001"
        assert log.ip_address == "192.168.1.1"


class TestTenantIsolation:
    """Tests for tenant isolation (INV-002)"""

    def test_tenant_a_access_request(self, tenant_a_config):
        """Test Tenant A access request"""
        request = AccessRequest(
            id="access-req-001",
            requester_id=f"{tenant_a_config['tenant_id']}-user-001",
            data_id=f"{tenant_a_config['tenant_id']}-data-001",
            source_region=tenant_a_config["region"],
            target_region="eu-west-1",
            access_type="read",
            reason="Business need"
        )
        
        assert tenant_a_config["tenant_id"] in request.requester_id
        assert tenant_a_config["tenant_id"] in request.data_id

    def test_tenant_b_access_request(self, tenant_b_config):
        """Test Tenant B access request"""
        request = AccessRequest(
            id="access-req-002",
            requester_id=f"{tenant_b_config['tenant_id']}-user-001",
            data_id=f"{tenant_b_config['tenant_id']}-data-001",
            source_region=tenant_b_config["region"],
            target_region="us-east-1",
            access_type="read",
            reason="Business need"
        )
        
        assert tenant_b_config["tenant_id"] in request.requester_id
        assert tenant_b_config["tenant_id"] in request.data_id

    def test_tenant_isolation_in_grants(self, tenant_a_config, tenant_b_config):
        """Test tenant isolation in access grants"""
        grant_a = AccessGrant(
            id="grant-001",
            request_id="access-req-001",
            user_id=f"{tenant_a_config['tenant_id']}-user-001",
            data_id=f"{tenant_a_config['tenant_id']}-data-001",
            source_region=tenant_a_config["region"],
            target_region="eu-west-1",
            access_type="read"
        )
        
        grant_b = AccessGrant(
            id="grant-002",
            request_id="access-req-002",
            user_id=f"{tenant_b_config['tenant_id']}-user-001",
            data_id=f"{tenant_b_config['tenant_id']}-data-001",
            source_region=tenant_b_config["region"],
            target_region="us-east-1",
            access_type="read"
        )
        
        # Verify tenant isolation
        assert tenant_a_config["tenant_id"] in grant_a.user_id
        assert tenant_b_config["tenant_id"] in grant_b.user_id
        assert grant_a.user_id != grant_b.user_id
