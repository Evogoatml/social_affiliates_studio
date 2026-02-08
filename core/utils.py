"""
Utility functions for error handling, retries, and common operations
"""

import time
import asyncio
from typing import Callable, Any, Optional, TypeVar
from functools import wraps

from core.logger import setup_logger

logger = setup_logger(__name__)

T = TypeVar('T')

def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retrying functions with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        backoff_factor: Multiplier for delay on each retry
        exceptions: Tuple of exception types to catch
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                        
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(
                            f"❌ {func.__name__} failed after {max_retries} retries: {e}"
                        )
                        raise
                    
                    logger.warning(
                        f"⚠️  {func.__name__} attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    
                    if asyncio.iscoroutinefunction(func):
                        await asyncio.sleep(delay)
                    else:
                        time.sleep(delay)
                    
                    delay *= backoff_factor
            
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator

def safe_execute(
    func: Callable,
    default_return: Any = None,
    error_message: str = "Operation failed"
) -> Callable:
    """
    Decorator to safely execute functions and return default on error
    
    Args:
        func: Function to wrap
        default_return: Value to return on error
        error_message: Custom error message
    """
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"❌ {error_message}: {e}")
            return default_return
    
    return wrapper

async def rate_limit(calls_per_minute: int = 60):
    """
    Simple rate limiter
    
    Args:
        calls_per_minute: Maximum calls allowed per minute
    """
    delay = 60.0 / calls_per_minute
    await asyncio.sleep(delay)

class RateLimiter:
    """Rate limiter for API calls"""
    
    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.delay = 60.0 / calls_per_minute
        self.last_call = 0
    
    async def wait(self):
        """Wait if necessary to respect rate limit"""
        now = time.time()
        time_since_last = now - self.last_call
        
        if time_since_last < self.delay:
            wait_time = self.delay - time_since_last
            logger.debug(f"⏱️  Rate limiting: waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
        
        self.last_call = time.time()

class CircuitBreaker:
    """Circuit breaker pattern for failing services"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        recovery_timeout: float = 300.0
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.recovery_timeout = recovery_timeout
        
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "closed"  # closed, open, half-open
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker"""
        
        # Check if circuit should close
        if self.state == "open":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                logger.info("🔄 Circuit breaker entering half-open state")
                self.state = "half-open"
            else:
                logger.warning("⚠️  Circuit breaker is OPEN - rejecting call")
                raise Exception("Circuit breaker is OPEN")
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Success - reset if in half-open
            if self.state == "half-open":
                logger.info("✅ Circuit breaker closing - service recovered")
                self.state = "closed"
                self.failure_count = 0
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                logger.error(
                    f"🔴 Circuit breaker OPENING after {self.failure_count} failures"
                )
                self.state = "open"
            
            raise

def validate_content(content: dict) -> tuple[bool, Optional[str]]:
    """
    Validate content before posting
    
    Returns:
        (is_valid, error_message)
    """
    required_fields = ['id', 'type', 'caption']
    
    for field in required_fields:
        if field not in content or not content[field]:
            return False, f"Missing required field: {field}"
    
    # Check caption length
    caption = content.get('caption', '')
    if len(caption) < 10:
        return False, "Caption too short (minimum 10 characters)"
    
    if len(caption) > 2200:
        return False, "Caption too long (maximum 2200 characters)"
    
    # Validate content type
    valid_types = ['image', 'video', 'carousel']
    if content['type'] not in valid_types:
        return False, f"Invalid content type: {content['type']}"
    
    return True, None

def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize text for safe posting
    
    Args:
        text: Text to sanitize
        max_length: Optional maximum length
    
    Returns:
        Sanitized text
    """
    # Remove null characters
    text = text.replace('\x00', '')
    
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Truncate if necessary
    if max_length and len(text) > max_length:
        text = text[:max_length-3] + '...'
    
    return text.strip()

def format_hashtags(hashtags: list, max_count: int = 30) -> str:
    """
    Format hashtags for social media
    
    Args:
        hashtags: List of hashtag strings (without #)
        max_count: Maximum number of hashtags
    
    Returns:
        Formatted hashtag string
    """
    # Remove duplicates and invalid hashtags
    valid_hashtags = []
    seen = set()
    
    for tag in hashtags[:max_count]:
        # Remove # if present
        tag = tag.strip().lstrip('#')
        
        # Validate hashtag (alphanumeric and underscores only)
        if tag and tag.replace('_', '').isalnum() and tag.lower() not in seen:
            valid_hashtags.append(tag)
            seen.add(tag.lower())
    
    return ' '.join([f'#{tag}' for tag in valid_hashtags])

def calculate_engagement_rate(
    likes: int,
    comments: int,
    shares: int,
    followers: int
) -> float:
    """
    Calculate engagement rate
    
    Args:
        likes: Number of likes
        comments: Number of comments
        shares: Number of shares
        followers: Number of followers
    
    Returns:
        Engagement rate as percentage
    """
    if followers == 0:
        return 0.0
    
    # Weight different engagement types
    total_engagement = likes + (comments * 2) + (shares * 3)
    rate = (total_engagement / followers) * 100
    
    return round(rate, 2)

class ProgressTracker:
    """Track progress of long-running operations"""
    
    def __init__(self, total: int, description: str = "Progress"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
    
    def update(self, increment: int = 1):
        """Update progress"""
        self.current += increment
        percentage = (self.current / self.total) * 100 if self.total > 0 else 0
        elapsed = time.time() - self.start_time
        
        if self.current > 0:
            eta = (elapsed / self.current) * (self.total - self.current)
            logger.info(
                f"📊 {self.description}: {self.current}/{self.total} "
                f"({percentage:.1f}%) - ETA: {eta:.0f}s"
            )
    
    def complete(self):
        """Mark as complete"""
        elapsed = time.time() - self.start_time
        logger.info(
            f"✅ {self.description} complete: {self.total} items in {elapsed:.1f}s"
        )
