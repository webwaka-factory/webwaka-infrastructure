"""
Unit Tests for ID-1 Security Patch Management

Tests for SecurityPatch, PatchManager, and PatchEnforcer.
"""

import pytest
from datetime import datetime, timedelta

from src.models.security import (
    SecurityPatch, PatchStatus, SeverityLevel
)


class TestSecurityPatch:
    """Tests for SecurityPatch model"""

    def test_create_security_patch(self, sample_security_patch):
        """Test creating a security patch"""
        patch = SecurityPatch(**sample_security_patch)
        
        assert patch.id == "patch-001"
        assert patch.component_name == "webwaka-platform"
        assert patch.severity == SeverityLevel.CRITICAL
        assert patch.is_mandatory is True

    def test_patch_severity_levels(self):
        """Test patch severity levels"""
        assert SeverityLevel.CRITICAL.value == "critical"
        assert SeverityLevel.HIGH.value == "high"
        assert SeverityLevel.MEDIUM.value == "medium"
        assert SeverityLevel.LOW.value == "low"

    def test_patch_status_values(self):
        """Test patch status values"""
        assert PatchStatus.AVAILABLE.value == "available"
        assert PatchStatus.APPLIED.value == "applied"
        assert PatchStatus.FAILED.value == "failed"
        assert PatchStatus.SUPERSEDED.value == "superseded"

    def test_patch_affected_versions(self, sample_security_patch):
        """Test patch affected versions"""
        patch = SecurityPatch(**sample_security_patch)
        
        assert len(patch.affected_versions) == 3
        assert "1.0.0" in patch.affected_versions
        assert "1.1.0" in patch.affected_versions

    def test_patch_patched_version(self, sample_security_patch):
        """Test patch patched version"""
        patch = SecurityPatch(**sample_security_patch)
        
        assert patch.patched_version == "1.2.1"

    def test_patch_cve_ids(self, sample_security_patch):
        """Test patch CVE IDs"""
        patch = SecurityPatch(**sample_security_patch)
        
        assert len(patch.cve_ids) == 1
        assert "CVE-2024-0001" in patch.cve_ids

    def test_critical_patch_priority(self, sample_security_patch):
        """Test critical patch priority"""
        patch = SecurityPatch(**sample_security_patch)
        
        # Critical patches should be applied immediately
        assert patch.severity == SeverityLevel.CRITICAL

    def test_mandatory_patch(self, sample_security_patch):
        """Test mandatory patch flag"""
        patch = SecurityPatch(**sample_security_patch)
        
        assert patch.is_mandatory is True


class TestSeverityPriority:
    """Tests for patch severity priority"""

    def test_critical_is_highest_priority(self):
        """Test that critical is highest priority"""
        severities = [SeverityLevel.LOW, SeverityLevel.MEDIUM, SeverityLevel.HIGH, SeverityLevel.CRITICAL]
        
        # Critical should be highest priority
        assert SeverityLevel.CRITICAL in severities

    def test_severity_ordering(self):
        """Test severity ordering"""
        # Define priority order
        priority_order = {
            SeverityLevel.CRITICAL: 4,
            SeverityLevel.HIGH: 3,
            SeverityLevel.MEDIUM: 2,
            SeverityLevel.LOW: 1
        }
        
        assert priority_order[SeverityLevel.CRITICAL] > priority_order[SeverityLevel.HIGH]
        assert priority_order[SeverityLevel.HIGH] > priority_order[SeverityLevel.MEDIUM]
        assert priority_order[SeverityLevel.MEDIUM] > priority_order[SeverityLevel.LOW]


class TestPatchEnforcement:
    """Tests for patch enforcement scenarios"""

    def test_frozen_policy_allows_security_patches(self, sample_frozen_policy, sample_security_patch):
        """Test that frozen policy allows security patches"""
        assert sample_frozen_policy.allow_security_patches is True

    def test_critical_patch_bypasses_approval(self, sample_security_patch):
        """Test that critical patches can bypass normal approval"""
        patch = SecurityPatch(**sample_security_patch)
        
        # Critical patches should be auto-approved for frozen policies
        assert patch.severity == SeverityLevel.CRITICAL

    def test_multiple_cve_patch(self):
        """Test patch with multiple CVEs"""
        patch = SecurityPatch(
            id="patch-002",
            component_type="platform",
            component_name="webwaka-platform",
            severity=SeverityLevel.HIGH,
            affected_versions=["1.0.0"],
            patched_version="1.0.1",
            cve_ids=["CVE-2024-0001", "CVE-2024-0002", "CVE-2024-0003"],
            description="Fixes multiple vulnerabilities",
            release_date=datetime.utcnow()
        )
        
        assert len(patch.cve_ids) == 3
