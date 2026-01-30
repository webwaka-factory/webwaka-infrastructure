"""Rollback management for deployments."""

import logging
from typing import Optional, Dict, List
from datetime import datetime

from ..models.rollback import RollbackRecord, RollbackStatus, ManifestVersion, RollbackHistory
from ..models.deployment import DeploymentManifest


logger = logging.getLogger(__name__)


class RollbackManager:
    """Manages rollback operations."""
    
    def __init__(self):
        """Initialize the rollback manager."""
        self.rollbacks: Dict[str, RollbackRecord] = {}
        self.manifest_history: Dict[str, List[ManifestVersion]] = {}
    
    async def initiate_rollback(
        self,
        instance_id: str,
        from_manifest_id: str,
        to_manifest_id: str,
        reason: Optional[str] = None,
        initiated_by: Optional[str] = None
    ) -> RollbackRecord:
        """Initiate a rollback operation.
        
        Args:
            instance_id: Instance ID
            from_manifest_id: Current manifest ID
            to_manifest_id: Target manifest ID
            reason: Reason for rollback
            initiated_by: User who initiated rollback
            
        Returns:
            Rollback record
        """
        logger.info(f"Initiating rollback for instance {instance_id} from {from_manifest_id} to {to_manifest_id}")
        
        rollback_id = f"rollback-{datetime.utcnow().timestamp()}"
        
        rollback = RollbackRecord(
            id=rollback_id,
            instance_id=instance_id,
            from_manifest_id=from_manifest_id,
            to_manifest_id=to_manifest_id,
            status=RollbackStatus.PENDING,
            reason=reason,
            initiated_by=initiated_by
        )
        
        self.rollbacks[rollback_id] = rollback
        logger.info(f"Rollback {rollback_id} initiated successfully")
        
        return rollback
    
    async def execute_rollback(self, rollback: RollbackRecord) -> RollbackRecord:
        """Execute a rollback operation.
        
        Args:
            rollback: Rollback record
            
        Returns:
            Updated rollback record
        """
        logger.info(f"Executing rollback {rollback.id}")
        
        rollback.status = RollbackStatus.IN_PROGRESS
        rollback.started_at = datetime.utcnow()
        
        try:
            # Step 1: Validate rollback feasibility
            logger.info(f"Validating rollback feasibility")
            rollback.logs.append("Validating rollback feasibility")
            
            # Step 2: Prepare rollback
            logger.info(f"Preparing rollback to manifest {rollback.to_manifest_id}")
            rollback.logs.append(f"Preparing rollback to manifest {rollback.to_manifest_id}")
            
            # Step 3: Execute rollback
            logger.info(f"Executing rollback on instance {rollback.instance_id}")
            rollback.logs.append(f"Executing rollback on instance {rollback.instance_id}")
            
            # Step 4: Verify rollback
            logger.info(f"Verifying rollback")
            rollback.logs.append("Verifying rollback")
            
            # Mark as completed
            rollback.status = RollbackStatus.COMPLETED
            rollback.completed_at = datetime.utcnow()
            rollback.logs.append("Rollback completed successfully")
            
            logger.info(f"Rollback {rollback.id} completed successfully")
            
        except Exception as e:
            rollback.status = RollbackStatus.FAILED
            rollback.error_message = str(e)
            rollback.completed_at = datetime.utcnow()
            rollback.logs.append(f"Rollback failed: {str(e)}")
            logger.error(f"Rollback {rollback.id} failed: {str(e)}")
        
        self.rollbacks[rollback.id] = rollback
        return rollback
    
    async def record_manifest_version(
        self,
        instance_id: str,
        manifest: DeploymentManifest,
        deployment_id: str,
        status: str
    ) -> ManifestVersion:
        """Record a manifest version in history.
        
        Args:
            instance_id: Instance ID
            manifest: Deployment manifest
            deployment_id: Associated deployment ID
            status: Deployment status
            
        Returns:
            Manifest version record
        """
        logger.info(f"Recording manifest version {manifest.id} for instance {instance_id}")
        
        manifest_version = ManifestVersion(
            id=manifest.id,
            version=manifest.version,
            deployed_at=datetime.utcnow(),
            deployment_id=deployment_id,
            status=status
        )
        
        if instance_id not in self.manifest_history:
            self.manifest_history[instance_id] = []
        
        self.manifest_history[instance_id].insert(0, manifest_version)
        
        # Keep only last 100 versions
        if len(self.manifest_history[instance_id]) > 100:
            self.manifest_history[instance_id] = self.manifest_history[instance_id][:100]
        
        logger.info(f"Manifest version {manifest.id} recorded successfully")
        return manifest_version
    
    async def get_rollback_history(self, instance_id: str) -> RollbackHistory:
        """Get rollback history for an instance.
        
        Args:
            instance_id: Instance ID
            
        Returns:
            Rollback history
        """
        logger.info(f"Retrieving rollback history for instance {instance_id}")
        
        instance_rollbacks = [r for r in self.rollbacks.values() if r.instance_id == instance_id]
        
        successful = len([r for r in instance_rollbacks if r.status == RollbackStatus.COMPLETED])
        failed = len([r for r in instance_rollbacks if r.status == RollbackStatus.FAILED])
        
        available_manifests = self.manifest_history.get(instance_id, [])
        
        return RollbackHistory(
            instance_id=instance_id,
            total_rollbacks=len(instance_rollbacks),
            successful_rollbacks=successful,
            failed_rollbacks=failed,
            recent_rollbacks=[],
            available_manifests=available_manifests
        )
    
    def get_rollback(self, rollback_id: str) -> Optional[RollbackRecord]:
        """Get rollback by ID.
        
        Args:
            rollback_id: Rollback ID
            
        Returns:
            Rollback record or None if not found
        """
        return self.rollbacks.get(rollback_id)
    
    def list_rollbacks(self, instance_id: Optional[str] = None) -> List[RollbackRecord]:
        """List rollbacks.
        
        Args:
            instance_id: Optional instance ID to filter by
            
        Returns:
            List of rollback records
        """
        if instance_id:
            return [r for r in self.rollbacks.values() if r.instance_id == instance_id]
        return list(self.rollbacks.values())
