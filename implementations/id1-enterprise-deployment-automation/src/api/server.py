"""FastAPI server setup for Enterprise Deployment Automation."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import (
    deployments,
    policies,
    versions,
    security,
    rollback
)


logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="Enterprise Deployment Automation API",
        description="API for managing enterprise deployments with policy enforcement, version pinning, and security patches",
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
    
    # Include routers
    app.include_router(deployments.router, prefix="/api/v1", tags=["Deployments"])
    app.include_router(policies.router, prefix="/api/v1", tags=["Policies"])
    app.include_router(versions.router, prefix="/api/v1", tags=["Versions"])
    app.include_router(security.router, prefix="/api/v1", tags=["Security"])
    app.include_router(rollback.router, prefix="/api/v1", tags=["Rollback"])
    
    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}
    
    # Root endpoint
    @app.get("/", tags=["Info"])
    async def root():
        """Root endpoint with API information."""
        return {
            "name": "Enterprise Deployment Automation API",
            "version": "1.0.0",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    
    logger.info("FastAPI application created successfully")
    return app
