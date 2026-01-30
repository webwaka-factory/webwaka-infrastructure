"""Update channel policy models."""

from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class PolicyType(str, Enum):
    """Update channel policy types."""
    
    AUTO_UPDATE = "auto_update"
    MANUAL_APPROVAL = "manual_approval"
    FROZEN = "frozen"


class UpdateChannelPolicy(BaseModel):
    """Update channel policy configuration."""
    
    id: str = Field(..., description="Unique policy identifier")
    instance_id: str = Field(..., description="Associated instance ID")
    policy_type: PolicyType = Field(..., description="Type of update policy")
    enabled: bool = Field(default=True, description="Whether policy is active")
    description: Optional[str] = Field(None, description="Policy description")
    
    # Auto-update specific settings
    auto_update_schedule: Optional[str] = Field(None, description="Cron expression for auto-updates")
    auto_update_maintenance_window: Optional[Dict[str, Any]] = Field(None, description="Maintenance window config")
    
    # Manual approval specific settings
    approval_required_roles: list[str] = Field(default_factory=list, description="Roles that can approve")
    approval_timeout_hours: int = Field(default=72, description="Approval timeout in hours")
    
    # Frozen specific settings
    frozen_versions: Dict[str, str] = Field(default_factory=dict, description="Pinned versions")
    allow_security_patches: bool = Field(default=True, description="Allow security patches in frozen mode")
    
    # Common settings
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "policy-001",
                "instance_id": "instance-prod-01",
                "policy_type": "manual_approval",
                "enabled": True,
                "description": "Production instance requires manual approval",
                "approval_required_roles": ["admin", "devops"],
                "approval_timeout_hours": 72
            }
        }


class PolicyUpdateRequest(BaseModel):
    """Request model for updating a policy."""
    
    policy_type: Optional[PolicyType] = None
    enabled: Optional[bool] = None
    description: Optional[str] = None
    auto_update_schedule: Optional[str] = None
    auto_update_maintenance_window: Optional[Dict[str, Any]] = None
    approval_required_roles: Optional[list[str]] = None
    approval_timeout_hours: Optional[int] = None
    frozen_versions: Optional[Dict[str, str]] = None
    allow_security_patches: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "policy_type": "manual_approval",
                "enabled": True,
                "approval_required_roles": ["admin", "devops"],
                "approval_timeout_hours": 48
            }
        }


class PolicyResponse(BaseModel):
    """Response model for policy operations."""
    
    id: str
    instance_id: str
    policy_type: PolicyType
    enabled: bool
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "policy-001",
                "instance_id": "instance-prod-01",
                "policy_type": "manual_approval",
                "enabled": True,
                "description": "Production instance requires manual approval",
                "created_at": "2024-01-30T10:00:00Z",
                "updated_at": "2024-01-30T10:00:00Z"
            }
        }
