from functools import wraps
from typing import Dict, Any, Optional, Callable
import logging
from flask import jsonify, Response
import traceback
from http import HTTPStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base exception for API errors"""
    def __init__(
        self,
        message: str,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        error_code: str = "UNKNOWN_ERROR",
        is_retryable: bool = True,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.is_retryable = is_retryable
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(APIError):
    """Validation error"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
            error_code="VALIDATION_ERROR",
            is_retryable=False,
            details=details
        )

class AuthenticationError(APIError):
    """Authentication error"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=HTTPStatus.UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR",
            is_retryable=True
        )

class RateLimitError(APIError):
    """Rate limit exceeded error"""
    def __init__(self, message: str, retry_after: int):
        super().__init__(
            message=message,
            status_code=HTTPStatus.TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_ERROR",
            is_retryable=True,
            details={"retry_after": retry_after}
        )

def handle_api_error(error: APIError) -> Response:
    """Convert API error to JSON response"""
    response = {
        "success": False,
        "error": {
            "code": error.error_code,
            "message": error.message,
            "retryable": error.is_retryable
        }
    }
    
    if error.details:
        response["error"]["details"] = error.details
        
    logger.error(f"API Error: {error.message} ({error.error_code})")
    return jsonify(response), error.status_code

def error_handler(func: Callable) -> Callable:
    """Decorator to handle API errors"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except APIError as e:
            return handle_api_error(e)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
            return handle_api_error(APIError(
                message="An unexpected error occurred",
                error_code="INTERNAL_SERVER_ERROR",
                is_retryable=True,
                details={"error": str(e)} if not isinstance(e, APIError) else None
            ))
    return wrapper

def validate_request(schema: Dict[str, Any]) -> Callable:
    """Decorator to validate request data"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Import here to avoid circular imports
                from jsonschema import validate, ValidationError as SchemaError
                
                request_data = request.get_json()
                validate(instance=request_data, schema=schema)
                return func(*args, **kwargs)
            except SchemaError as e:
                raise ValidationError(
                    message="Invalid request data",
                    details={"validation_error": str(e)}
                )
            except Exception as e:
                logger.error(f"Validation error: {str(e)}\n{traceback.format_exc()}")
                raise ValidationError(
                    message="Failed to validate request",
                    details={"error": str(e)}
                )
        return wrapper
    return decorator

def rate_limit(
    max_requests: int,
    time_window: int,
    key_func: Optional[Callable] = None
) -> Callable:
    """Rate limiting decorator"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Import here to avoid circular imports
            from flask import request
            from redis import Redis
            from datetime import datetime
            
            redis_client = Redis(host='localhost', port=6379, db=0)
            
            # Get key for rate limiting
            if key_func:
                rate_key = f"rate_limit:{key_func()}"
            else:
                rate_key = f"rate_limit:{request.remote_addr}"
            
            # Check rate limit
            current = int(redis_client.get(rate_key) or 0)
            if current >= max_requests:
                retry_after = redis_client.ttl(rate_key)
                raise RateLimitError(
                    message="Rate limit exceeded",
                    retry_after=retry_after
                )
            
            # Update rate limit
            pipe = redis_client.pipeline()
            pipe.incr(rate_key)
            pipe.expire(rate_key, time_window)
            pipe.execute()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
