"""
Unit Tests for ID-1 Deployment Models

Tests for Deployment, DeploymentManifest, and related models.
"""

import pytest
from datetime import datetime, timedelta

from src.models.deployment import (
    Deployment, DeploymentStatus, DeploymentManifest,
    DeploymentRequest, DeploymentResponse
)


class TestDeploymentManifest:
    """Tests for DeploymentManifest model"""

    def test_create_manifest(self, sample_manifest):
        """Test creating a deployment manifest"""
        assert sample_manifest.id == "manifest-001"
        assert sample_manifest.version == "1.0.0"
        assert sample_manifest.platform_version == "2.0.0"
        assert "commerce" in sample_manifest.suites
        assert sample_manifest.suites["commerce"] == "1.5.0"

    def test_manifest_with_suites(self, sample_manifest):
        """Test manifest with multiple suites"""
        assert len(sample_manifest.suites) == 3
        assert sample_manifest.suites["mlas"] == "1.2.0"
        assert sample_manifest.suites["transport"] == "1.0.0"

    def test_manifest_with_capabilities(self, sample_manifest):
        """Test manifest with capabilities"""
        assert len(sample_manifest.capabilities) == 2
        assert sample_manifest.capabilities["reporting"] == "1.0.0"

    def test_manifest_configuration(self, sample_manifest):
        """Test manifest configuration"""
        assert sample_manifest.configuration["environment"] == "production"
        assert sample_manifest.configuration["replicas"] == 3

    def test_manifest_nigeria_region(self, sample_manifest):
        """Test manifest with Nigeria region (INV-007)"""
        assert sample_manifest.configuration["region"] == "af-west-1"

    def test_manifest_metadata(self, sample_manifest):
        """Test manifest metadata"""
        assert sample_manifest.metadata["created_by"] == "admin"


class TestDeployment:
    """Tests for Deployment model"""

    def test_create_deployment(self, sample_deployment):
        """Test creating a deployment"""
        deployment = Deployment(**sample_deployment)
        
        assert deployment.id == "deploy-001"
        assert deployment.manifest_id == "manifest-001"
        assert deployment.instance_id == "instance-prod-01"
        assert deployment.status == DeploymentStatus.PENDING

    def test_deployment_status_transitions(self, sample_deployment):
        """Test deployment status transitions"""
        deployment = Deployment(**sample_deployment)
        
        # Pending -> Compiling
        deployment.status = DeploymentStatus.COMPILING
        assert deployment.status == DeploymentStatus.COMPILING
        
        # Compiling -> Deploying
        deployment.status = DeploymentStatus.DEPLOYING
        assert deployment.status == DeploymentStatus.DEPLOYING
        
        # Deploying -> Deployed
        deployment.status = DeploymentStatus.DEPLOYED
        assert deployment.status == DeploymentStatus.DEPLOYED

    def test_deployment_failure(self, sample_deployment):
        """Test deployment failure"""
        deployment = Deployment(**sample_deployment)
        
        deployment.status = DeploymentStatus.FAILED
        deployment.error_message = "Deployment validation failed"
        
        assert deployment.status == DeploymentStatus.FAILED
        assert deployment.error_message == "Deployment validation failed"

    def test_deployment_rollback(self, sample_deployment):
        """Test deployment rollback status"""
        deployment = Deployment(**sample_deployment)
        deployment.status = DeploymentStatus.ROLLED_BACK
        
        assert deployment.status == DeploymentStatus.ROLLED_BACK

    def test_deployment_cancellation(self, sample_deployment):
        """Test deployment cancellation"""
        deployment = Deployment(**sample_deployment)
        deployment.status = DeploymentStatus.CANCELLED
        
        assert deployment.status == DeploymentStatus.CANCELLED

    def test_deployment_logs(self, sample_deployment):
        """Test deployment logs"""
        deployment = Deployment(**sample_deployment)
        
        deployment.logs.append("Starting deployment")
        deployment.logs.append("Validating manifest")
        deployment.logs.append("Deployment complete")
        
        assert len(deployment.logs) == 3
        assert "Starting deployment" in deployment.logs

    def test_deployment_timestamps(self, sample_deployment):
        """Test deployment timestamps"""
        deployment = Deployment(**sample_deployment)
        
        deployment.started_at = datetime.utcnow()
        deployment.completed_at = datetime.utcnow() + timedelta(minutes=10)
        
        assert deployment.started_at is not None
        assert deployment.completed_at is not None
        assert deployment.completed_at > deployment.started_at


class TestDeploymentRequest:
    """Tests for DeploymentRequest model"""

    def test_create_deployment_request(self):
        """Test creating a deployment request"""
        request = DeploymentRequest(
            manifest_id="manifest-001",
            instance_id="instance-prod-01",
            dry_run=False,
            skip_validation=False
        )
        
        assert request.manifest_id == "manifest-001"
        assert request.instance_id == "instance-prod-01"
        assert request.dry_run is False

    def test_deployment_request_dry_run(self):
        """Test deployment request with dry run"""
        request = DeploymentRequest(
            manifest_id="manifest-001",
            instance_id="instance-prod-01",
            dry_run=True
        )
        
        assert request.dry_run is True

    def test_deployment_request_skip_validation(self):
        """Test deployment request with skip validation"""
        request = DeploymentRequest(
            manifest_id="manifest-001",
            instance_id="instance-prod-01",
            skip_validation=True
        )
        
        assert request.skip_validation is True


class TestDeploymentResponse:
    """Tests for DeploymentResponse model"""

    def test_deployment_response(self, sample_deployment):
        """Test deployment response"""
        deployment = Deployment(**sample_deployment)
        
        response = DeploymentResponse(
            id=deployment.id,
            status=deployment.status,
            manifest_id=deployment.manifest_id,
            instance_id=deployment.instance_id,
            created_at=deployment.created_at,
            started_at=None,
            completed_at=None,
            error_message=None
        )
        
        assert response.id == "deploy-001"
        assert response.status == DeploymentStatus.PENDING

    def test_deployment_response_with_error(self, sample_deployment):
        """Test deployment response with error"""
        response = DeploymentResponse(
            id="deploy-001",
            status=DeploymentStatus.FAILED,
            manifest_id="manifest-001",
            instance_id="instance-prod-01",
            created_at=datetime.utcnow(),
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            error_message="Validation failed"
        )
        
        assert response.status == DeploymentStatus.FAILED
        assert response.error_message == "Validation failed"
