"""Policy enforcement logic."""

import logging
from typing import Optional, Tuple
from datetime import datetime

from ..models.policy import UpdateChannelPolicy, PolicyType
from ..models.deployment import DeploymentManifest


logger = logging.getLogger(__name__)


class PolicyEnforcer:
    """Enforces update channel policies."""
    
    async def can_deploy(
        self,
        policy: UpdateChannelPolicy,
        manifest: DeploymentManifest,
        is_security_patch: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """Check if deployment is allowed by policy.
        
        Args:
            policy: Update channel policy
            manifest: Deployment manifest
            is_security_patch: Whether this is a security patch deployment
            
        Returns:
            Tuple of (allowed, reason)
        """
        logger.info(f"Checking deployment against policy {policy.id}")
        
        if not policy.enabled:
            return False, "Policy is disabled"
        
        if policy.policy_type == PolicyType.AUTO_UPDATE:
            return await self._check_auto_update(policy, manifest)
        
        elif policy.policy_type == PolicyType.MANUAL_APPROVAL:
            return await self._check_manual_approval(policy, manifest)
        
        elif policy.policy_type == PolicyType.FROZEN:
            return await self._check_frozen(policy, manifest, is_security_patch)
        
        return False, "Unknown policy type"
    
    async def _check_auto_update(
        self,
        policy: UpdateChannelPolicy,
        manifest: DeploymentManifest
    ) -> Tuple[bool, Optional[str]]:
        """Check auto-update policy.
        
        Args:
            policy: Auto-update policy
            manifest: Deployment manifest
            
        Returns:
            Tuple of (allowed, reason)
        """
        logger.info(f"Checking auto-update policy {policy.id}")
        
        # Check maintenance window if configured
        if policy.auto_update_maintenance_window:
            is_in_window = await self._is_in_maintenance_window(
                policy.auto_update_maintenance_window
            )
            if not is_in_window:
                return False, "Not in maintenance window"
        
        return True, None
    
    async def _check_manual_approval(
        self,
        policy: UpdateChannelPolicy,
        manifest: DeploymentManifest
    ) -> Tuple[bool, Optional[str]]:
        """Check manual approval policy.
        
        Args:
            policy: Manual approval policy
            manifest: Deployment manifest
            
        Returns:
            Tuple of (allowed, reason)
        """
        logger.info(f"Checking manual approval policy {policy.id}")
        
        # Manual approval requires explicit approval (checked elsewhere)
        return False, "Manual approval required"
    
    async def _check_frozen(
        self,
        policy: UpdateChannelPolicy,
        manifest: DeploymentManifest,
        is_security_patch: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """Check frozen policy.
        
        Args:
            policy: Frozen policy
            manifest: Deployment manifest
            is_security_patch: Whether this is a security patch
            
        Returns:
            Tuple of (allowed, reason)
        """
        logger.info(f"Checking frozen policy {policy.id}")
        
        # Security patches are allowed if configured
        if is_security_patch and policy.allow_security_patches:
            return True, None
        
        # Check if versions match frozen versions
        if manifest.platform_version != policy.frozen_versions.get("platform"):
            return False, "Platform version does not match frozen version"
        
        for suite_name, suite_version in manifest.suites.items():
            frozen_version = policy.frozen_versions.get(f"suite:{suite_name}")
            if frozen_version and suite_version != frozen_version:
                return False, f"Suite {suite_name} version does not match frozen version"
        
        return True, None
    
    async def _is_in_maintenance_window(self, window_config: dict) -> bool:
        """Check if current time is in maintenance window.
        
        Args:
            window_config: Maintenance window configuration
            
        Returns:
            True if in window, False otherwise
        """
        # Implementation would check against configured maintenance windows
        # For now, return True to allow deployment
        return True
    
    async def enforce_security_patch(
        self,
        policy: UpdateChannelPolicy,
        patch_version: str
    ) -> Tuple[bool, Optional[str]]:
        """Enforce security patch regardless of policy.
        
        Args:
            policy: Update channel policy
            patch_version: Security patch version
            
        Returns:
            Tuple of (allowed, reason)
        """
        logger.info(f"Enforcing security patch against policy {policy.id}")
        
        if policy.policy_type == PolicyType.FROZEN:
            if not policy.allow_security_patches:
                return False, "Security patches not allowed in frozen policy"
        
        return True, None
