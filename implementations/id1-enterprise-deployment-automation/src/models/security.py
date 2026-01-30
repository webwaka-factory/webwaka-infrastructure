"""Security patch models."""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class PatchStatus(str, Enum):
    """Security patch status enumeration."""
    
    AVAILABLE = "available"
    APPLIED = "applied"
    FAILED = "failed"
    SUPERSEDED = "superseded"
    SKIPPED = "skipped"


class SeverityLevel(str, Enum):
    """Security patch severity levels."""
    
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SecurityPatch(BaseModel):
    """Security patch information."""
    
    id: str = Field(..., description="Unique patch identifier")
    cve_ids: List[str] = Field(default_factory=list, description="Associated CVE IDs")
    component_type: str = Field(..., description="Component type (platform, suite, capability)")
    component_name: str = Field(..., description="Component name")
    affected_versions: List[str] = Field(..., description="List of affected versions")
    patched_version: str = Field(..., description="Version with patch applied")
    severity: SeverityLevel = Field(..., description="Patch severity level")
    description: str = Field(..., description="Patch description")
    release_date: datetime = Field(..., description="Patch release date")
    is_mandatory: bool = Field(default=True, description="Whether patch is mandatory")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "patch-001",
                "cve_ids": ["CVE-2024-0001"],
                "component_type": "platform",
                "component_name": "webwaka-platform",
                "affected_versions": ["1.9.0", "1.9.1"],
                "patched_version": "1.9.2",
                "severity": "critical",
                "description": "SQL injection vulnerability in user authentication",
                "release_date": "2024-01-30T00:00:00Z",
                "is_mandatory": True
            }
        }


class PatchApplication(BaseModel):
    """Security patch application record."""
    
    id: str = Field(..., description="Unique application record ID")
    instance_id: str = Field(..., description="Associated instance ID")
    patch_id: str = Field(..., description="Applied patch ID")
    status: PatchStatus = Field(default=PatchStatus.AVAILABLE)
    applied_at: Optional[datetime] = None
    applied_by: Optional[str] = None
    error_message: Optional[str] = None
    logs: List[str] = Field(default_factory=list, description="Application logs")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "app-001",
                "instance_id": "instance-prod-01",
                "patch_id": "patch-001",
                "status": "applied",
                "applied_at": "2024-01-30T10:00:00Z",
                "applied_by": "system"
            }
        }


class PatchApplicationRequest(BaseModel):
    """Request model for applying a security patch."""
    
    patch_id: str = Field(..., description="Patch ID to apply")
    dry_run: bool = Field(False, description="Run in dry-run mode")
    force: bool = Field(False, description="Force application even if policy doesn't allow")
    
    class Config:
        json_schema_extra = {
            "example": {
                "patch_id": "patch-001",
                "dry_run": False,
                "force": False
            }
        }


class PatchApplicationResponse(BaseModel):
    """Response model for patch application."""
    
    id: str
    instance_id: str
    patch_id: str
    status: PatchStatus
    applied_at: Optional[datetime]
    error_message: Optional[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "app-001",
                "instance_id": "instance-prod-01",
                "patch_id": "patch-001",
                "status": "applied",
                "applied_at": "2024-01-30T10:00:00Z"
            }
        }


class PatchStatusResponse(BaseModel):
    """Response model for patch status."""
    
    instance_id: str
    total_patches: int
    applied_patches: int
    pending_patches: int
    failed_patches: int
    critical_patches: int
    patches: List[PatchApplicationResponse] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "instance_id": "instance-prod-01",
                "total_patches": 5,
                "applied_patches": 3,
                "pending_patches": 1,
                "failed_patches": 1,
                "critical_patches": 1
            }
        }
