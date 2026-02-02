"""
Unit Tests for ID-3 Region Models

Tests for Region, RegionConfig, and related models.
"""

import pytest
from datetime import datetime

from src.models.region import Region, RegionStatus, RegionConfig


class TestRegion:
    """Tests for Region model"""

    def test_create_region(self, nigeria_region):
        """Test creating a region"""
        assert nigeria_region.id == "region-af-west-1"
        assert nigeria_region.name == "Africa West (Nigeria)"
        assert nigeria_region.aws_region == "af-west-1"
        assert nigeria_region.country_code == "NG"

    def test_region_status(self, nigeria_region):
        """Test region status"""
        assert nigeria_region.status == RegionStatus.ACTIVE

    def test_region_config(self, nigeria_region):
        """Test region configuration"""
        assert nigeria_region.config.aws_region == "af-west-1"
        assert nigeria_region.config.country_code == "NG"
        assert nigeria_region.config.data_center_location == "Lagos, Nigeria"

    def test_region_availability_zones(self, nigeria_region):
        """Test region availability zones"""
        assert len(nigeria_region.config.availability_zones) == 2
        assert "af-west-1a" in nigeria_region.config.availability_zones


class TestRegionStatus:
    """Tests for RegionStatus enum"""

    def test_region_status_values(self):
        """Test region status values"""
        assert RegionStatus.ACTIVE.value == "active"
        assert RegionStatus.INACTIVE.value == "inactive"
        assert RegionStatus.DEGRADED.value == "degraded"
        assert RegionStatus.MAINTENANCE.value == "maintenance"
        assert RegionStatus.PROVISIONING.value == "provisioning"
        assert RegionStatus.DECOMMISSIONING.value == "decommissioning"

    def test_region_status_transitions(self, nigeria_region):
        """Test region status transitions"""
        # Active -> Maintenance
        nigeria_region.status = RegionStatus.MAINTENANCE
        assert nigeria_region.status == RegionStatus.MAINTENANCE
        
        # Maintenance -> Active
        nigeria_region.status = RegionStatus.ACTIVE
        assert nigeria_region.status == RegionStatus.ACTIVE


class TestRegionConfig:
    """Tests for RegionConfig model"""

    def test_create_region_config(self):
        """Test creating region configuration"""
        config = RegionConfig(
            aws_region="af-west-1",
            country_code="NG",
            data_center_location="Lagos, Nigeria",
            availability_zones=["af-west-1a", "af-west-1b"]
        )
        
        assert config.aws_region == "af-west-1"
        assert config.country_code == "NG"

    def test_region_config_replication(self, eu_region):
        """Test region replication targets"""
        assert len(eu_region.config.replication_targets) == 1
        assert "eu-central-1" in eu_region.config.replication_targets

    def test_region_config_no_replication(self, nigeria_region):
        """Test region without replication targets"""
        assert len(nigeria_region.config.replication_targets) == 0


class TestMultipleRegions:
    """Tests for multiple region scenarios"""

    def test_nigeria_region_properties(self, nigeria_region):
        """Test Nigeria region properties (INV-007)"""
        assert nigeria_region.country_code == "NG"
        assert nigeria_region.aws_region == "af-west-1"

    def test_eu_region_properties(self, eu_region):
        """Test EU region properties"""
        assert eu_region.country_code == "IE"
        assert eu_region.aws_region == "eu-west-1"

    def test_us_region_properties(self, us_region):
        """Test US region properties"""
        assert us_region.country_code == "US"
        assert us_region.aws_region == "us-east-1"

    def test_region_comparison(self, nigeria_region, eu_region, us_region):
        """Test region comparison"""
        regions = [nigeria_region, eu_region, us_region]
        
        assert len(regions) == 3
        assert all(r.status == RegionStatus.ACTIVE for r in regions)
        
        # Verify unique IDs
        ids = [r.id for r in regions]
        assert len(ids) == len(set(ids))
