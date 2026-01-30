"""Core multi-region deployment engine."""

import logging
from typing import Optional, Dict, List
from datetime import datetime

from ..models.region import Region, RegionStatus, RegionConfig


logger = logging.getLogger(__name__)


class MultiRegionEngine:
    """Core engine for managing multi-region deployments."""
    
    def __init__(self):
        """Initialize the multi-region engine."""
        self.regions: Dict[str, Region] = {}
        self.region_index: Dict[str, str] = {}  # aws_region -> region_id
        self.health_status: Dict[str, Dict] = {}
    
    async def register_region(
        self,
        name: str,
        aws_region: str,
        country_code: str,
        data_center_location: str,
        availability_zones: List[str],
        replication_targets: Optional[List[str]] = None
    ) -> Region:
        """Register a new region.
        
        Args:
            name: Region name
            aws_region: AWS region code
            country_code: Country code
            data_center_location: Data center location
            availability_zones: List of availability zones
            replication_targets: Optional replication targets
            
        Returns:
            Registered region
        """
        logger.info(f"Registering region {aws_region}")
        
        region_id = f"region-{aws_region}"
        
        config = RegionConfig(
            aws_region=aws_region,
            country_code=country_code,
            data_center_location=data_center_location,
            availability_zones=availability_zones,
            replication_targets=replication_targets or []
        )
        
        region = Region(
            id=region_id,
            name=name,
            aws_region=aws_region,
            country_code=country_code,
            status=RegionStatus.PROVISIONING,
            config=config
        )
        
        self.regions[region_id] = region
        self.region_index[aws_region] = region_id
        
        logger.info(f"Region {region_id} registered successfully")
        return region
    
    async def activate_region(self, region_id: str) -> Optional[Region]:
        """Activate a region.
        
        Args:
            region_id: Region ID
            
        Returns:
            Updated region or None if not found
        """
        logger.info(f"Activating region {region_id}")
        
        region = self.regions.get(region_id)
        if not region:
            logger.warning(f"Region {region_id} not found")
            return None
        
        region.status = RegionStatus.ACTIVE
        region.updated_at = datetime.utcnow()
        self.regions[region_id] = region
        
        logger.info(f"Region {region_id} activated successfully")
        return region
    
    async def deactivate_region(self, region_id: str) -> Optional[Region]:
        """Deactivate a region.
        
        Args:
            region_id: Region ID
            
        Returns:
            Updated region or None if not found
        """
        logger.info(f"Deactivating region {region_id}")
        
        region = self.regions.get(region_id)
        if not region:
            logger.warning(f"Region {region_id} not found")
            return None
        
        region.status = RegionStatus.INACTIVE
        region.updated_at = datetime.utcnow()
        self.regions[region_id] = region
        
        logger.info(f"Region {region_id} deactivated successfully")
        return region
    
    async def get_region_health(self, region_id: str) -> Dict:
        """Get region health status.
        
        Args:
            region_id: Region ID
            
        Returns:
            Health status information
        """
        logger.info(f"Checking health for region {region_id}")
        
        region = self.regions.get(region_id)
        if not region:
            return {"status": "unknown", "error": "Region not found"}
        
        return {
            "region_id": region_id,
            "status": region.status,
            "health": "healthy" if region.status == RegionStatus.ACTIVE else "degraded",
            "last_check": datetime.utcnow().isoformat()
        }
    
    def get_region(self, region_id: str) -> Optional[Region]:
        """Get region by ID.
        
        Args:
            region_id: Region ID
            
        Returns:
            Region or None if not found
        """
        return self.regions.get(region_id)
    
    def get_region_by_aws_region(self, aws_region: str) -> Optional[Region]:
        """Get region by AWS region code.
        
        Args:
            aws_region: AWS region code
            
        Returns:
            Region or None if not found
        """
        region_id = self.region_index.get(aws_region)
        if region_id:
            return self.regions.get(region_id)
        return None
    
    def list_regions(self) -> List[Region]:
        """List all regions.
        
        Returns:
            List of regions
        """
        return list(self.regions.values())
    
    def list_active_regions(self) -> List[Region]:
        """List active regions.
        
        Returns:
            List of active regions
        """
        return [r for r in self.regions.values() if r.status == RegionStatus.ACTIVE]
    
    async def delete_region(self, region_id: str) -> bool:
        """Delete a region.
        
        Args:
            region_id: Region ID
            
        Returns:
            True if deleted, False if not found
        """
        logger.info(f"Deleting region {region_id}")
        
        region = self.regions.get(region_id)
        if not region:
            logger.warning(f"Region {region_id} not found")
            return False
        
        # Remove from indices
        del self.regions[region_id]
        if region.aws_region in self.region_index:
            del self.region_index[region.aws_region]
        
        logger.info(f"Region {region_id} deleted successfully")
        return True
