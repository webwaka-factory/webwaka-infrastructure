"""
Integration Tests for ID-1 Deployment Flows

Tests for complete deployment workflows.
"""

import pytest
from datetime import datetime, timedelta

from src.core.deployment_engine import DeploymentEngine
from src.models.deployment import DeploymentStatus, DeploymentManifest
from src.models.policy import PolicyType


class TestDeploymentWorkflow:
    """Tests for complete deployment workflow"""

    @pytest.mark.asyncio
    async def test_complete_deployment_flow(self, deployment_engine, sample_manifest):
        """Test complete deployment flow"""
        # Step 1: Create deployment
        deployment = await deployment_engine.create_deployment(
            manifest=sample_manifest,
            instance_id="instance-prod-01"
        )
        
        assert deployment.status == DeploymentStatus.PENDING
        
        # Step 2: Execute deployment
        result = await deployment_engine.execute_deployment(deployment, sample_manifest)
        
        assert result.status == DeploymentStatus.DEPLOYED
        assert result.completed_at is not None

    @pytest.mark.asyncio
    async def test_deployment_with_policy(self, deployment_engine, sample_manifest, sample_policy):
        """Test deployment with policy enforcement"""
        deployment = await deployment_engine.create_deployment(
            manifest=sample_manifest,
            instance_id="instance-prod-01",
            policy=sample_policy
        )
        
        assert deployment.status == DeploymentStatus.PENDING

    @pytest.mark.asyncio
    async def test_deployment_dry_run(self, deployment_engine, sample_manifest):
        """Test deployment dry run"""
        deployment = await deployment_engine.create_deployment(
            manifest=sample_manifest,
            instance_id="instance-prod-01",
            dry_run=True
        )
        
        assert deployment.status == DeploymentStatus.PENDING

    @pytest.mark.asyncio
    async def test_deployment_listing(self, deployment_engine, sample_manifest):
        """Test deployment listing"""
        # Create multiple deployments
        await deployment_engine.create_deployment(
            manifest=sample_manifest,
            instance_id="instance-prod-01"
        )
        
        deployments = deployment_engine.list_deployments()
        assert len(deployments) >= 1

    @pytest.mark.asyncio
    async def test_deployment_listing_by_instance(self, deployment_engine, sample_manifest):
        """Test deployment listing by instance"""
        await deployment_engine.create_deployment(
            manifest=sample_manifest,
            instance_id="instance-prod-01"
        )
        
        await deployment_engine.create_deployment(
            manifest=sample_manifest,
            instance_id="instance-dev-01"
        )
        
        prod_deployments = deployment_engine.list_deployments(instance_id="instance-prod-01")
        assert all(d.instance_id == "instance-prod-01" for d in prod_deployments)


class TestRollbackWorkflow:
    """Tests for rollback workflow"""

    @pytest.mark.asyncio
    async def test_deployment_rollback_flow(self, deployment_engine, rollback_manager, sample_manifest):
        """Test deployment rollback flow"""
        # Step 1: Create and execute deployment
        deployment = await deployment_engine.create_deployment(
            manifest=sample_manifest,
            instance_id="instance-prod-01"
        )
        await deployment_engine.execute_deployment(deployment, sample_manifest)
        
        # Step 2: Initiate rollback
        rollback = await rollback_manager.initiate_rollback(
            instance_id="instance-prod-01",
            from_manifest_id=sample_manifest.id,
            to_manifest_id="manifest-000",
            reason="Performance issues"
        )
        
        # Step 3: Execute rollback
        result = await rollback_manager.execute_rollback(rollback)
        
        assert result.status.value == "completed"

    @pytest.mark.asyncio
    async def test_rollback_history_tracking(self, rollback_manager, sample_manifest):
        """Test rollback history tracking"""
        # Record manifest version
        await rollback_manager.record_manifest_version(
            instance_id="instance-prod-01",
            manifest=sample_manifest,
            deployment_id="deploy-001",
            status="deployed"
        )
        
        # Get history
        history = await rollback_manager.get_rollback_history("instance-prod-01")
        
        assert history.instance_id == "instance-prod-01"


class TestPolicyEnforcement:
    """Tests for policy enforcement during deployment"""

    @pytest.mark.asyncio
    async def test_auto_update_policy(self, deployment_engine, sample_manifest, sample_auto_update_policy):
        """Test deployment with auto-update policy"""
        deployment = await deployment_engine.create_deployment(
            manifest=sample_manifest,
            instance_id="instance-dev-01",
            policy=sample_auto_update_policy
        )
        
        assert deployment.status == DeploymentStatus.PENDING

    @pytest.mark.asyncio
    async def test_frozen_policy(self, deployment_engine, sample_manifest, sample_frozen_policy):
        """Test deployment with frozen policy"""
        deployment = await deployment_engine.create_deployment(
            manifest=sample_manifest,
            instance_id="instance-stable-01",
            policy=sample_frozen_policy
        )
        
        assert deployment.status == DeploymentStatus.PENDING


class TestMultiRegionDeployment:
    """Tests for multi-region deployment (INV-007)"""

    @pytest.mark.asyncio
    async def test_nigeria_region_deployment(self, deployment_engine, sample_manifest, nigeria_instance_config):
        """Test deployment to Nigeria region"""
        # Update manifest for Nigeria
        sample_manifest.configuration["region"] = "af-west-1"
        sample_manifest.configuration["country"] = "NG"
        
        deployment = await deployment_engine.create_deployment(
            manifest=sample_manifest,
            instance_id=nigeria_instance_config["instance_id"]
        )
        
        assert deployment.instance_id == "instance-ng-prod-01"

    @pytest.mark.asyncio
    async def test_multi_region_deployment_sequence(self, deployment_engine, multi_region_manifests):
        """Test multi-region deployment sequence"""
        deployments = []
        
        for manifest in multi_region_manifests:
            deployment = await deployment_engine.create_deployment(
                manifest=manifest,
                instance_id=f"instance-{manifest.configuration['country'].lower()}-01"
            )
            deployments.append(deployment)
        
        assert len(deployments) == 3
        
        # Verify each region
        regions = [d.instance_id for d in deployments]
        assert "instance-ng-01" in regions
        assert "instance-us-01" in regions
        assert "instance-eu-01" in regions


class TestDeploymentValidation:
    """Tests for deployment validation"""

    @pytest.mark.asyncio
    async def test_manifest_validation(self, deployment_engine, sample_manifest):
        """Test manifest validation during deployment"""
        deployment = await deployment_engine.create_deployment(
            manifest=sample_manifest,
            instance_id="instance-prod-01"
        )
        
        # Deployment should be created if validation passes
        assert deployment is not None

    @pytest.mark.asyncio
    async def test_deployment_logs(self, deployment_engine, sample_manifest):
        """Test deployment logs are recorded"""
        deployment = await deployment_engine.create_deployment(
            manifest=sample_manifest,
            instance_id="instance-prod-01"
        )
        
        result = await deployment_engine.execute_deployment(deployment, sample_manifest)
        
        assert len(result.logs) > 0
        assert any("compilation" in log.lower() for log in result.logs)
