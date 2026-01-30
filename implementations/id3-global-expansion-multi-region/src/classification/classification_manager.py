"""Data classification management."""

import logging
from typing import Optional, List, Dict
from datetime import datetime

from ..models.classification import DataClassification, ClassificationLevel


logger = logging.getLogger(__name__)


class ClassificationManager:
    """Manages data classification."""
    
    def __init__(self):
        """Initialize the classification manager."""
        self.classifications: Dict[str, DataClassification] = {}
        self.data_classifications: Dict[str, str] = {}  # data_id -> classification_id
        self.classification_counter = 0
    
    async def classify_data(
        self,
        data_id: str,
        classification_level: ClassificationLevel,
        data_type: str,
        sensitivity: str = "medium",
        retention_period_days: Optional[int] = None,
        encryption_required: bool = True,
        pii_present: bool = False,
        requires_audit_log: bool = True,
        classified_by: Optional[str] = None
    ) -> DataClassification:
        """Classify data.
        
        Args:
            data_id: Data ID
            classification_level: Classification level
            data_type: Type of data
            sensitivity: Sensitivity level
            retention_period_days: Retention period
            encryption_required: Whether encryption is required
            pii_present: Whether PII is present
            requires_audit_log: Whether audit logging is required
            classified_by: User who classified the data
            
        Returns:
            Classification record
        """
        logger.info(f"Classifying data {data_id} as {classification_level}")
        
        self.classification_counter += 1
        classification_id = f"class-{self.classification_counter:03d}"
        
        classification = DataClassification(
            id=classification_id,
            data_id=data_id,
            classification_level=classification_level,
            data_type=data_type,
            sensitivity=sensitivity,
            retention_period_days=retention_period_days,
            encryption_required=encryption_required,
            pii_present=pii_present,
            requires_audit_log=requires_audit_log,
            classified_by=classified_by
        )
        
        self.classifications[classification_id] = classification
        self.data_classifications[data_id] = classification_id
        
        logger.info(f"Data {data_id} classified as {classification_level}")
        return classification
    
    def get_classification(self, classification_id: str) -> Optional[DataClassification]:
        """Get classification by ID.
        
        Args:
            classification_id: Classification ID
            
        Returns:
            Classification or None if not found
        """
        return self.classifications.get(classification_id)
    
    def get_data_classification(self, data_id: str) -> Optional[DataClassification]:
        """Get classification for data.
        
        Args:
            data_id: Data ID
            
        Returns:
            Classification or None if not found
        """
        classification_id = self.data_classifications.get(data_id)
        if classification_id:
            return self.classifications.get(classification_id)
        return None
    
    def list_classifications(self) -> List[DataClassification]:
        """List all classifications.
        
        Returns:
            List of classifications
        """
        return list(self.classifications.values())
    
    def list_classifications_by_level(
        self,
        level: ClassificationLevel
    ) -> List[DataClassification]:
        """List classifications by level.
        
        Args:
            level: Classification level
            
        Returns:
            List of classifications with the specified level
        """
        return [c for c in self.classifications.values() if c.classification_level == level]
    
    def list_pii_data(self) -> List[DataClassification]:
        """List all data containing PII.
        
        Returns:
            List of classifications with PII
        """
        return [c for c in self.classifications.values() if c.pii_present]
    
    async def update_classification(
        self,
        classification_id: str,
        **updates
    ) -> Optional[DataClassification]:
        """Update a classification.
        
        Args:
            classification_id: Classification ID
            **updates: Fields to update
            
        Returns:
            Updated classification or None if not found
        """
        logger.info(f"Updating classification {classification_id}")
        
        classification = self.classifications.get(classification_id)
        if not classification:
            logger.warning(f"Classification {classification_id} not found")
            return None
        
        # Update allowed fields
        if "sensitivity" in updates:
            classification.sensitivity = updates["sensitivity"]
        if "retention_period_days" in updates:
            classification.retention_period_days = updates["retention_period_days"]
        if "encryption_required" in updates:
            classification.encryption_required = updates["encryption_required"]
        if "pii_present" in updates:
            classification.pii_present = updates["pii_present"]
        if "requires_audit_log" in updates:
            classification.requires_audit_log = updates["requires_audit_log"]
        
        self.classifications[classification_id] = classification
        logger.info(f"Classification {classification_id} updated successfully")
        return classification
