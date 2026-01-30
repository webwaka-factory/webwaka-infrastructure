"""Security patch enforcement."""

import logging
from typing import Optional, Tuple
from datetime import datetime

from ..models.security import SecurityPatch, SeverityLevel
from ..models.policy import UpdateChannelPolicy, PolicyType


logger = logging.getLogger(__name__)


class PatchEnforcer:
    """Enforces security patch policies."""
    
    async def should_enforce_patch(
        self,
        patch: SecurityPatch,
        policy: Optional[UpdateChannelPolicy] = None
    ) -> Tuple[bool, Optional[str]]:
        """Determine if a security patch should be enforced.
        
        Args:
            patch: Security patch
            policy: Optional update channel policy
            
        Returns:
            Tuple of (should_enforce, reason)
        """
        logger.info(f"Evaluating patch enforcement for {patch.id}")
        
        # Critical patches are always enforced
        if patch.severity == SeverityLevel.CRITICAL:
            logger.info(f"Patch {patch.id} is critical and will be enforced")
            return True, None
        
        # Check policy
        if policy:
            if policy.policy_type == PolicyType.FROZEN:
                if not policy.allow_security_patches:
                    return False, "Security patches not allowed in frozen policy"
            
            elif policy.policy_type == PolicyType.MANUAL_APPROVAL:
                return False, "Manual approval required for non-critical patches"
        
        return True, None
    
    async def validate_patch_prerequisites(
        self,
        patch: SecurityPatch,
        current_version: str
    ) -> Tuple[bool, Optional[str]]:
        """Validate patch prerequisites.
        
        Args:
            patch: Security patch
            current_version: Current component version
            
        Returns:
            Tuple of (valid, reason)
        """
        logger.info(f"Validating prerequisites for patch {patch.id}")
        
        # Check if current version is affected
        if current_version not in patch.affected_versions:
            return False, f"Current version {current_version} is not affected by this patch"
        
        # Check dependencies
        if patch.affected_versions:
            logger.info(f"Patch {patch.id} affects versions: {patch.affected_versions}")
        
        return True, None
    
    async def schedule_patch_application(
        self,
        patch: SecurityPatch,
        policy: Optional[UpdateChannelPolicy] = None
    ) -> Optional[datetime]:
        """Schedule patch application based on policy.
        
        Args:
            patch: Security patch
            policy: Optional update channel policy
            
        Returns:
            Scheduled application time or None for immediate
        """
        logger.info(f"Scheduling patch {patch.id} for application")
        
        # Critical patches are applied immediately
        if patch.severity == SeverityLevel.CRITICAL:
            return None
        
        # Check maintenance window if policy exists
        if policy and policy.auto_update_maintenance_window:
            # Return scheduled time based on maintenance window
            # For now, return None for immediate application
            return None
        
        return None
    
    async def validate_patch_compatibility(
        self,
        patch: SecurityPatch,
        suite_versions: dict,
        capability_versions: dict
    ) -> Tuple[bool, Optional[str]]:
        """Validate patch compatibility with other components.
        
        Args:
            patch: Security patch
            suite_versions: Suite versions
            capability_versions: Capability versions
            
        Returns:
            Tuple of (compatible, reason)
        """
        logger.info(f"Validating compatibility for patch {patch.id}")
        
        # Check dependencies
        for dep_name, dep_version in patch.metadata.get("dependencies", {}).items():
            if dep_name in suite_versions:
                if suite_versions[dep_name] != dep_version:
                    return False, f"Dependency {dep_name} version mismatch"
        
        return True, None
