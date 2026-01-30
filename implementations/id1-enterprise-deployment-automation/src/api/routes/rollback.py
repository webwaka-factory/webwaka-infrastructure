"""Rollback API routes."""

import logging
from fastapi import APIRouter, HTTPException, status

from ...models.rollback import (
    RollbackRecord,
    RollbackRequest,
    RollbackResponse,
    RollbackHistory
)
from ...rollback.rollback_manager import RollbackManager


logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory storage for demo purposes
rollback_manager = RollbackManager()


@router.post("/rollback", response_model=RollbackResponse, status_code=status.HTTP_201_CREATED)
async def initiate_rollback(instance_id: str, request: RollbackRequest):
    """Initiate a rollback operation.
    
    Args:
        instance_id: Instance ID
        request: Rollback request
        
    Returns:
        Rollback response
    """
    try:
        rollback = await rollback_manager.initiate_rollback(
            instance_id=instance_id,
            from_manifest_id="current-manifest",
            to_manifest_id=request.to_manifest_id,
            reason=request.reason
        )
        
        return RollbackResponse(
            id=rollback.id,
            instance_id=rollback.instance_id,
            from_manifest_id=rollback.from_manifest_id,
            to_manifest_id=rollback.to_manifest_id,
            status=rollback.status,
            initiated_at=rollback.initiated_at,
            started_at=rollback.started_at,
            completed_at=rollback.completed_at,
            error_message=rollback.error_message
        )
    except Exception as e:
        logger.error(f"Error initiating rollback: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/rollback/{rollback_id}", response_model=RollbackResponse)
async def get_rollback(rollback_id: str):
    """Get rollback by ID.
    
    Args:
        rollback_id: Rollback ID
        
    Returns:
        Rollback response
    """
    rollback = rollback_manager.get_rollback(rollback_id)
    
    if not rollback:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rollback not found")
    
    return RollbackResponse(
        id=rollback.id,
        instance_id=rollback.instance_id,
        from_manifest_id=rollback.from_manifest_id,
        to_manifest_id=rollback.to_manifest_id,
        status=rollback.status,
        initiated_at=rollback.initiated_at,
        started_at=rollback.started_at,
        completed_at=rollback.completed_at,
        error_message=rollback.error_message
    )


@router.get("/rollback/history/{instance_id}", response_model=RollbackHistory)
async def get_rollback_history(instance_id: str):
    """Get rollback history for an instance.
    
    Args:
        instance_id: Instance ID
        
    Returns:
        Rollback history
    """
    try:
        history = await rollback_manager.get_rollback_history(instance_id)
        return history
    except Exception as e:
        logger.error(f"Error getting rollback history: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/rollback", response_model=list[RollbackResponse])
async def list_rollbacks(instance_id: str = None):
    """List rollback operations.
    
    Args:
        instance_id: Optional instance ID to filter by
        
    Returns:
        List of rollback responses
    """
    rollbacks = rollback_manager.list_rollbacks(instance_id)
    
    return [
        RollbackResponse(
            id=r.id,
            instance_id=r.instance_id,
            from_manifest_id=r.from_manifest_id,
            to_manifest_id=r.to_manifest_id,
            status=r.status,
            initiated_at=r.initiated_at,
            started_at=r.started_at,
            completed_at=r.completed_at,
            error_message=r.error_message
        )
        for r in rollbacks
    ]
