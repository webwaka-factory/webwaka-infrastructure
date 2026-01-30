"""Region models for multi-region deployment."""

from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class RegionStatus(str, Enum):
    """Region status enumeration."""
    
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    PROVISIONING = "provisioning"
    DECOMMISSIONING = "decommissioning"


class RegionConfig(BaseModel):
    """Region configuration."""
    
    aws_region: str = Field(..., description="AWS region code (e.g., us-east-1)")
    country_code: str = Field(..., description="ISO 3166-1 alpha-2 country code")
    data_center_location: str = Field(..., description="Physical location of data center")
    availability_zones: List[str] = Field(..., description="List of availability zones")
    replication_targets: List[str] = Field(default_factory=list, description="Target regions for replication")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional configuration")


class Region(BaseModel):
    """Region information for multi-region deployment."""
    
    id: str = Field(..., description="Unique region identifier")
    name: str = Field(..., description="Human-readable region name")
    aws_region: str = Field(..., description="AWS region code")
    country_code: str = Field(..., description="Country code")
    status: RegionStatus = Field(default=RegionStatus.PROVISIONING)
    config: RegionConfig = Field(..., description="Region configuration")
    capacity: Dict[str, Any] = Field(default_factory=dict, description="Region capacity metrics")
    health_status: Dict[str, Any] = Field(default_factory=dict, description="Region health metrics")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "region-us-east-1",
                "name": "US East (N. Virginia)",
                "aws_region": "us-east-1",
                "country_code": "US",
                "status": "active",
                "config": {
                    "aws_region": "us-east-1",
                    "country_code": "US",
                    "data_center_location": "Virginia, USA",
                    "availability_zones": ["us-east-1a", "us-east-1b", "us-east-1c"]
                }
            }
        }


class RegionCreateRequest(BaseModel):
    """Request model for creating a region."""
    
    name: str = Field(..., description="Region name")
    aws_region: str = Field(..., description="AWS region code")
    country_code: str = Field(..., description="Country code")
    data_center_location: str = Field(..., description="Data center location")
    availability_zones: List[str] = Field(..., description="Availability zones")
    replication_targets: Optional[List[str]] = Field(None, description="Replication targets")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "US East (N. Virginia)",
                "aws_region": "us-east-1",
                "country_code": "US",
                "data_center_location": "Virginia, USA",
                "availability_zones": ["us-east-1a", "us-east-1b", "us-east-1c"]
            }
        }


class RegionResponse(BaseModel):
    """Response model for region operations."""
    
    id: str
    name: str
    aws_region: str
    country_code: str
    status: RegionStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "region-us-east-1",
                "name": "US East (N. Virginia)",
                "aws_region": "us-east-1",
                "country_code": "US",
                "status": "active",
                "created_at": "2024-01-30T10:00:00Z",
                "updated_at": "2024-01-30T10:00:00Z"
            }
        }
