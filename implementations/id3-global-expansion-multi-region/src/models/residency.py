"""Data residency models."""

from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ResidencyMode(str, Enum):
    """Data residency modes."""
    
    SINGLE_COUNTRY = "single_country"
    REGIONAL = "regional"
    HYBRID = "hybrid"
    FULLY_SOVEREIGN = "fully_sovereign"
    CLIENT_OWNED_SOVEREIGNTY = "client_owned_sovereignty"


class ResidencyPolicyType(str, Enum):
    """Residency policy types."""
    
    MANDATORY = "mandatory"
    PREFERRED = "preferred"
    FLEXIBLE = "flexible"


class ResidencyPolicy(BaseModel):
    """Data residency policy."""
    
    id: str = Field(..., description="Unique policy identifier")
    name: str = Field(..., description="Policy name")
    residency_mode: ResidencyMode = Field(..., description="Residency mode")
    policy_type: ResidencyPolicyType = Field(default=ResidencyPolicyType.MANDATORY)
    description: Optional[str] = Field(None, description="Policy description")
    
    # Single-Country specific
    allowed_countries: List[str] = Field(default_factory=list, description="Allowed countries (ISO codes)")
    
    # Regional specific
    allowed_regions: List[str] = Field(default_factory=list, description="Allowed AWS regions")
    
    # Hybrid specific
    primary_region: Optional[str] = Field(None, description="Primary region for hybrid mode")
    secondary_regions: List[str] = Field(default_factory=list, description="Secondary regions for hybrid mode")
    
    # Fully Sovereign specific
    sovereign_country: Optional[str] = Field(None, description="Sovereign country for fully sovereign mode")
    
    # Client-Owned Sovereignty specific
    client_specified_regions: List[str] = Field(default_factory=list, description="Client-specified regions")
    
    enabled: bool = Field(default=True, description="Whether policy is active")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "policy-001",
                "name": "EU Data Residency",
                "residency_mode": "regional",
                "policy_type": "mandatory",
                "allowed_regions": ["eu-west-1", "eu-central-1"],
                "enabled": True
            }
        }


class ResidencyPolicyCreateRequest(BaseModel):
    """Request model for creating a residency policy."""
    
    name: str = Field(..., description="Policy name")
    residency_mode: ResidencyMode = Field(..., description="Residency mode")
    policy_type: ResidencyPolicyType = Field(default=ResidencyPolicyType.MANDATORY)
    description: Optional[str] = None
    allowed_countries: Optional[List[str]] = None
    allowed_regions: Optional[List[str]] = None
    primary_region: Optional[str] = None
    secondary_regions: Optional[List[str]] = None
    sovereign_country: Optional[str] = None
    client_specified_regions: Optional[List[str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "EU Data Residency",
                "residency_mode": "regional",
                "policy_type": "mandatory",
                "allowed_regions": ["eu-west-1", "eu-central-1"]
            }
        }


class ResidencyPolicyResponse(BaseModel):
    """Response model for residency policy operations."""
    
    id: str
    name: str
    residency_mode: ResidencyMode
    policy_type: ResidencyPolicyType
    enabled: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "policy-001",
                "name": "EU Data Residency",
                "residency_mode": "regional",
                "policy_type": "mandatory",
                "enabled": True,
                "created_at": "2024-01-30T10:00:00Z",
                "updated_at": "2024-01-30T10:00:00Z"
            }
        }
