"""Data classification models."""

from enum import Enum
from typing import Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ClassificationLevel(str, Enum):
    """Data classification levels."""
    
    IDENTITY = "identity"
    TRANSACTIONAL = "transactional"
    OPERATIONAL = "operational"
    CONTENT = "content"
    ANALYTICAL_DERIVED = "analytical_derived"


class DataClassification(BaseModel):
    """Data classification record."""
    
    id: str = Field(..., description="Unique classification identifier")
    data_id: str = Field(..., description="Associated data ID")
    classification_level: ClassificationLevel = Field(..., description="Classification level")
    data_type: str = Field(..., description="Type of data (e.g., user_profile, transaction)")
    sensitivity: str = Field(default="medium", description="Data sensitivity level")
    retention_period_days: Optional[int] = Field(None, description="Retention period in days")
    encryption_required: bool = Field(default=True, description="Whether encryption is required")
    pii_present: bool = Field(default=False, description="Whether PII is present")
    requires_audit_log: bool = Field(default=True, description="Whether audit logging is required")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    classified_at: datetime = Field(default_factory=datetime.utcnow)
    classified_by: Optional[str] = Field(None, description="User who classified the data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "class-001",
                "data_id": "data-12345",
                "classification_level": "identity",
                "data_type": "user_profile",
                "sensitivity": "high",
                "pii_present": True,
                "requires_audit_log": True,
                "classified_at": "2024-01-30T10:00:00Z"
            }
        }


class ClassifyDataRequest(BaseModel):
    """Request model for classifying data."""
    
    data_id: str = Field(..., description="Data ID to classify")
    classification_level: ClassificationLevel = Field(..., description="Classification level")
    data_type: str = Field(..., description="Type of data")
    sensitivity: str = Field(default="medium", description="Sensitivity level")
    retention_period_days: Optional[int] = None
    encryption_required: bool = Field(default=True)
    pii_present: bool = Field(default=False)
    requires_audit_log: bool = Field(default=True)
    
    class Config:
        json_schema_extra = {
            "example": {
                "data_id": "data-12345",
                "classification_level": "identity",
                "data_type": "user_profile",
                "sensitivity": "high",
                "pii_present": True
            }
        }


class ClassificationResponse(BaseModel):
    """Response model for classification operations."""
    
    id: str
    data_id: str
    classification_level: ClassificationLevel
    data_type: str
    sensitivity: str
    encryption_required: bool
    pii_present: bool
    classified_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "class-001",
                "data_id": "data-12345",
                "classification_level": "identity",
                "data_type": "user_profile",
                "sensitivity": "high",
                "encryption_required": True,
                "pii_present": True,
                "classified_at": "2024-01-30T10:00:00Z"
            }
        }
