"""
Curriculum standards search functionality.

This module provides tools for searching curriculum standards via the InceptAPI.
"""

import logging
import time

import httpx

from inceptbench_new.config import settings

logger = logging.getLogger(__name__)


async def get_curriculum_context(content: str, curriculum: str = "common_core") -> str:
    """
    Get curriculum context by calling the InceptAPI curriculum search endpoint.
    
    The API handles all complexity including:
    - Content preparation and cleaning
    - Extracting explicit curriculum standards from content
    - Vector store search across curriculum databases
    - Deduplication of results
    
    Args:
        content: The educational content to analyze
        curriculum: Curriculum name (default: "common_core")
        
    Returns:
        Formatted curriculum context string, or empty string if none found
    """
    start_time = time.time()
    
    try:
        logger.info(f"Searching {curriculum} curriculum standards for content of length {len(content)}")
        
        # Call the InceptAPI curriculum search endpoint
        async with httpx.AsyncClient(timeout=settings.CURRICULUM_SEARCH_TIMEOUT) as client:
            headers = {}
            if settings.INCEPT_API_KEY:
                headers["Authorization"] = f"Bearer {settings.INCEPT_API_KEY}"
            
            response = await client.post(
                f"{settings.INCEPTAPI_BASE_URL}/curriculum-search",
                json={
                    "prompt": content,
                    "curriculum_name": curriculum
                },
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", "")
            
            if results:
                logger.info(f"Curriculum standards search completed in {time.time() - start_time:.2f}s")
                return f"\n\nRelevant Curriculum Context:\n{results}"
            else:
                logger.warning(f"No curriculum standards found after {time.time() - start_time:.2f}s")
                return ""
                
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error from curriculum API after {time.time() - start_time:.2f}s: "
                    f"{e.response.status_code} - {e.response.text}")
        return ""
    except Exception as e:
        logger.warning(f"Could not retrieve curriculum context after {time.time() - start_time:.2f}s: {e}")
        return ""

