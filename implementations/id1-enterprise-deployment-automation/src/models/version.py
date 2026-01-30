"""Version management models."""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class Version(BaseModel):
    """Version information."""
    
    id: str = Field(..., description="Unique version identifier")
    component_type: str = Field(..., description="Type of component (platform, suite, capability)")
    component_name: str = Field(..., description="Component name")
    version_string: str = Field(..., description="Semantic version string")
    release_date: datetime = Field(..., description="Release date")
    is_stable: bool = Field(default=True, description="Whether version is stable")
    is_security_patch: bool = Field(default=False, description="Whether this is a security patch")
    dependencies: Dict[str, str] = Field(default_factory=dict, description="Version dependencies")
    changelog: Optional[str] = Field(None, description="Release notes/changelog")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "ver-001",
                "component_type": "platform",
                "component_name": "webwaka-platform",
                "version_string": "2.0.0",
                "release_date": "2024-01-30T00:00:00Z",
                "is_stable": True,
                "is_security_patch": False,
                "dependencies": {
                    "commerce-suite": "1.5.0"
                }
            }
        }


class VersionConstraint(BaseModel):
    """Version constraint specification."""
    
    component_type: str = Field(..., description="Component type")
    component_name: str = Field(..., description="Component name")
    constraint: str = Field(..., description="Version constraint (e.g., '>=1.0.0,<2.0.0')")
    
    class Config:
        json_schema_extra = {
            "example": {
                "component_type": "suite",
                "component_name": "commerce",
                "constraint": ">=1.5.0,<2.0.0"
            }
        }


class VersionPin(BaseModel):
    """Version pin for locking specific versions."""
    
    id: str = Field(..., description="Unique pin identifier")
    instance_id: str = Field(..., description="Associated instance ID")
    component_type: str = Field(..., description="Component type (platform, suite, capability)")
    component_name: str = Field(..., description="Component name")
    pinned_version: str = Field(..., description="Pinned version string")
    reason: Optional[str] = Field(None, description="Reason for pinning")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Pin expiration date")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "pin-001",
                "instance_id": "instance-prod-01",
                "component_type": "suite",
                "component_name": "commerce",
                "pinned_version": "1.5.0",
                "reason": "Compatibility with legacy system",
                "created_at": "2024-01-30T10:00:00Z"
            }
        }


class VersionPinRequest(BaseModel):
    """Request model for creating a version pin."""
    
    component_type: str = Field(..., description="Component type")
    component_name: str = Field(..., description="Component name")
    pinned_version: str = Field(..., description="Version to pin")
    reason: Optional[str] = None
    expires_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "component_type": "suite",
                "component_name": "commerce",
                "pinned_version": "1.5.0",
                "reason": "Compatibility with legacy system"
            }
        }


class VersionCompatibilityCheck(BaseModel):
    """Version compatibility check request."""
    
    platform_version: str = Field(..., description="Platform version")
    suites: Dict[str, str] = Field(..., description="Suite versions")
    capabilities: Dict[str, str] = Field(..., description="Capability versions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "platform_version": "2.0.0",
                "suites": {
                    "commerce": "1.5.0",
                    "mlas": "1.2.0"
                },
                "capabilities": {
                    "reporting": "1.0.0"
                }
            }
        }


class VersionCompatibilityResult(BaseModel):
    """Version compatibility check result."""
    
    is_compatible: bool = Field(..., description="Whether versions are compatible")
    compatible_versions: List[str] = Field(default_factory=list, description="List of compatible versions")
    incompatibilities: List[str] = Field(default_factory=list, description="List of incompatibilities")
    warnings: List[str] = Field(default_factory=list, description="Compatibility warnings")
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_compatible": True,
                "compatible_versions": ["2.0.0"],
                "incompatibilities": [],
                "warnings": ["Commerce suite 1.5.0 has known issues with reporting 1.0.0"]
            }
        }
