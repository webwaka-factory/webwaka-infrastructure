"""Cross-border access control models."""

from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class AccessRequestStatus(str, Enum):
    """Access request status enumeration."""
    
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    REVOKED = "revoked"


class AccessRequest(BaseModel):
    """Cross-border access request."""
    
    id: str = Field(..., description="Unique request identifier")
    requester_id: str = Field(..., description="User ID requesting access")
    data_id: str = Field(..., description="Data ID being requested")
    source_region: str = Field(..., description="Source region")
    target_region: str = Field(..., description="Target region for access")
    access_type: str = Field(..., description="Type of access (read, write, export)")
    reason: str = Field(..., description="Business reason for access")
    status: AccessRequestStatus = Field(default=AccessRequestStatus.PENDING)
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Access expiration time")
    approved_by: Optional[str] = Field(None, description="Approver user ID")
    approved_at: Optional[datetime] = Field(None, description="Approval timestamp")
    rejection_reason: Optional[str] = Field(None, description="Rejection reason if rejected")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "access-req-001",
                "requester_id": "user-123",
                "data_id": "data-456",
                "source_region": "us-east-1",
                "target_region": "eu-west-1",
                "access_type": "read",
                "reason": "Customer support investigation",
                "status": "pending",
                "requested_at": "2024-01-30T10:00:00Z"
            }
        }


class AccessGrant(BaseModel):
    """Approved cross-border access grant."""
    
    id: str = Field(..., description="Unique grant identifier")
    request_id: str = Field(..., description="Associated access request ID")
    user_id: str = Field(..., description="User ID with access")
    data_id: str = Field(..., description="Data ID with access")
    source_region: str = Field(..., description="Source region")
    target_region: str = Field(..., description="Target region")
    access_type: str = Field(..., description="Type of access granted")
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Grant expiration time")
    revoked_at: Optional[datetime] = Field(None, description="Revocation timestamp if revoked")
    revoked_by: Optional[str] = Field(None, description="User who revoked access")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "grant-001",
                "request_id": "access-req-001",
                "user_id": "user-123",
                "data_id": "data-456",
                "source_region": "us-east-1",
                "target_region": "eu-west-1",
                "access_type": "read",
                "granted_at": "2024-01-30T10:15:00Z"
            }
        }


class AccessAuditLog(BaseModel):
    """Audit log for cross-border access."""
    
    id: str = Field(..., description="Unique log entry ID")
    user_id: str = Field(..., description="User ID performing action")
    action: str = Field(..., description="Action performed (request, approve, revoke, access)")
    data_id: str = Field(..., description="Data ID involved")
    source_region: str = Field(..., description="Source region")
    target_region: str = Field(..., description="Target region")
    status: str = Field(..., description="Action status (success, failure)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = Field(default_factory=dict, description="Action details")
    ip_address: Optional[str] = Field(None, description="IP address of requester")
    user_agent: Optional[str] = Field(None, description="User agent string")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "audit-001",
                "user_id": "user-123",
                "action": "access",
                "data_id": "data-456",
                "source_region": "us-east-1",
                "target_region": "eu-west-1",
                "status": "success",
                "timestamp": "2024-01-30T10:20:00Z"
            }
        }


class AccessRequestCreateRequest(BaseModel):
    """Request model for creating an access request."""
    
    data_id: str = Field(..., description="Data ID to access")
    target_region: str = Field(..., description="Target region")
    access_type: str = Field(..., description="Type of access")
    reason: str = Field(..., description="Business reason")
    expires_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "data_id": "data-456",
                "target_region": "eu-west-1",
                "access_type": "read",
                "reason": "Customer support investigation"
            }
        }


class AccessApprovalRequest(BaseModel):
    """Request model for approving access."""
    
    request_id: str = Field(..., description="Access request ID")
    approved: bool = Field(..., description="Whether to approve")
    reason: Optional[str] = Field(None, description="Approval or rejection reason")
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "access-req-001",
                "approved": True,
                "reason": "Approved for customer support"
            }
        }
