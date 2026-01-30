"""Residency policy enforcement."""

import logging
from typing import Dict, Optional

from .residency_manager import ResidencyManager


logger = logging.getLogger(__name__)


class ResidencyEnforcer:
    """Enforces residency policies."""
    
    def __init__(self, residency_manager: ResidencyManager):
        """Initialize the residency enforcer.
        
        Args:
            residency_manager: Residency manager instance
        """
        self.residency_manager = residency_manager
    
    async def enforce_residency(
        self,
        policy_id: str,
        data_id: str,
        target_region: str
    ) -> Dict:
        """Enforce residency policy for data.
        
        Args:
            policy_id: Policy ID
            data_id: Data ID
            target_region: Target region
            
        Returns:
            Enforcement result
        """
        logger.info(f"Enforcing residency for data {data_id} in region {target_region}")
        
        validation = await self.residency_manager.validate_region_compliance(
            policy_id,
            target_region
        )
        
        if not validation["compliant"]:
            logger.warning(f"Residency violation: {validation.get('reason')}")
            return {
                "allowed": False,
                "data_id": data_id,
                "target_region": target_region,
                "reason": validation.get("reason", "Residency policy violation")
            }
        
        logger.info(f"Residency check passed for data {data_id}")
        return {
            "allowed": True,
            "data_id": data_id,
            "target_region": target_region,
            "policy_id": policy_id
        }
    
    async def check_cross_border_access(
        self,
        source_region: str,
        target_region: str,
        policy_id: str
    ) -> Dict:
        """Check if cross-border access is allowed.
        
        Args:
            source_region: Source region
            target_region: Target region
            policy_id: Policy ID
            
        Returns:
            Access check result
        """
        logger.info(f"Checking cross-border access from {source_region} to {target_region}")
        
        policy = self.residency_manager.get_policy(policy_id)
        if not policy:
            return {"allowed": False, "reason": "Policy not found"}
        
        if not policy.enabled:
            return {"allowed": False, "reason": "Policy is disabled"}
        
        # Check if cross-border access is allowed for this policy
        if source_region == target_region:
            return {"allowed": True, "reason": "Same region access"}
        
        # For mandatory policies, cross-border access requires explicit approval
        if policy.policy_type.value == "mandatory":
            return {
                "allowed": False,
                "reason": "Cross-border access requires explicit approval for mandatory policies"
            }
        
        return {"allowed": True, "reason": "Cross-border access permitted"}
