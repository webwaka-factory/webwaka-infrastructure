"""Policy management for update channels."""

import logging
from typing import Optional, Dict, List
from datetime import datetime

from ..models.policy import UpdateChannelPolicy, PolicyType


logger = logging.getLogger(__name__)


class PolicyManager:
    """Manages update channel policies for instances."""
    
    def __init__(self):
        """Initialize the policy manager."""
        self.policies: Dict[str, UpdateChannelPolicy] = {}
    
    async def create_policy(
        self,
        instance_id: str,
        policy_type: PolicyType,
        description: Optional[str] = None,
        **kwargs
    ) -> UpdateChannelPolicy:
        """Create a new update channel policy.
        
        Args:
            instance_id: Instance ID
            policy_type: Type of policy
            description: Policy description
            **kwargs: Additional policy-specific parameters
            
        Returns:
            Created policy
        """
        logger.info(f"Creating {policy_type} policy for instance {instance_id}")
        
        policy_id = f"policy-{datetime.utcnow().timestamp()}"
        
        policy = UpdateChannelPolicy(
            id=policy_id,
            instance_id=instance_id,
            policy_type=policy_type,
            description=description,
            **kwargs
        )
        
        self.policies[policy_id] = policy
        logger.info(f"Policy {policy_id} created successfully")
        
        return policy
    
    async def update_policy(
        self,
        policy_id: str,
        **updates
    ) -> Optional[UpdateChannelPolicy]:
        """Update an existing policy.
        
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
        
        # Update fields
        for key, value in updates.items():
            if hasattr(policy, key):
                setattr(policy, key, value)
        
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
        
        if policy_id in self.policies:
            del self.policies[policy_id]
            logger.info(f"Policy {policy_id} deleted successfully")
            return True
        
        logger.warning(f"Policy {policy_id} not found")
        return False
    
    def get_policy(self, policy_id: str) -> Optional[UpdateChannelPolicy]:
        """Get policy by ID.
        
        Args:
            policy_id: Policy ID
            
        Returns:
            Policy or None if not found
        """
        return self.policies.get(policy_id)
    
    def get_instance_policy(self, instance_id: str) -> Optional[UpdateChannelPolicy]:
        """Get policy for an instance.
        
        Args:
            instance_id: Instance ID
            
        Returns:
            Policy or None if not found
        """
        for policy in self.policies.values():
            if policy.instance_id == instance_id and policy.enabled:
                return policy
        return None
    
    def list_policies(self, instance_id: Optional[str] = None) -> List[UpdateChannelPolicy]:
        """List policies.
        
        Args:
            instance_id: Optional instance ID to filter by
            
        Returns:
            List of policies
        """
        if instance_id:
            return [p for p in self.policies.values() if p.instance_id == instance_id]
        return list(self.policies.values())
