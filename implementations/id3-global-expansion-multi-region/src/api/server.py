"""FastAPI server setup for Global Expansion & Multi-Region API."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..core.multi_region_engine import MultiRegionEngine
from ..core.region_orchestrator import RegionOrchestrator
from ..residency.residency_manager import ResidencyManager
from ..residency.residency_enforcer import ResidencyEnforcer
from ..classification.classification_manager import ClassificationManager
from ..classification.classification_enforcer import ClassificationEnforcer
from ..access_control.access_manager import AccessManager
from ..access_control.access_enforcer import AccessEnforcer
from ..access_control.audit_logger import AuditLogger


logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="Global Expansion & Multi-Region API",
        description="API for managing multi-region deployments with data residency and access controls",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize managers
    multi_region_engine = MultiRegionEngine()
    region_orchestrator = RegionOrchestrator()
    residency_manager = ResidencyManager()
    residency_enforcer = ResidencyEnforcer(residency_manager)
    classification_manager = ClassificationManager()
    classification_enforcer = ClassificationEnforcer(classification_manager)
    access_manager = AccessManager()
    access_enforcer = AccessEnforcer(access_manager)
    audit_logger = AuditLogger()
    
    # Store managers in app state
    app.state.multi_region_engine = multi_region_engine
    app.state.region_orchestrator = region_orchestrator
    app.state.residency_manager = residency_manager
    app.state.residency_enforcer = residency_enforcer
    app.state.classification_manager = classification_manager
    app.state.classification_enforcer = classification_enforcer
    app.state.access_manager = access_manager
    app.state.access_enforcer = access_enforcer
    app.state.audit_logger = audit_logger
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "Global Expansion & Multi-Region API",
            "version": "1.0.0"
        }
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "Global Expansion & Multi-Region API",
            "version": "1.0.0",
            "docs": "/docs"
        }
    
    logger.info("FastAPI application created successfully")
    return app


if __name__ == "__main__":
    import uvicorn
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    app = create_app()
    
    logger.info("Starting Global Expansion & Multi-Region API")
    logger.info("API documentation available at http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
