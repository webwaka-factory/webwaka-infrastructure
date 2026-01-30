"""Main entry point for the Enterprise Deployment Automation API."""

import uvicorn
import logging

from src.api.server import create_app


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    app = create_app()
    
    logger.info("Starting Enterprise Deployment Automation API")
    logger.info("API documentation available at http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
