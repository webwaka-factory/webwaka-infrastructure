"""Residency policy management."""

import logging
from typing import Optional, List, Dict
from datetime import datetime

from ..models.residency import ResidencyPolicy, ResidencyMode, ResidencyPolicyType


logger = logging.getLogger(__name__)


class ResidencyManager:
    """Manages data residency policies."""
    
    def __init__(self):
        """Initialize the residency manager."""
        self.policies: Dict[str, ResidencyPolicy] = {}
        self.policy_counter = 0
    
    async def create_policy(
        self,
        name: str,
        residency_mode: ResidencyMode,
        policy_type: ResidencyPolicyType = ResidencyPolicyType.MANDATORY,
        description: Optional[str] = None,
        **kwargs
    ) -> ResidencyPolicy:
        """Create a residency policy.
        
        Args:
            name: Policy name
            residency_mode: Residency mode
            policy_type: Policy type
            description: Optional description
            **kwargs: Additional policy parameters
            
        Returns:
            Created policy
        """
        logger.info(f"Creating residency policy: {name}")
        
        self.policy_counter += 1
        policy_id = f"policy-{self.policy_counter:03d}"
        
        policy = ResidencyPolicy(
            id=policy_id,
            name=name,
            residency_mode=residency_mode,
            policy_type=policy_type,
            description=description,
            allowed_countries=kwargs.get("allowed_countries", []),
            allowed_regions=kwargs.get("allowed_regions", []),
            primary_region=kwargs.get("primary_region"),
            secondary_regions=kwargs.get("secondary_regions", []),
            sovereign_country=kwargs.get("sovereign_country"),
            client_specified_regions=kwargs.get("client_specified_regions", [])
        )
        
        self.policies[policy_id] = policy
        logger.info(f"Residency policy {policy_id} created successfully")
        
        return policy
    
    def get_policy(self, policy_id: str) -> Optional[ResidencyPolicy]:
        """Get policy by ID.
        
        Args:
            policy_id: Policy ID
            
        Returns:
            Policy or None if not found
        """
        return self.policies.get(policy_id)
    
    def list_policies(self) -> List[ResidencyPolicy]:
        """List all policies.
        
        Returns:
            List of policies
        """
        return list(self.policies.values())
    
    def list_policies_by_mode(self, mode: ResidencyMode) -> List[ResidencyPolicy]:
        """List policies by residency mode.
        
        Args:
            mode: Residency mode
            
        Returns:
            List of policies with the specified mode
        """
        return [p for p in self.policies.values() if p.residency_mode == mode]
    
    async def update_policy(
        self,
        policy_id: str,
        **updates
    ) -> Optional[ResidencyPolicy]:
        """Update a policy.
        
        Args:
            policy_id: Policy ID
            **updates: Fields to update
            
        Returns:
            Updated policy or None if not found
        """
        logger.info(f"Updating policy {policy_id}")
        
        policy = self.policies.get(policy_id)
        if not policy:
            logger.warning(f"Policy {policy_id} not found")
            return None
        
        # Update allowed fields
        if "name" in updates:
            policy.name = updates["name"]
        if "description" in updates:
            policy.description = updates["description"]
        if "enabled" in updates:
            policy.enabled = updates["enabled"]
        if "allowed_regions" in updates:
            policy.allowed_regions = updates["allowed_regions"]
        if "allowed_countries" in updates:
            policy.allowed_countries = updates["allowed_countries"]
        
        policy.updated_at = datetime.utcnow()
        self.policies[policy_id] = policy
        
        logger.info(f"Policy {policy_id} updated successfully")
        return policy
    
    async def delete_policy(self, policy_id: str) -> bool:
        """Delete a policy.
        
        Args:
            policy_id: Policy ID
            
        Returns:
            True if deleted, False if not found
        """
        logger.info(f"Deleting policy {policy_id}")
        
        if policy_id not in self.policies:
            logger.warning(f"Policy {policy_id} not found")
            return False
        
        del self.policies[policy_id]
        logger.info(f"Policy {policy_id} deleted successfully")
        return True
    
    async def validate_region_compliance(
        self,
        policy_id: str,
        target_region: str
    ) -> Dict:
        """Validate if a region complies with a policy.
        
        Args:
            policy_id: Policy ID
            target_region: Target region to validate
            
        Returns:
            Validation result
        """
        logger.info(f"Validating region {target_region} against policy {policy_id}")
        
        policy = self.policies.get(policy_id)
        if not policy:
            return {"compliant": False, "reason": "Policy not found"}
        
        if not policy.enabled:
            return {"compliant": False, "reason": "Policy is disabled"}
        
        # Validate based on mode
        if policy.residency_mode == ResidencyMode.SINGLE_COUNTRY:
            compliant = target_region in policy.allowed_regions
        elif policy.residency_mode == ResidencyMode.REGIONAL:
            compliant = target_region in policy.allowed_regions
        elif policy.residency_mode == ResidencyMode.HYBRID:
            compliant = target_region in [policy.primary_region] + policy.secondary_regions
        elif policy.residency_mode == ResidencyMode.FULLY_SOVEREIGN:
            compliant = target_region in policy.allowed_regions
        elif policy.residency_mode == ResidencyMode.CLIENT_OWNED_SOVEREIGNTY:
            compliant = target_region in policy.client_specified_regions
        else:
            compliant = False
        
        return {
            "compliant": compliant,
            "policy_id": policy_id,
            "target_region": target_region,
            "residency_mode": policy.residency_mode
        }
