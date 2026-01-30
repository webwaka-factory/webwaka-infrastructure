"""Version management for deployments."""

import logging
from typing import Optional, Dict, List
from datetime import datetime

from ..models.version import Version, VersionConstraint


logger = logging.getLogger(__name__)


class VersionManager:
    """Manages available versions and compatibility."""
    
    def __init__(self):
        """Initialize the version manager."""
        self.versions: Dict[str, Version] = {}
        self.version_index: Dict[str, List[Version]] = {}
    
    async def register_version(self, version: Version) -> None:
        """Register a new version.
        
        Args:
            version: Version to register
        """
        logger.info(f"Registering version {version.id}: {version.component_name} {version.version_string}")
        
        self.versions[version.id] = version
        
        # Index by component
        component_key = f"{version.component_type}:{version.component_name}"
        if component_key not in self.version_index:
            self.version_index[component_key] = []
        
        self.version_index[component_key].append(version)
        
        # Sort by version (newest first)
        self.version_index[component_key].sort(
            key=lambda v: self._parse_version(v.version_string),
            reverse=True
        )
        
        logger.info(f"Version {version.id} registered successfully")
    
    async def get_available_versions(
        self,
        component_type: str,
        component_name: str
    ) -> List[Version]:
        """Get available versions for a component.
        
        Args:
            component_type: Component type
            component_name: Component name
            
        Returns:
            List of available versions
        """
        component_key = f"{component_type}:{component_name}"
        return self.version_index.get(component_key, [])
    
    async def get_latest_version(
        self,
        component_type: str,
        component_name: str,
        stable_only: bool = True
    ) -> Optional[Version]:
        """Get latest version for a component.
        
        Args:
            component_type: Component type
            component_name: Component name
            stable_only: Only return stable versions
            
        Returns:
            Latest version or None
        """
        versions = await self.get_available_versions(component_type, component_name)
        
        if stable_only:
            versions = [v for v in versions if v.is_stable]
        
        return versions[0] if versions else None
    
    async def check_compatibility(
        self,
        platform_version: str,
        suite_versions: Dict[str, str],
        capability_versions: Dict[str, str]
    ) -> tuple[bool, List[str], List[str]]:
        """Check version compatibility.
        
        Args:
            platform_version: Platform version
            suite_versions: Suite versions
            capability_versions: Capability versions
            
        Returns:
            Tuple of (is_compatible, incompatibilities, warnings)
        """
        logger.info(f"Checking compatibility for platform {platform_version}")
        
        incompatibilities = []
        warnings = []
        
        # Get platform version
        platform_versions = await self.get_available_versions("platform", "webwaka-platform")
        platform_ver = next((v for v in platform_versions if v.version_string == platform_version), None)
        
        if not platform_ver:
            incompatibilities.append(f"Platform version {platform_version} not found")
            return False, incompatibilities, warnings
        
        # Check suite compatibility
        for suite_name, suite_version in suite_versions.items():
            suite_versions_list = await self.get_available_versions("suite", suite_name)
            suite_ver = next((v for v in suite_versions_list if v.version_string == suite_version), None)
            
            if not suite_ver:
                incompatibilities.append(f"Suite {suite_name} version {suite_version} not found")
            elif suite_name in platform_ver.dependencies:
                required_version = platform_ver.dependencies[suite_name]
                if suite_version != required_version:
                    warnings.append(f"Suite {suite_name} {suite_version} may not be compatible with platform {platform_version}")
        
        # Check capability compatibility
        for cap_name, cap_version in capability_versions.items():
            cap_versions_list = await self.get_available_versions("capability", cap_name)
            cap_ver = next((v for v in cap_versions_list if v.version_string == cap_version), None)
            
            if not cap_ver:
                incompatibilities.append(f"Capability {cap_name} version {cap_version} not found")
        
        is_compatible = len(incompatibilities) == 0
        
        return is_compatible, incompatibilities, warnings
    
    def _parse_version(self, version_string: str) -> tuple:
        """Parse semantic version string.
        
        Args:
            version_string: Version string (e.g., "1.2.3")
            
        Returns:
            Tuple of version components for comparison
        """
        try:
            parts = version_string.split(".")
            return tuple(int(p) for p in parts[:3])
        except (ValueError, IndexError):
            return (0, 0, 0)
    
    def get_version(self, version_id: str) -> Optional[Version]:
        """Get version by ID.
        
        Args:
            version_id: Version ID
            
        Returns:
            Version or None if not found
        """
        return self.versions.get(version_id)
    
    def list_versions(self) -> List[Version]:
        """List all registered versions.
        
        Returns:
            List of versions
        """
        return list(self.versions.values())
