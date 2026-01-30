"""Unit tests for multi-region engine."""

import pytest
from src.core.multi_region_engine import MultiRegionEngine
from src.models.region import RegionStatus


@pytest.fixture
def engine():
    """Create multi-region engine instance."""
    return MultiRegionEngine()


@pytest.mark.asyncio
async def test_register_region(engine):
    """Test region registration."""
    region = await engine.register_region(
        name="US East (N. Virginia)",
        aws_region="us-east-1",
        country_code="US",
        data_center_location="Virginia, USA",
        availability_zones=["us-east-1a", "us-east-1b", "us-east-1c"]
    )
    
    assert region.id == "region-us-east-1"
    assert region.name == "US East (N. Virginia)"
    assert region.aws_region == "us-east-1"
    assert region.status == RegionStatus.PROVISIONING


@pytest.mark.asyncio
async def test_activate_region(engine):
    """Test region activation."""
    region = await engine.register_region(
        name="US East (N. Virginia)",
        aws_region="us-east-1",
        country_code="US",
        data_center_location="Virginia, USA",
        availability_zones=["us-east-1a", "us-east-1b", "us-east-1c"]
    )
    
    activated = await engine.activate_region(region.id)
    
    assert activated is not None
    assert activated.status == RegionStatus.ACTIVE


@pytest.mark.asyncio
async def test_get_region(engine):
    """Test retrieving region."""
    region = await engine.register_region(
        name="US East (N. Virginia)",
        aws_region="us-east-1",
        country_code="US",
        data_center_location="Virginia, USA",
        availability_zones=["us-east-1a", "us-east-1b", "us-east-1c"]
    )
    
    retrieved = engine.get_region(region.id)
    
    assert retrieved is not None
    assert retrieved.id == region.id


@pytest.mark.asyncio
async def test_list_regions(engine):
    """Test listing regions."""
    await engine.register_region(
        name="US East (N. Virginia)",
        aws_region="us-east-1",
        country_code="US",
        data_center_location="Virginia, USA",
        availability_zones=["us-east-1a", "us-east-1b", "us-east-1c"]
    )
    
    await engine.register_region(
        name="EU West (Ireland)",
        aws_region="eu-west-1",
        country_code="IE",
        data_center_location="Dublin, Ireland",
        availability_zones=["eu-west-1a", "eu-west-1b", "eu-west-1c"]
    )
    
    regions = engine.list_regions()
    assert len(regions) == 2


@pytest.mark.asyncio
async def test_delete_region(engine):
    """Test region deletion."""
    region = await engine.register_region(
        name="US East (N. Virginia)",
        aws_region="us-east-1",
        country_code="US",
        data_center_location="Virginia, USA",
        availability_zones=["us-east-1a", "us-east-1b", "us-east-1c"]
    )
    
    deleted = await engine.delete_region(region.id)
    
    assert deleted is True
    assert engine.get_region(region.id) is None
