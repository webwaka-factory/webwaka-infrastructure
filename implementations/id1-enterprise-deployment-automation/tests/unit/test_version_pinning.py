"""
Unit Tests for ID-1 Version Pinning

Tests for VersionPin and version management.
"""

import pytest
from datetime import datetime, timedelta

from src.models.version import VersionPin


class TestVersionPin:
    """Tests for VersionPin model"""

    def test_create_version_pin(self, sample_version_pin):
        """Test creating a version pin"""
        pin = VersionPin(**sample_version_pin)
        
        assert pin.id == "pin-001"
        assert pin.instance_id == "instance-prod-01"
        assert pin.component_name == "commerce"
        assert pin.pinned_version == "1.4.0"

    def test_version_pin_with_reason(self, sample_version_pin):
        """Test version pin with reason"""
        pin = VersionPin(**sample_version_pin)
        
        assert pin.reason == "Stable version for production"

    def test_version_pin_component_type(self, sample_version_pin):
        """Test version pin component type"""
        pin = VersionPin(**sample_version_pin)
        
        assert pin.component_type == "suite"

    def test_version_pin_expiration(self):
        """Test version pin with expiration"""
        pin = VersionPin(
            id="pin-001",
            instance_id="instance-prod-01",
            component_type="suite",
            component_name="commerce",
            pinned_version="1.4.0",
            reason="Temporary pin",
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        
        assert pin.expires_at is not None


class TestVersionPinValidation:
    """Tests for version pin validation"""

    def test_valid_semver_version(self):
        """Test valid semantic version"""
        pin = VersionPin(
            id="pin-001",
            instance_id="instance-prod-01",
            component_type="suite",
            component_name="commerce",
            pinned_version="1.4.0",
            reason="Valid semver"
        )
        
        assert pin.pinned_version == "1.4.0"

    def test_valid_prerelease_version(self):
        """Test valid prerelease version"""
        pin = VersionPin(
            id="pin-001",
            instance_id="instance-prod-01",
            component_type="suite",
            component_name="commerce",
            pinned_version="1.4.0-beta.1",
            reason="Prerelease version"
        )
        
        assert "beta" in pin.pinned_version


class TestVersionPinScenarios:
    """Tests for version pin scenarios"""

    def test_production_version_lock(self):
        """Test production version lock scenario"""
        pins = [
            VersionPin(
                id="pin-prod-001",
                instance_id="instance-prod-01",
                component_type="platform",
                component_name="webwaka-platform",
                pinned_version="2.0.0",
                reason="Production stability"
            ),
            VersionPin(
                id="pin-prod-002",
                instance_id="instance-prod-01",
                component_type="suite",
                component_name="commerce",
                pinned_version="1.5.0",
                reason="Production stability"
            )
        ]
        
        assert len(pins) == 2

    def test_nigeria_instance_version_pin(self, nigeria_instance_config):
        """Test Nigeria instance version pin (INV-007)"""
        pin = VersionPin(
            id="pin-ng-001",
            instance_id=nigeria_instance_config["instance_id"],
            component_type="suite",
            component_name="commerce",
            pinned_version="1.5.0",
            reason="Stable version for Nigeria deployment"
        )
        
        assert pin.instance_id == "instance-ng-prod-01"

    def test_platform_version_pin(self):
        """Test platform version pin"""
        pin = VersionPin(
            id="pin-platform-001",
            instance_id="instance-prod-01",
            component_type="platform",
            component_name="webwaka-platform",
            pinned_version="2.0.0",
            reason="Lock platform version"
        )
        
        assert pin.component_type == "platform"

    def test_capability_version_pin(self):
        """Test capability version pin"""
        pin = VersionPin(
            id="pin-cap-001",
            instance_id="instance-prod-01",
            component_type="capability",
            component_name="reporting",
            pinned_version="1.0.0",
            reason="Lock reporting capability"
        )
        
        assert pin.component_type == "capability"
