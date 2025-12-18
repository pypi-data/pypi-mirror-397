"""
AWS Lambda handler for the Educational Content Evaluator API.

This module provides a Lambda-compatible handler using Mangum to adapt
the FastAPI application for AWS Lambda + API Gateway.

Usage:
    Deploy this as your Lambda function handler:
    Handler: inceptbench_new.api.lambda_handler.handler
"""

import logging

from mangum import Mangum

from .main import app

# Configure logging for Lambda
logger = logging.getLogger()
if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create Lambda handler using Mangum
# Mangum adapts the ASGI FastAPI app to work with Lambda's event format
handler = Mangum(
    app,
    lifespan="off",  # Lambda manages lifecycle, not the app
    api_gateway_base_path="/",  # Adjust if using custom domain with base path
)


# Optional: Add custom Lambda-specific logic
def lambda_handler(event, context):
    """
    Custom Lambda handler with additional logging and error handling.
    
    Args:
        event: Lambda event object (API Gateway format)
        context: Lambda context object
        
    Returns:
        API Gateway response format
    """
    logger.info(f"Lambda invoked: {event.get('httpMethod')} {event.get('path')}")
    logger.debug(f"Request ID: {context.request_id}")
    
    try:
        # Call Mangum handler
        response = handler(event, context)
        logger.info(f"Response status: {response.get('statusCode')}")
        return response
    except Exception as e:
        logger.error(f"Lambda handler error: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": '{"error": "InternalServerError", "message": "Lambda execution failed"}'
        }

