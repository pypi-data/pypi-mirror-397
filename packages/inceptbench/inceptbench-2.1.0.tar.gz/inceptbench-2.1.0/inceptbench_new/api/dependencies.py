"""
API dependency injection.

This module provides dependency injection functions for FastAPI endpoints,
including service instance management and request validation.
"""

import logging
import os
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..service import EvaluationService
from ..config.settings import settings

logger = logging.getLogger(__name__)

# Global service instance (initialized once, reused across requests)
_service_instance: EvaluationService | None = None

# Security scheme for Bearer token
security = HTTPBearer()


def get_evaluation_service() -> EvaluationService:
    """
    Get or create the evaluation service instance.
    
    This dependency provides a singleton service instance that's reused
    across all requests, avoiding the overhead of recreating clients.
    
    Returns:
        EvaluationService instance
        
    Raises:
        HTTPException: If service initialization fails
    """
    global _service_instance
    
    if _service_instance is None:
        try:
            logger.info("Initializing EvaluationService...")
            _service_instance = EvaluationService()
            logger.info("EvaluationService initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize EvaluationService: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service initialization failed: {str(e)}"
            )
    
    return _service_instance


def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Verify API key from Authorization header.
    
    Expects: Authorization: Bearer <api_key>
    
    The API key is validated against the INCEPTBENCH_API_KEY environment variable.
    Supports multiple keys as comma-separated values.
    
    Format:
        INCEPTBENCH_API_KEY=key1,key2,key3
    
    Args:
        credentials: HTTPAuthorizationCredentials from Bearer token
        
    Returns:
        The validated API key
        
    Raises:
        HTTPException: If API key is invalid or missing
    """
    provided_key = credentials.credentials
    
    # Load API keys from environment
    api_key_env = os.getenv("INCEPTBENCH_API_KEY")
    
    # If no keys are configured, deny access
    if not api_key_env:
        logger.error("INCEPTBENCH_API_KEY environment variable is not configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API authentication is not configured. Please contact the administrator."
        )
    
    # Parse comma-separated keys and strip whitespace
    valid_keys = [key.strip() for key in api_key_env.split(",") if key.strip()]
    
    if not valid_keys:
        logger.error("INCEPTBENCH_API_KEY environment variable is empty")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API authentication is not configured. Please contact the administrator."
        )
    
    # Validate provided key against all valid keys
    if provided_key not in valid_keys:
        logger.warning(f"Invalid API key attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return provided_key


# Type aliases for dependency injection
EvaluationServiceDep = Annotated[EvaluationService, Depends(get_evaluation_service)]
APIKeyDep = Annotated[str, Depends(verify_api_key)]

