"""Version API routes."""

import logging
from fastapi import APIRouter, HTTPException, status

from ...models.version import (
    Version,
    VersionPin,
    VersionPinRequest,
    VersionCompatibilityCheck,
    VersionCompatibilityResult
)
from ...versioning.version_manager import VersionManager
from ...versioning.version_pinner import VersionPinner


logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory storage for demo purposes
version_manager = VersionManager()
version_pinner = VersionPinner()


@router.get("/versions", response_model=list[Version])
async def list_versions(component_type: str = None, component_name: str = None):
    """List available versions.
    
    Args:
        component_type: Optional component type filter
        component_name: Optional component name filter
        
    Returns:
        List of versions
    """
    if component_type and component_name:
        return await version_manager.get_available_versions(component_type, component_name)
    
    return version_manager.list_versions()


@router.post("/versions/pin", response_model=VersionPin, status_code=status.HTTP_201_CREATED)
async def pin_version(instance_id: str, request: VersionPinRequest):
    """Pin a version for an instance.
    
    Args:
        instance_id: Instance ID
        request: Version pin request
        
    Returns:
        Created version pin
    """
    try:
        pin = await version_pinner.pin_version(
            instance_id=instance_id,
            component_type=request.component_type,
            component_name=request.component_name,
            pinned_version=request.pinned_version,
            reason=request.reason,
            expires_at=request.expires_at
        )
        
        return pin
    except Exception as e:
        logger.error(f"Error pinning version: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/versions/pin/{pin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unpin_version(pin_id: str):
    """Remove a version pin.
    
    Args:
        pin_id: Pin ID
    """
    deleted = await version_pinner.unpin_version(pin_id)
    
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pin not found")


@router.get("/versions/pins/{instance_id}", response_model=list[VersionPin])
async def get_instance_pins(instance_id: str):
    """Get version pins for an instance.
    
    Args:
        instance_id: Instance ID
        
    Returns:
        List of version pins
    """
    return await version_pinner.get_instance_pins(instance_id)


@router.post("/versions/compatibility", response_model=VersionCompatibilityResult)
async def check_compatibility(request: VersionCompatibilityCheck):
    """Check version compatibility.
    
    Args:
        request: Compatibility check request
        
    Returns:
        Compatibility check result
    """
    try:
        is_compatible, incompatibilities, warnings = await version_manager.check_compatibility(
            platform_version=request.platform_version,
            suite_versions=request.suites,
            capability_versions=request.capabilities
        )
        
        return VersionCompatibilityResult(
            is_compatible=is_compatible,
            compatible_versions=["2.0.0"] if is_compatible else [],
            incompatibilities=incompatibilities,
            warnings=warnings
        )
    except Exception as e:
        logger.error(f"Error checking compatibility: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
