"""Unit tests for deployment engine."""

import pytest
from datetime import datetime

from src.core.deployment_engine import DeploymentEngine
from src.core.validator import DeploymentValidator
from src.models.deployment import DeploymentManifest, DeploymentStatus


@pytest.fixture
def deployment_engine():
    """Create deployment engine instance."""
    return DeploymentEngine()


@pytest.fixture
def sample_manifest():
    """Create sample deployment manifest."""
    return DeploymentManifest(
        id="manifest-001",
        version="1.0.0",
        platform_version="2.0.0",
        suites={"commerce": "1.5.0"},
        capabilities={"reporting": "1.0.0"}
    )


@pytest.mark.asyncio
async def test_create_deployment(deployment_engine, sample_manifest):
    """Test deployment creation."""
    deployment = await deployment_engine.create_deployment(
        manifest=sample_manifest,
        instance_id="instance-001"
    )
    
    assert deployment.id is not None
    assert deployment.manifest_id == "manifest-001"
    assert deployment.instance_id == "instance-001"
    assert deployment.status == DeploymentStatus.PENDING


@pytest.mark.asyncio
async def test_get_deployment(deployment_engine, sample_manifest):
    """Test retrieving deployment."""
    deployment = await deployment_engine.create_deployment(
        manifest=sample_manifest,
        instance_id="instance-001"
    )
    
    retrieved = deployment_engine.get_deployment(deployment.id)
    
    assert retrieved is not None
    assert retrieved.id == deployment.id
    assert retrieved.manifest_id == deployment.manifest_id


@pytest.mark.asyncio
async def test_list_deployments(deployment_engine, sample_manifest):
    """Test listing deployments."""
    await deployment_engine.create_deployment(
        manifest=sample_manifest,
        instance_id="instance-001"
    )
    
    await deployment_engine.create_deployment(
        manifest=sample_manifest,
        instance_id="instance-002"
    )
    
    all_deployments = deployment_engine.list_deployments()
    assert len(all_deployments) == 2
    
    instance_deployments = deployment_engine.list_deployments("instance-001")
    assert len(instance_deployments) == 1
    assert instance_deployments[0].instance_id == "instance-001"


@pytest.mark.asyncio
async def test_execute_deployment(deployment_engine, sample_manifest):
    """Test deployment execution."""
    deployment = await deployment_engine.create_deployment(
        manifest=sample_manifest,
        instance_id="instance-001"
    )
    
    executed = await deployment_engine.execute_deployment(deployment, sample_manifest)
    
    assert executed.status == DeploymentStatus.DEPLOYED
    assert executed.started_at is not None
    assert executed.completed_at is not None
    assert len(executed.logs) > 0


@pytest.mark.asyncio
async def test_deployment_validation_failure(deployment_engine):
    """Test deployment with invalid manifest."""
    invalid_manifest = DeploymentManifest(
        id="",
        version="1.0.0",
        platform_version=""
    )
    
    with pytest.raises(ValueError):
        await deployment_engine.create_deployment(
            manifest=invalid_manifest,
            instance_id="instance-001"
        )
