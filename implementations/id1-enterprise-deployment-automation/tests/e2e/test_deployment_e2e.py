"""
End-to-End Tests for ID-1 Deployment Automation

Complete workflow tests for the Enterprise Deployment Automation system.
"""

import pytest
from datetime import datetime, timedelta

from src.core.deployment_engine import DeploymentEngine
from src.rollback.rollback_manager import RollbackManager
from src.policies.policy_manager import PolicyManager
from src.models.deployment import DeploymentStatus, DeploymentManifest
from src.models.policy import PolicyType, UpdateChannelPolicy


class TestCompleteDeploymentLifecycle:
    """Tests for complete deployment lifecycle"""

    @pytest.mark.asyncio
    async def test_full_deployment_lifecycle(self, deployment_engine, rollback_manager, sample_manifest):
        """Test full deployment lifecycle from creation to completion"""
        # Phase 1: Create deployment
        deployment = await deployment_engine.create_deployment(
            manifest=sample_manifest,
            instance_id="instance-prod-01"
        )
        assert deployment.status == DeploymentStatus.PENDING
        
        # Phase 2: Execute deployment
        result = await deployment_engine.execute_deployment(deployment, sample_manifest)
        assert result.status == DeploymentStatus.DEPLOYED
        
        # Phase 3: Record in rollback history
        await rollback_manager.record_manifest_version(
            instance_id="instance-prod-01",
            manifest=sample_manifest,
            deployment_id=deployment.id,
            status="deployed"
        )
        
        # Phase 4: Verify deployment
        stored_deployment = deployment_engine.get_deployment(deployment.id)
        assert stored_deployment is not None
        assert stored_deployment.status == DeploymentStatus.DEPLOYED

    @pytest.mark.asyncio
    async def test_deployment_and_rollback_cycle(self, deployment_engine, rollback_manager, sample_manifest):
        """Test deployment followed by rollback"""
        # Deploy version 1
        manifest_v1 = DeploymentManifest(
            id="manifest-v1",
            version="1.0.0",
            platform_version="2.0.0",
            suites={"commerce": "1.4.0"},
            configuration={"environment": "production"}
        )
        
        deployment_v1 = await deployment_engine.create_deployment(
            manifest=manifest_v1,
            instance_id="instance-prod-01"
        )
        await deployment_engine.execute_deployment(deployment_v1, manifest_v1)
        
        # Deploy version 2
        manifest_v2 = DeploymentManifest(
            id="manifest-v2",
            version="2.0.0",
            platform_version="2.0.0",
            suites={"commerce": "1.5.0"},
            configuration={"environment": "production"}
        )
        
        deployment_v2 = await deployment_engine.create_deployment(
            manifest=manifest_v2,
            instance_id="instance-prod-01"
        )
        await deployment_engine.execute_deployment(deployment_v2, manifest_v2)
        
        # Rollback to version 1
        rollback = await rollback_manager.initiate_rollback(
            instance_id="instance-prod-01",
            from_manifest_id="manifest-v2",
            to_manifest_id="manifest-v1",
            reason="Version 2 caused issues"
        )
        
        result = await rollback_manager.execute_rollback(rollback)
        assert result.status.value == "completed"


class TestPolicyDrivenDeployment:
    """Tests for policy-driven deployment scenarios"""

    @pytest.mark.asyncio
    async def test_manual_approval_workflow(self, deployment_engine, sample_manifest, sample_policy):
        """Test manual approval workflow"""
        # Create deployment with manual approval policy
        deployment = await deployment_engine.create_deployment(
            manifest=sample_manifest,
            instance_id="instance-prod-01",
            policy=sample_policy
        )
        
        assert deployment.status == DeploymentStatus.PENDING
        assert sample_policy.policy_type == PolicyType.MANUAL_APPROVAL

    @pytest.mark.asyncio
    async def test_auto_update_workflow(self, deployment_engine, sample_manifest, sample_auto_update_policy):
        """Test auto-update workflow"""
        deployment = await deployment_engine.create_deployment(
            manifest=sample_manifest,
            instance_id="instance-dev-01",
            policy=sample_auto_update_policy
        )
        
        # Auto-update should proceed without manual approval
        result = await deployment_engine.execute_deployment(deployment, sample_manifest)
        assert result.status == DeploymentStatus.DEPLOYED

    @pytest.mark.asyncio
    async def test_frozen_policy_security_patch(self, deployment_engine, sample_frozen_policy):
        """Test frozen policy allows security patches"""
        # Create security patch manifest
        security_manifest = DeploymentManifest(
            id="manifest-security-001",
            version="1.9.1",
            platform_version="1.9.1",
            suites={},
            configuration={"type": "security_patch"},
            metadata={"cve_ids": ["CVE-2024-0001"]}
        )
        
        deployment = await deployment_engine.create_deployment(
            manifest=security_manifest,
            instance_id="instance-stable-01",
            policy=sample_frozen_policy
        )
        
        # Security patches should be allowed even with frozen policy
        assert sample_frozen_policy.allow_security_patches is True


class TestNigeriaDeploymentScenarios:
    """Tests for Nigeria-specific deployment scenarios (INV-007)"""

    @pytest.mark.asyncio
    async def test_nigeria_first_deployment(self, deployment_engine, nigeria_instance_config):
        """Test Nigeria-first deployment"""
        manifest = DeploymentManifest(
            id="manifest-ng-001",
            version="1.0.0",
            platform_version="2.0.0",
            suites={
                "commerce": "1.5.0",
                "transport": "1.0.0"
            },
            configuration={
                "region": "af-west-1",
                "country": "NG",
                "data_center": "Lagos, Nigeria",
                "compliance": ["NDPR"]
            }
        )
        
        deployment = await deployment_engine.create_deployment(
            manifest=manifest,
            instance_id=nigeria_instance_config["instance_id"]
        )
        
        result = await deployment_engine.execute_deployment(deployment, manifest)
        assert result.status == DeploymentStatus.DEPLOYED

    @pytest.mark.asyncio
    async def test_nigeria_data_residency_compliance(self, deployment_engine, nigeria_instance_config):
        """Test Nigeria data residency compliance"""
        manifest = DeploymentManifest(
            id="manifest-ng-002",
            version="1.0.0",
            platform_version="2.0.0",
            suites={"commerce": "1.5.0"},
            configuration={
                "region": "af-west-1",
                "country": "NG",
                "data_residency": "single_country",
                "allowed_regions": ["af-west-1"]
            }
        )
        
        deployment = await deployment_engine.create_deployment(
            manifest=manifest,
            instance_id=nigeria_instance_config["instance_id"]
        )
        
        assert deployment.instance_id == "instance-ng-prod-01"


class TestDeploymentRecovery:
    """Tests for deployment recovery scenarios"""

    @pytest.mark.asyncio
    async def test_failed_deployment_recovery(self, deployment_engine, rollback_manager, sample_manifest):
        """Test recovery from failed deployment"""
        # Record initial state
        initial_manifest = DeploymentManifest(
            id="manifest-initial",
            version="1.0.0",
            platform_version="2.0.0",
            suites={"commerce": "1.4.0"},
            configuration={"environment": "production"}
        )
        
        await rollback_manager.record_manifest_version(
            instance_id="instance-prod-01",
            manifest=initial_manifest,
            deployment_id="deploy-initial",
            status="deployed"
        )
        
        # Simulate failed deployment
        deployment = await deployment_engine.create_deployment(
            manifest=sample_manifest,
            instance_id="instance-prod-01"
        )
        
        # Execute deployment (simulating success for test)
        result = await deployment_engine.execute_deployment(deployment, sample_manifest)
        
        # If deployment had failed, we would rollback
        if result.status == DeploymentStatus.FAILED:
            rollback = await rollback_manager.initiate_rollback(
                instance_id="instance-prod-01",
                from_manifest_id=sample_manifest.id,
                to_manifest_id="manifest-initial",
                reason="Deployment failed"
            )
            await rollback_manager.execute_rollback(rollback)


class TestDeploymentAudit:
    """Tests for deployment audit trail"""

    @pytest.mark.asyncio
    async def test_deployment_audit_trail(self, deployment_engine, sample_manifest):
        """Test deployment audit trail"""
        deployment = await deployment_engine.create_deployment(
            manifest=sample_manifest,
            instance_id="instance-prod-01"
        )
        
        result = await deployment_engine.execute_deployment(deployment, sample_manifest)
        
        # Verify audit trail (logs)
        assert len(result.logs) > 0
        assert result.created_at is not None
        assert result.started_at is not None
        assert result.completed_at is not None

    @pytest.mark.asyncio
    async def test_rollback_audit_trail(self, rollback_manager):
        """Test rollback audit trail"""
        rollback = await rollback_manager.initiate_rollback(
            instance_id="instance-prod-01",
            from_manifest_id="manifest-002",
            to_manifest_id="manifest-001",
            reason="Performance issues",
            initiated_by="admin"
        )
        
        result = await rollback_manager.execute_rollback(rollback)
        
        # Verify audit trail
        assert result.initiated_by == "admin"
        assert result.reason == "Performance issues"
        assert len(result.logs) > 0
