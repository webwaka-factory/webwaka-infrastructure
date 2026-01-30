"""Security patch API routes."""

import logging
from fastapi import APIRouter, HTTPException, status

from ...models.security import (
    SecurityPatch,
    PatchApplicationRequest,
    PatchApplicationResponse,
    PatchStatusResponse
)
from ...security.patch_manager import PatchManager


logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory storage for demo purposes
patch_manager = PatchManager()


@router.get("/security/patches", response_model=list[SecurityPatch])
async def list_patches(component_type: str = None, component_name: str = None):
    """List available security patches.
    
    Args:
        component_type: Optional component type filter
        component_name: Optional component name filter
        
    Returns:
        List of security patches
    """
    if component_type and component_name:
        return await patch_manager.get_available_patches(component_type, component_name)
    
    return patch_manager.list_patches()


@router.get("/security/patches/critical", response_model=list[SecurityPatch])
async def get_critical_patches():
    """Get all critical security patches.
    
    Returns:
        List of critical patches
    """
    return await patch_manager.get_critical_patches()


@router.post("/security/patches/apply", response_model=PatchApplicationResponse, status_code=status.HTTP_201_CREATED)
async def apply_patch(instance_id: str, request: PatchApplicationRequest):
    """Apply a security patch to an instance.
    
    Args:
        instance_id: Instance ID
        request: Patch application request
        
    Returns:
        Patch application response
    """
    try:
        application = await patch_manager.apply_patch(instance_id, request.patch_id)
        
        return PatchApplicationResponse(
            id=application.id,
            instance_id=application.instance_id,
            patch_id=application.patch_id,
            status=application.status,
            applied_at=application.applied_at,
            error_message=application.error_message
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error applying patch: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/security/patches/status/{instance_id}", response_model=PatchStatusResponse)
async def get_patch_status(instance_id: str):
    """Get patch status for an instance.
    
    Args:
        instance_id: Instance ID
        
    Returns:
        Patch status response
    """
    try:
        status_info = await patch_manager.get_instance_patch_status(instance_id)
        
        return PatchStatusResponse(
            instance_id=instance_id,
            total_patches=status_info["total_patches"],
            applied_patches=status_info["applied_patches"],
            pending_patches=status_info["pending_patches"],
            failed_patches=status_info["failed_patches"],
            critical_patches=0
        )
    except Exception as e:
        logger.error(f"Error getting patch status: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
