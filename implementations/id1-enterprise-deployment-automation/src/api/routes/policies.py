"""Policy API routes."""

import logging
from fastapi import APIRouter, HTTPException, status

from ...models.policy import (
    UpdateChannelPolicy,
    PolicyType,
    PolicyUpdateRequest,
    PolicyResponse
)
from ...policies.policy_manager import PolicyManager


logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory storage for demo purposes
policy_manager = PolicyManager()


@router.post("/policies", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_policy(instance_id: str, policy_type: PolicyType, description: str = None):
    """Create a new update channel policy.
    
    Args:
        instance_id: Instance ID
        policy_type: Type of policy
        description: Policy description
        
    Returns:
        Created policy response
    """
    try:
        policy = await policy_manager.create_policy(
            instance_id=instance_id,
            policy_type=policy_type,
            description=description
        )
        
        return PolicyResponse(
            id=policy.id,
            instance_id=policy.instance_id,
            policy_type=policy.policy_type,
            enabled=policy.enabled,
            description=policy.description,
            created_at=policy.created_at,
            updated_at=policy.updated_at
        )
    except Exception as e:
        logger.error(f"Error creating policy: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/policies/{policy_id}", response_model=PolicyResponse)
async def get_policy(policy_id: str):
    """Get policy by ID.
    
    Args:
        policy_id: Policy ID
        
    Returns:
        Policy response
    """
    policy = policy_manager.get_policy(policy_id)
    
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
    
    return PolicyResponse(
        id=policy.id,
        instance_id=policy.instance_id,
        policy_type=policy.policy_type,
        enabled=policy.enabled,
        description=policy.description,
        created_at=policy.created_at,
        updated_at=policy.updated_at
    )


@router.get("/policies", response_model=list[PolicyResponse])
async def list_policies(instance_id: str = None):
    """List policies.
    
    Args:
        instance_id: Optional instance ID to filter by
        
    Returns:
        List of policy responses
    """
    policies = policy_manager.list_policies(instance_id)
    
    return [
        PolicyResponse(
            id=p.id,
            instance_id=p.instance_id,
            policy_type=p.policy_type,
            enabled=p.enabled,
            description=p.description,
            created_at=p.created_at,
            updated_at=p.updated_at
        )
        for p in policies
    ]


@router.put("/policies/{policy_id}", response_model=PolicyResponse)
async def update_policy(policy_id: str, request: PolicyUpdateRequest):
    """Update a policy.
    
    Args:
        policy_id: Policy ID
        request: Update request
        
    Returns:
        Updated policy response
    """
    updates = request.dict(exclude_unset=True)
    policy = await policy_manager.update_policy(policy_id, **updates)
    
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
    
    return PolicyResponse(
        id=policy.id,
        instance_id=policy.instance_id,
        policy_type=policy.policy_type,
        enabled=policy.enabled,
        description=policy.description,
        created_at=policy.created_at,
        updated_at=policy.updated_at
    )


@router.delete("/policies/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_policy(policy_id: str):
    """Delete a policy.
    
    Args:
        policy_id: Policy ID
    """
    deleted = await policy_manager.delete_policy(policy_id)
    
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
