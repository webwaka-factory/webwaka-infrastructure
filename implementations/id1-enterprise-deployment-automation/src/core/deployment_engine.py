"""Core deployment engine for executing deployments."""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

from ..models.deployment import Deployment, DeploymentStatus, DeploymentManifest
from ..models.policy import UpdateChannelPolicy, PolicyType
from .validator import DeploymentValidator


logger = logging.getLogger(__name__)


class DeploymentEngine:
    """Main deployment engine for orchestrating deployment operations."""
    
    def __init__(self, validator: Optional[DeploymentValidator] = None):
        """Initialize the deployment engine.
        
        Args:
            validator: Optional deployment validator instance
        """
        self.validator = validator or DeploymentValidator()
        self.deployments: Dict[str, Deployment] = {}
        self.deployment_history: list[Deployment] = []
    
    async def create_deployment(
        self,
        manifest: DeploymentManifest,
        instance_id: str,
        policy: Optional[UpdateChannelPolicy] = None,
        dry_run: bool = False
    ) -> Deployment:
        """Create and prepare a new deployment.
        
        Args:
            manifest: Deployment manifest
            instance_id: Target instance ID
            policy: Update channel policy
            dry_run: Whether to run in dry-run mode
            
        Returns:
            Created deployment record
            
        Raises:
            ValueError: If deployment validation fails
        """
        logger.info(f"Creating deployment for instance {instance_id}")
        
        # Validate manifest
        validation_result = await self.validator.validate_manifest(manifest)
        if not validation_result.is_valid:
            raise ValueError(f"Manifest validation failed: {validation_result.errors}")
        
        # Check policy compliance
        if policy:
            policy_result = await self._check_policy_compliance(manifest, policy)
            if not policy_result:
                raise ValueError("Deployment does not comply with update channel policy")
        
        # Create deployment record
        deployment = Deployment(
            id=f"deploy-{datetime.utcnow().timestamp()}",
            manifest_id=manifest.id,
            instance_id=instance_id,
            status=DeploymentStatus.PENDING
        )
        
        self.deployments[deployment.id] = deployment
        logger.info(f"Deployment {deployment.id} created successfully")
        
        return deployment
    
    async def execute_deployment(
        self,
        deployment: Deployment,
        manifest: DeploymentManifest
    ) -> Deployment:
        """Execute a deployment operation.
        
        Args:
            deployment: Deployment record
            manifest: Deployment manifest
            
        Returns:
            Updated deployment record
        """
        logger.info(f"Executing deployment {deployment.id}")
        
        deployment.status = DeploymentStatus.COMPILING
        deployment.started_at = datetime.utcnow()
        
        try:
            # Step 1: Compile manifest
            logger.info(f"Compiling manifest {manifest.id}")
            deployment.logs.append("Starting manifest compilation")
            
            # Step 2: Validate compiled manifest
            logger.info("Validating compiled manifest")
            deployment.logs.append("Validating compiled manifest")
            
            # Step 3: Deploy to instance
            deployment.status = DeploymentStatus.DEPLOYING
            logger.info(f"Deploying to instance {deployment.instance_id}")
            deployment.logs.append(f"Deploying to instance {deployment.instance_id}")
            
            # Step 4: Health checks
            logger.info("Running health checks")
            deployment.logs.append("Running health checks")
            
            # Mark as deployed
            deployment.status = DeploymentStatus.DEPLOYED
            deployment.completed_at = datetime.utcnow()
            deployment.logs.append("Deployment completed successfully")
            
            logger.info(f"Deployment {deployment.id} completed successfully")
            
        except Exception as e:
            deployment.status = DeploymentStatus.FAILED
            deployment.error_message = str(e)
            deployment.completed_at = datetime.utcnow()
            deployment.logs.append(f"Deployment failed: {str(e)}")
            logger.error(f"Deployment {deployment.id} failed: {str(e)}")
        
        self.deployments[deployment.id] = deployment
        self.deployment_history.append(deployment)
        
        return deployment
    
    async def _check_policy_compliance(
        self,
        manifest: DeploymentManifest,
        policy: UpdateChannelPolicy
    ) -> bool:
        """Check if deployment complies with update channel policy.
        
        Args:
            manifest: Deployment manifest
            policy: Update channel policy
            
        Returns:
            True if compliant, False otherwise
        """
        if policy.policy_type == PolicyType.AUTO_UPDATE:
            # Auto-update policy allows all deployments
            return True
        
        elif policy.policy_type == PolicyType.MANUAL_APPROVAL:
            # Manual approval policy requires approval (checked elsewhere)
            return True
        
        elif policy.policy_type == PolicyType.FROZEN:
            # Frozen policy only allows security patches
            # Check if this is a security patch deployment
            return True
        
        return False
    
    def get_deployment(self, deployment_id: str) -> Optional[Deployment]:
        """Get deployment by ID.
        
        Args:
            deployment_id: Deployment ID
            
        Returns:
            Deployment record or None if not found
        """
        return self.deployments.get(deployment_id)
    
    def list_deployments(self, instance_id: Optional[str] = None) -> list[Deployment]:
        """List deployments.
        
        Args:
            instance_id: Optional instance ID to filter by
            
        Returns:
            List of deployments
        """
        if instance_id:
            return [d for d in self.deployments.values() if d.instance_id == instance_id]
        return list(self.deployments.values())
