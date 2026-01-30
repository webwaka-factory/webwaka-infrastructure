"""Manifest compiler for generating deployment configurations."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..models.deployment import DeploymentManifest
from ..models.version import Version


logger = logging.getLogger(__name__)


class ManifestCompiler:
    """Compiles deployment manifests from version specifications."""
    
    def __init__(self):
        """Initialize the manifest compiler."""
        self.compiled_manifests: Dict[str, DeploymentManifest] = {}
    
    async def compile_manifest(
        self,
        platform_version: str,
        suites: Dict[str, str],
        capabilities: Dict[str, str],
        configuration: Optional[Dict[str, Any]] = None
    ) -> DeploymentManifest:
        """Compile a deployment manifest.
        
        Args:
            platform_version: Platform version
            suites: Suite versions mapping
            capabilities: Capability versions mapping
            configuration: Optional deployment configuration
            
        Returns:
            Compiled deployment manifest
        """
        logger.info(f"Compiling manifest for platform {platform_version}")
        
        manifest_id = f"manifest-{datetime.utcnow().timestamp()}"
        
        manifest = DeploymentManifest(
            id=manifest_id,
            version="1.0.0",
            platform_version=platform_version,
            suites=suites,
            capabilities=capabilities,
            configuration=configuration or {},
            metadata={
                "compiled_at": datetime.utcnow().isoformat(),
                "compiler_version": "1.0.0"
            }
        )
        
        self.compiled_manifests[manifest_id] = manifest
        logger.info(f"Manifest {manifest_id} compiled successfully")
        
        return manifest
    
    async def validate_manifest_syntax(self, manifest: DeploymentManifest) -> bool:
        """Validate manifest syntax.
        
        Args:
            manifest: Deployment manifest
            
        Returns:
            True if valid, False otherwise
        """
        logger.info(f"Validating manifest syntax for {manifest.id}")
        
        # Check required fields
        if not manifest.platform_version:
            logger.error("Platform version is required")
            return False
        
        if not manifest.suites and not manifest.capabilities:
            logger.warning("Manifest has no suites or capabilities")
        
        return True
    
    async def resolve_dependencies(
        self,
        manifest: DeploymentManifest,
        available_versions: Dict[str, list[Version]]
    ) -> Dict[str, str]:
        """Resolve version dependencies.
        
        Args:
            manifest: Deployment manifest
            available_versions: Available versions by component
            
        Returns:
            Resolved version mappings
        """
        logger.info(f"Resolving dependencies for manifest {manifest.id}")
        
        resolved_versions = {}
        
        # Resolve platform dependencies
        resolved_versions["platform"] = manifest.platform_version
        
        # Resolve suite dependencies
        for suite_name, suite_version in manifest.suites.items():
            resolved_versions[f"suite:{suite_name}"] = suite_version
        
        # Resolve capability dependencies
        for cap_name, cap_version in manifest.capabilities.items():
            resolved_versions[f"capability:{cap_name}"] = cap_version
        
        logger.info(f"Dependencies resolved for manifest {manifest.id}")
        return resolved_versions
    
    def get_manifest(self, manifest_id: str) -> Optional[DeploymentManifest]:
        """Get compiled manifest by ID.
        
        Args:
            manifest_id: Manifest ID
            
        Returns:
            Manifest or None if not found
        """
        return self.compiled_manifests.get(manifest_id)
    
    def list_manifests(self) -> list[DeploymentManifest]:
        """List all compiled manifests.
        
        Returns:
            List of manifests
        """
        return list(self.compiled_manifests.values())
