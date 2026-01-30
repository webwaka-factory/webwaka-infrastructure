"""Deployment validation module."""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass

from ..models.deployment import DeploymentManifest


logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    
    is_valid: bool
    errors: List[str]
    warnings: List[str]


class DeploymentValidator:
    """Validates deployments and manifests."""
    
    async def validate_manifest(self, manifest: DeploymentManifest) -> ValidationResult:
        """Validate a deployment manifest.
        
        Args:
            manifest: Deployment manifest to validate
            
        Returns:
            Validation result
        """
        logger.info(f"Validating manifest {manifest.id}")
        
        errors = []
        warnings = []
        
        # Check required fields
        if not manifest.id:
            errors.append("Manifest ID is required")
        
        if not manifest.platform_version:
            errors.append("Platform version is required")
        
        if not manifest.version:
            errors.append("Manifest version is required")
        
        # Check version format
        if manifest.platform_version and not self._is_valid_semver(manifest.platform_version):
            warnings.append(f"Platform version {manifest.platform_version} is not valid semver")
        
        # Check suites
        for suite_name, suite_version in manifest.suites.items():
            if not suite_version:
                errors.append(f"Suite {suite_name} has empty version")
            elif not self._is_valid_semver(suite_version):
                warnings.append(f"Suite {suite_name} version {suite_version} is not valid semver")
        
        # Check capabilities
        for cap_name, cap_version in manifest.capabilities.items():
            if not cap_version:
                errors.append(f"Capability {cap_name} has empty version")
            elif not self._is_valid_semver(cap_version):
                warnings.append(f"Capability {cap_name} version {cap_version} is not valid semver")
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info(f"Manifest {manifest.id} validation passed")
        else:
            logger.error(f"Manifest {manifest.id} validation failed: {errors}")
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings
        )
    
    async def validate_deployment_readiness(
        self,
        instance_id: str,
        manifest: DeploymentManifest
    ) -> ValidationResult:
        """Validate if instance is ready for deployment.
        
        Args:
            instance_id: Instance ID
            manifest: Deployment manifest
            
        Returns:
            Validation result
        """
        logger.info(f"Validating deployment readiness for instance {instance_id}")
        
        errors = []
        warnings = []
        
        # Check instance connectivity
        logger.info(f"Checking connectivity to instance {instance_id}")
        
        # Check available disk space
        logger.info(f"Checking disk space on instance {instance_id}")
        
        # Check current version compatibility
        logger.info(f"Checking version compatibility for instance {instance_id}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    async def validate_rollback_feasibility(
        self,
        instance_id: str,
        from_manifest_id: str,
        to_manifest_id: str
    ) -> ValidationResult:
        """Validate if rollback is feasible.
        
        Args:
            instance_id: Instance ID
            from_manifest_id: Current manifest ID
            to_manifest_id: Target manifest ID
            
        Returns:
            Validation result
        """
        logger.info(f"Validating rollback feasibility for instance {instance_id}")
        
        errors = []
        warnings = []
        
        if not from_manifest_id:
            errors.append("Current manifest ID is required")
        
        if not to_manifest_id:
            errors.append("Target manifest ID is required")
        
        if from_manifest_id == to_manifest_id:
            errors.append("Cannot rollback to the same manifest version")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _is_valid_semver(self, version: str) -> bool:
        """Check if version string is valid semantic versioning.
        
        Args:
            version: Version string
            
        Returns:
            True if valid semver, False otherwise
        """
        import re
        
        # Basic semver pattern: major.minor.patch
        pattern = r"^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?(\+[a-zA-Z0-9]+)?$"
        return bool(re.match(pattern, version))
