"""Cross-border access enforcement."""

import logging
from typing import Dict, Optional
from datetime import datetime

from .access_manager import AccessManager


logger = logging.getLogger(__name__)


class AccessEnforcer:
    """Enforces cross-border access controls."""
    
    def __init__(self, access_manager: AccessManager):
        """Initialize the access enforcer.
        
        Args:
            access_manager: Access manager instance
        """
        self.access_manager = access_manager
    
    async def check_access_permission(
        self,
        user_id: str,
        data_id: str,
        source_region: str,
        target_region: str,
        access_type: str
    ) -> Dict:
        """Check if user has permission to access data across regions.
        
        Args:
            user_id: User ID
            data_id: Data ID
            source_region: Source region
            target_region: Target region
            access_type: Type of access
            
        Returns:
            Permission check result
        """
        logger.info(f"Checking access permission for {user_id} to {data_id}")
        
        # Check for active grants
        grants = self.access_manager.list_access_grants(user_id)
        
        for grant in grants:
            if (grant.data_id == data_id and
                grant.source_region == source_region and
                grant.target_region == target_region and
                grant.access_type == access_type):
                
                # Check if grant is expired
                if grant.expires_at and datetime.utcnow() > grant.expires_at:
                    logger.warning(f"Grant {grant.id} has expired")
                    continue
                
                logger.info(f"Access granted for {user_id} to {data_id}")
                return {
                    "allowed": True,
                    "grant_id": grant.id,
                    "expires_at": grant.expires_at
                }
        
        logger.warning(f"No valid grant found for {user_id} to {data_id}")
        return {
            "allowed": False,
            "reason": "No valid access grant found"
        }
    
    async def check_cross_border_access(
        self,
        source_region: str,
        target_region: str
    ) -> Dict:
        """Check if cross-border access is allowed between regions.
        
        Args:
            source_region: Source region
            target_region: Target region
            
        Returns:
            Access check result
        """
        logger.info(f"Checking cross-border access from {source_region} to {target_region}")
        
        if source_region == target_region:
            return {"allowed": True, "reason": "Same region access"}
        
        # Cross-border access is allowed but requires audit logging
        return {
            "allowed": True,
            "reason": "Cross-border access allowed with audit logging",
            "requires_audit": True
        }
