"""Main entry point for running the API server."""

import sys
import uvicorn
from loguru import logger

from .config import settings


def setup_logging():
    """Configure logging."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level
    )


def main():
    """Run the API server."""
    setup_logging()
    logger.info("Starting ProtonX Legal Text Classification API")
    logger.info(f"Model: {settings.model_name}")
    logger.info(f"Host: {settings.api_host}:{settings.api_port}")
    
    uvicorn.run(
        "src.api:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()
