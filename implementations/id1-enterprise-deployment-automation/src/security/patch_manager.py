"""Security patch management."""

import logging
from typing import Optional, Dict, List
from datetime import datetime

from ..models.security import SecurityPatch, PatchApplication, PatchStatus, SeverityLevel


logger = logging.getLogger(__name__)


class PatchManager:
    """Manages security patches."""
    
    def __init__(self):
        """Initialize the patch manager."""
        self.patches: Dict[str, SecurityPatch] = {}
        self.applications: Dict[str, PatchApplication] = {}
        self.patch_index: Dict[str, List[SecurityPatch]] = {}
    
    async def register_patch(self, patch: SecurityPatch) -> None:
        """Register a new security patch.
        
        Args:
            patch: Security patch to register
        """
        logger.info(f"Registering patch {patch.id}: {patch.component_name} {patch.patched_version}")
        
        self.patches[patch.id] = patch
        
        # Index by component
        component_key = f"{patch.component_type}:{patch.component_name}"
        if component_key not in self.patch_index:
            self.patch_index[component_key] = []
        
        self.patch_index[component_key].append(patch)
        
        logger.info(f"Patch {patch.id} registered successfully")
    
    async def get_available_patches(
        self,
        component_type: str,
        component_name: str,
        current_version: Optional[str] = None
    ) -> List[SecurityPatch]:
        """Get available patches for a component.
        
        Args:
            component_type: Component type
            component_name: Component name
            current_version: Optional current version to filter patches
            
        Returns:
            List of available patches
        """
        component_key = f"{component_type}:{component_name}"
        patches = self.patch_index.get(component_key, [])
        
        if current_version:
            patches = [p for p in patches if current_version in p.affected_versions]
        
        return patches
    
    async def get_critical_patches(self) -> List[SecurityPatch]:
        """Get all critical security patches.
        
        Returns:
            List of critical patches
        """
        return [p for p in self.patches.values() if p.severity == SeverityLevel.CRITICAL]
    
    async def apply_patch(
        self,
        instance_id: str,
        patch_id: str
    ) -> PatchApplication:
        """Apply a security patch to an instance.
        
        Args:
            instance_id: Instance ID
            patch_id: Patch ID
            
        Returns:
            Patch application record
        """
        logger.info(f"Applying patch {patch_id} to instance {instance_id}")
        
        patch = self.patches.get(patch_id)
        if not patch:
            logger.error(f"Patch {patch_id} not found")
            raise ValueError(f"Patch {patch_id} not found")
        
        app_id = f"app-{datetime.utcnow().timestamp()}"
        
        application = PatchApplication(
            id=app_id,
            instance_id=instance_id,
            patch_id=patch_id,
            status=PatchStatus.APPLIED,
            applied_at=datetime.utcnow(),
            applied_by="system"
        )
        
        self.applications[app_id] = application
        
        logger.info(f"Patch {patch_id} applied to instance {instance_id}")
        return application
    
    async def get_instance_patch_status(self, instance_id: str) -> Dict[str, any]:
        """Get patch status for an instance.
        
        Args:
            instance_id: Instance ID
            
        Returns:
            Patch status information
        """
        applications = [a for a in self.applications.values() if a.instance_id == instance_id]
        
        total = len(applications)
        applied = len([a for a in applications if a.status == PatchStatus.APPLIED])
        failed = len([a for a in applications if a.status == PatchStatus.FAILED])
        pending = len([a for a in applications if a.status == PatchStatus.AVAILABLE])
        
        return {
            "instance_id": instance_id,
            "total_patches": total,
            "applied_patches": applied,
            "failed_patches": failed,
            "pending_patches": pending,
            "applications": applications
        }
    
    def get_patch(self, patch_id: str) -> Optional[SecurityPatch]:
        """Get patch by ID.
        
        Args:
            patch_id: Patch ID
            
        Returns:
            Patch or None if not found
        """
        return self.patches.get(patch_id)
    
    def list_patches(self) -> List[SecurityPatch]:
        """List all patches.
        
        Returns:
            List of patches
        """
        return list(self.patches.values())
