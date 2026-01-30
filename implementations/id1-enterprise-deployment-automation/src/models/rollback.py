"""Rollback operation models."""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class RollbackStatus(str, Enum):
    """Rollback operation status."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RollbackRecord(BaseModel):
    """Rollback operation record."""
    
    id: str = Field(..., description="Unique rollback operation ID")
    instance_id: str = Field(..., description="Associated instance ID")
    from_manifest_id: str = Field(..., description="Current manifest ID")
    to_manifest_id: str = Field(..., description="Target manifest ID to rollback to")
    status: RollbackStatus = Field(default=RollbackStatus.PENDING)
    reason: Optional[str] = Field(None, description="Reason for rollback")
    initiated_by: Optional[str] = Field(None, description="User who initiated rollback")
    initiated_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    logs: List[str] = Field(default_factory=list, description="Rollback operation logs")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "rollback-001",
                "instance_id": "instance-prod-01",
                "from_manifest_id": "manifest-002",
                "to_manifest_id": "manifest-001",
                "status": "completed",
                "reason": "Deployment caused performance degradation",
                "initiated_by": "admin@example.com",
                "initiated_at": "2024-01-30T10:00:00Z",
                "completed_at": "2024-01-30T10:15:00Z"
            }
        }


class RollbackRequest(BaseModel):
    """Request model for initiating a rollback."""
    
    to_manifest_id: str = Field(..., description="Target manifest ID")
    reason: Optional[str] = Field(None, description="Reason for rollback")
    dry_run: bool = Field(False, description="Run rollback in dry-run mode")
    skip_validation: bool = Field(False, description="Skip pre-rollback validation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "to_manifest_id": "manifest-001",
                "reason": "Deployment caused performance degradation",
                "dry_run": False,
                "skip_validation": False
            }
        }


class RollbackResponse(BaseModel):
    """Response model for rollback operations."""
    
    id: str
    instance_id: str
    from_manifest_id: str
    to_manifest_id: str
    status: RollbackStatus
    initiated_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "rollback-001",
                "instance_id": "instance-prod-01",
                "from_manifest_id": "manifest-002",
                "to_manifest_id": "manifest-001",
                "status": "completed",
                "initiated_at": "2024-01-30T10:00:00Z",
                "completed_at": "2024-01-30T10:15:00Z"
            }
        }


class ManifestVersion(BaseModel):
    """Historical manifest version for rollback reference."""
    
    id: str = Field(..., description="Manifest ID")
    version: str = Field(..., description="Manifest version")
    deployed_at: datetime = Field(..., description="Deployment timestamp")
    deployment_id: str = Field(..., description="Associated deployment ID")
    status: str = Field(..., description="Deployment status")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "manifest-001",
                "version": "1.0.0",
                "deployed_at": "2024-01-30T09:00:00Z",
                "deployment_id": "deploy-001",
                "status": "deployed"
            }
        }


class RollbackHistory(BaseModel):
    """Rollback history for an instance."""
    
    instance_id: str = Field(..., description="Instance ID")
    total_rollbacks: int = Field(..., description="Total rollback operations")
    successful_rollbacks: int = Field(..., description="Successful rollbacks")
    failed_rollbacks: int = Field(..., description="Failed rollbacks")
    recent_rollbacks: List[RollbackResponse] = Field(default_factory=list, description="Recent rollback operations")
    available_manifests: List[ManifestVersion] = Field(default_factory=list, description="Available manifests for rollback")
    
    class Config:
        json_schema_extra = {
            "example": {
                "instance_id": "instance-prod-01",
                "total_rollbacks": 2,
                "successful_rollbacks": 2,
                "failed_rollbacks": 0,
                "recent_rollbacks": [],
                "available_manifests": []
            }
        }
