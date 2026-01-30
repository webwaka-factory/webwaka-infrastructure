"""Data classification enforcement."""

import logging
from typing import Dict, Optional

from .classification_manager import ClassificationManager
from ..models.classification import ClassificationLevel


logger = logging.getLogger(__name__)


class ClassificationEnforcer:
    """Enforces data classification policies."""
    
    def __init__(self, classification_manager: ClassificationManager):
        """Initialize the classification enforcer.
        
        Args:
            classification_manager: Classification manager instance
        """
        self.classification_manager = classification_manager
    
    async def enforce_classification(
        self,
        data_id: str,
        classification_level: ClassificationLevel
    ) -> Dict:
        """Enforce classification for data.
        
        Args:
            data_id: Data ID
            classification_level: Classification level
            
        Returns:
            Enforcement result
        """
        logger.info(f"Enforcing classification for data {data_id}")
        
        existing = self.classification_manager.get_data_classification(data_id)
        
        if existing:
            logger.warning(f"Data {data_id} is already classified")
            return {
                "enforced": False,
                "data_id": data_id,
                "reason": "Data is already classified",
                "existing_classification": existing.classification_level
            }
        
        logger.info(f"Classification enforcement passed for data {data_id}")
        return {
            "enforced": True,
            "data_id": data_id,
            "classification_level": classification_level
        }
    
    async def check_encryption_requirement(
        self,
        data_id: str
    ) -> Dict:
        """Check if data requires encryption.
        
        Args:
            data_id: Data ID
            
        Returns:
            Encryption requirement check result
        """
        logger.info(f"Checking encryption requirement for data {data_id}")
        
        classification = self.classification_manager.get_data_classification(data_id)
        
        if not classification:
            return {
                "requires_encryption": True,
                "reason": "Data not classified, encryption required by default"
            }
        
        return {
            "requires_encryption": classification.encryption_required,
            "classification_level": classification.classification_level,
            "data_id": data_id
        }
    
    async def check_audit_log_requirement(
        self,
        data_id: str
    ) -> Dict:
        """Check if data requires audit logging.
        
        Args:
            data_id: Data ID
            
        Returns:
            Audit log requirement check result
        """
        logger.info(f"Checking audit log requirement for data {data_id}")
        
        classification = self.classification_manager.get_data_classification(data_id)
        
        if not classification:
            return {
                "requires_audit_log": True,
                "reason": "Data not classified, audit logging required by default"
            }
        
        return {
            "requires_audit_log": classification.requires_audit_log,
            "classification_level": classification.classification_level,
            "data_id": data_id
        }
    
    async def check_retention_compliance(
        self,
        data_id: str
    ) -> Dict:
        """Check retention compliance for data.
        
        Args:
            data_id: Data ID
            
        Returns:
            Retention compliance check result
        """
        logger.info(f"Checking retention compliance for data {data_id}")
        
        classification = self.classification_manager.get_data_classification(data_id)
        
        if not classification:
            return {
                "compliant": False,
                "reason": "Data not classified"
            }
        
        if classification.retention_period_days is None:
            return {
                "compliant": False,
                "reason": "Retention period not set"
            }
        
        return {
            "compliant": True,
            "data_id": data_id,
            "retention_period_days": classification.retention_period_days,
            "classification_level": classification.classification_level
        }
