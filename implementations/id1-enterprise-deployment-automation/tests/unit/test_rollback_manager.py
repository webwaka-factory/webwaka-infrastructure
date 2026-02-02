"""
Unit Tests for ID-1 Rollback Manager

Tests for RollbackManager and related functionality.
"""

import pytest
from datetime import datetime, timedelta

from src.models.rollback import (
    RollbackRecord, RollbackStatus, ManifestVersion, RollbackHistory
)
from src.rollback.rollback_manager import RollbackManager


class TestRollbackManager:
    """Tests for RollbackManager"""

    @pytest.mark.asyncio
    async def test_initiate_rollback(self, rollback_manager):
        """Test initiating a rollback"""
        rollback = await rollback_manager.initiate_rollback(
            instance_id="instance-prod-01",
            from_manifest_id="manifest-002",
            to_manifest_id="manifest-001",
            reason="Performance degradation",
            initiated_by="admin"
        )
        
        assert rollback.instance_id == "instance-prod-01"
        assert rollback.from_manifest_id == "manifest-002"
        assert rollback.to_manifest_id == "manifest-001"
        assert rollback.status == RollbackStatus.PENDING
        assert rollback.reason == "Performance degradation"

    @pytest.mark.asyncio
    async def test_execute_rollback(self, rollback_manager):
        """Test executing a rollback"""
        rollback = await rollback_manager.initiate_rollback(
            instance_id="instance-prod-01",
            from_manifest_id="manifest-002",
            to_manifest_id="manifest-001"
        )
        
        result = await rollback_manager.execute_rollback(rollback)
        
        assert result.status == RollbackStatus.COMPLETED
        assert result.completed_at is not None
        assert len(result.logs) > 0

    @pytest.mark.asyncio
    async def test_rollback_status_transitions(self, rollback_manager):
        """Test rollback status transitions"""
        rollback = await rollback_manager.initiate_rollback(
            instance_id="instance-prod-01",
            from_manifest_id="manifest-002",
            to_manifest_id="manifest-001"
        )
        
        assert rollback.status == RollbackStatus.PENDING
        
        # Execute rollback
        result = await rollback_manager.execute_rollback(rollback)
        assert result.status == RollbackStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_record_manifest_version(self, rollback_manager, sample_manifest):
        """Test recording manifest version"""
        version = await rollback_manager.record_manifest_version(
            instance_id="instance-prod-01",
            manifest=sample_manifest,
            deployment_id="deploy-001",
            status="deployed"
        )
        
        assert version.id == sample_manifest.id
        assert version.version == sample_manifest.version
        assert version.deployment_id == "deploy-001"

    @pytest.mark.asyncio
    async def test_get_rollback_history(self, rollback_manager):
        """Test getting rollback history"""
        # Create some rollbacks
        await rollback_manager.initiate_rollback(
            instance_id="instance-prod-01",
            from_manifest_id="manifest-002",
            to_manifest_id="manifest-001"
        )
        
        history = await rollback_manager.get_rollback_history("instance-prod-01")
        
        assert history.instance_id == "instance-prod-01"
        assert history.total_rollbacks >= 1

    def test_get_rollback(self, rollback_manager):
        """Test getting rollback by ID"""
        # Non-existent rollback
        rollback = rollback_manager.get_rollback("nonexistent")
        assert rollback is None

    @pytest.mark.asyncio
    async def test_list_rollbacks(self, rollback_manager):
        """Test listing rollbacks"""
        await rollback_manager.initiate_rollback(
            instance_id="instance-prod-01",
            from_manifest_id="manifest-002",
            to_manifest_id="manifest-001"
        )
        
        rollbacks = rollback_manager.list_rollbacks()
        assert len(rollbacks) >= 1

    @pytest.mark.asyncio
    async def test_list_rollbacks_by_instance(self, rollback_manager):
        """Test listing rollbacks by instance"""
        await rollback_manager.initiate_rollback(
            instance_id="instance-prod-01",
            from_manifest_id="manifest-002",
            to_manifest_id="manifest-001"
        )
        
        await rollback_manager.initiate_rollback(
            instance_id="instance-dev-01",
            from_manifest_id="manifest-003",
            to_manifest_id="manifest-002"
        )
        
        prod_rollbacks = rollback_manager.list_rollbacks(instance_id="instance-prod-01")
        assert all(r.instance_id == "instance-prod-01" for r in prod_rollbacks)


class TestRollbackRecord:
    """Tests for RollbackRecord model"""

    def test_create_rollback_record(self, sample_rollback):
        """Test creating a rollback record"""
        rollback = RollbackRecord(**sample_rollback)
        
        assert rollback.id == "rollback-001"
        assert rollback.instance_id == "instance-prod-01"
        assert rollback.status == RollbackStatus.PENDING

    def test_rollback_status_values(self):
        """Test rollback status values"""
        assert RollbackStatus.PENDING.value == "pending"
        assert RollbackStatus.IN_PROGRESS.value == "in_progress"
        assert RollbackStatus.COMPLETED.value == "completed"
        assert RollbackStatus.FAILED.value == "failed"

    def test_rollback_with_logs(self, sample_rollback):
        """Test rollback with logs"""
        rollback = RollbackRecord(**sample_rollback)
        
        rollback.logs.append("Starting rollback")
        rollback.logs.append("Validating target manifest")
        rollback.logs.append("Rollback complete")
        
        assert len(rollback.logs) == 3


class TestManifestVersion:
    """Tests for ManifestVersion model"""

    def test_create_manifest_version(self):
        """Test creating a manifest version"""
        version = ManifestVersion(
            id="manifest-001",
            version="1.0.0",
            deployed_at=datetime.utcnow(),
            deployment_id="deploy-001",
            status="deployed"
        )
        
        assert version.id == "manifest-001"
        assert version.version == "1.0.0"
        assert version.status == "deployed"


class TestRollbackHistory:
    """Tests for RollbackHistory model"""

    def test_create_rollback_history(self):
        """Test creating rollback history"""
        history = RollbackHistory(
            instance_id="instance-prod-01",
            total_rollbacks=5,
            successful_rollbacks=4,
            failed_rollbacks=1,
            recent_rollbacks=[],
            available_manifests=[]
        )
        
        assert history.instance_id == "instance-prod-01"
        assert history.total_rollbacks == 5
        assert history.successful_rollbacks == 4
        assert history.failed_rollbacks == 1
