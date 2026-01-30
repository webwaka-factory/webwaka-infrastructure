"""Deployment API routes."""

import logging
from fastapi import APIRouter, HTTPException, status

from ...models.deployment import (
    Deployment,
    DeploymentRequest,
    DeploymentResponse,
    DeploymentManifest
)
from ...core.deployment_engine import DeploymentEngine


logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory storage for demo purposes
deployment_engine = DeploymentEngine()


@router.post("/deployments", response_model=DeploymentResponse, status_code=status.HTTP_201_CREATED)
async def create_deployment(request: DeploymentRequest):
    """Create a new deployment.
    
    Args:
        request: Deployment request
        
    Returns:
        Created deployment response
    """
    try:
        # Create a sample manifest for demo
        manifest = DeploymentManifest(
            id=request.manifest_id,
            version="1.0.0",
            platform_version="2.0.0",
            suites={"commerce": "1.5.0"},
            capabilities={"reporting": "1.0.0"}
        )
        
        deployment = await deployment_engine.create_deployment(
            manifest=manifest,
            instance_id=request.instance_id,
            dry_run=request.dry_run
        )
        
        return DeploymentResponse(
            id=deployment.id,
            status=deployment.status,
            manifest_id=deployment.manifest_id,
            instance_id=deployment.instance_id,
            created_at=deployment.created_at,
            started_at=deployment.started_at,
            completed_at=deployment.completed_at,
            error_message=deployment.error_message
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating deployment: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/deployments/{deployment_id}", response_model=DeploymentResponse)
async def get_deployment(deployment_id: str):
    """Get deployment by ID.
    
    Args:
        deployment_id: Deployment ID
        
    Returns:
        Deployment response
    """
    deployment = deployment_engine.get_deployment(deployment_id)
    
    if not deployment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deployment not found")
    
    return DeploymentResponse(
        id=deployment.id,
        status=deployment.status,
        manifest_id=deployment.manifest_id,
        instance_id=deployment.instance_id,
        created_at=deployment.created_at,
        started_at=deployment.started_at,
        completed_at=deployment.completed_at,
        error_message=deployment.error_message
    )


@router.get("/deployments", response_model=list[DeploymentResponse])
async def list_deployments(instance_id: str = None):
    """List deployments.
    
    Args:
        instance_id: Optional instance ID to filter by
        
    Returns:
        List of deployment responses
    """
    deployments = deployment_engine.list_deployments(instance_id)
    
    return [
        DeploymentResponse(
            id=d.id,
            status=d.status,
            manifest_id=d.manifest_id,
            instance_id=d.instance_id,
            created_at=d.created_at,
            started_at=d.started_at,
            completed_at=d.completed_at,
            error_message=d.error_message
        )
        for d in deployments
    ]
