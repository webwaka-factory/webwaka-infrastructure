"""Deployment models for the Enterprise Deployment Automation system."""

from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class DeploymentStatus(str, Enum):
    """Deployment status enumeration."""
    
    PENDING = "pending"
    COMPILING = "compiling"
    COMPILED = "compiled"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"


class DeploymentManifest(BaseModel):
    """Deployment manifest containing version specifications and configurations."""
    
    id: str = Field(..., description="Unique manifest identifier")
    version: str = Field(..., description="Manifest version")
    platform_version: str = Field(..., description="Platform version to deploy")
    suites: Dict[str, str] = Field(default_factory=dict, description="Suite name to version mapping")
    capabilities: Dict[str, str] = Field(default_factory=dict, description="Capability name to version mapping")
    configuration: Dict[str, Any] = Field(default_factory=dict, description="Deployment configuration")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "manifest-001",
                "version": "1.0.0",
                "platform_version": "2.0.0",
                "suites": {
                    "commerce": "1.5.0",
                    "mlas": "1.2.0"
                },
                "capabilities": {
                    "reporting": "1.0.0",
                    "content_management": "1.1.0"
                },
                "configuration": {
                    "environment": "production",
                    "replicas": 3
                }
            }
        }


class Deployment(BaseModel):
    """Deployment record representing a deployment operation."""
    
    id: str = Field(..., description="Unique deployment identifier")
    manifest_id: str = Field(..., description="Associated deployment manifest ID")
    instance_id: str = Field(..., description="Target enterprise instance ID")
    status: DeploymentStatus = Field(default=DeploymentStatus.PENDING)
    previous_manifest_id: Optional[str] = Field(None, description="Previous manifest for rollback reference")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    logs: List[str] = Field(default_factory=list, description="Deployment logs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "deploy-001",
                "manifest_id": "manifest-001",
                "instance_id": "instance-prod-01",
                "status": "deployed",
                "previous_manifest_id": "manifest-000",
                "created_at": "2024-01-30T10:00:00Z",
                "started_at": "2024-01-30T10:05:00Z",
                "completed_at": "2024-01-30T10:15:00Z"
            }
        }


class DeploymentRequest(BaseModel):
    """Request model for creating a new deployment."""
    
    manifest_id: str = Field(..., description="Deployment manifest ID")
    instance_id: str = Field(..., description="Target enterprise instance ID")
    dry_run: bool = Field(False, description="Run deployment in dry-run mode")
    skip_validation: bool = Field(False, description="Skip pre-deployment validation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "manifest_id": "manifest-001",
                "instance_id": "instance-prod-01",
                "dry_run": False,
                "skip_validation": False
            }
        }


class DeploymentResponse(BaseModel):
    """Response model for deployment operations."""
    
    id: str
    status: DeploymentStatus
    manifest_id: str
    instance_id: str
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "deploy-001",
                "status": "deployed",
                "manifest_id": "manifest-001",
                "instance_id": "instance-prod-01",
                "created_at": "2024-01-30T10:00:00Z",
                "started_at": "2024-01-30T10:05:00Z",
                "completed_at": "2024-01-30T10:15:00Z"
            }
        }
