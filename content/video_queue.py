"""
Video Queue Management - Async queue for video generation requests
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from core.logger import setup_logger

logger = setup_logger(__name__)


class QueuePriority(Enum):
    """Priority levels for video generation"""
    LOW = 3
    NORMAL = 2
    HIGH = 1
    URGENT = 0


@dataclass
class VideoGenerationRequest:
    """Video generation request in queue"""
    request_id: str
    prompt: str
    params: Dict[str, Any]
    priority: QueuePriority = QueuePriority.NORMAL
    created_at: datetime = field(default_factory=datetime.now)
    retry_count: int = 0
    max_retries: int = 3
    callback: Optional[callable] = None
    
    def __lt__(self, other):
        """Compare by priority for queue ordering"""
        return self.priority.value < other.priority.value


class VideoQueue:
    """Async queue for managing video generation requests"""
    
    def __init__(self, config: Dict = None, max_concurrent: int = 3):
        self.config = config or {}
        self.max_concurrent = max_concurrent
        
        # Queue for pending requests
        self.queue = asyncio.PriorityQueue()
        
        # Track active requests
        self.active_requests: Dict[str, VideoGenerationRequest] = {}
        
        # Track completed requests
        self.completed: List[str] = []
        self.failed: List[str] = []
        
        # Statistics
        self.stats = {
            "total_queued": 0,
            "total_completed": 0,
            "total_failed": 0,
            "current_queue_size": 0,
            "active_count": 0
        }
        
        logger.info(f"✅ Video Queue initialized (max concurrent: {max_concurrent})")
    
    async def add_request(
        self,
        request_id: str,
        prompt: str,
        params: Dict[str, Any],
        priority: QueuePriority = QueuePriority.NORMAL,
        callback: Optional[callable] = None
    ) -> bool:
        """
        Add a video generation request to the queue
        
        Args:
            request_id: Unique request identifier
            prompt: Video generation prompt
            params: Generation parameters
            priority: Request priority
            callback: Optional callback function when complete
        
        Returns:
            True if added successfully
        """
        try:
            request = VideoGenerationRequest(
                request_id=request_id,
                prompt=prompt,
                params=params,
                priority=priority,
                callback=callback
            )
            
            await self.queue.put((priority.value, request))
            
            self.stats["total_queued"] += 1
            self.stats["current_queue_size"] = self.queue.qsize()
            
            logger.info(
                f"✅ Added video request to queue: {request_id} "
                f"(priority: {priority.name}, queue size: {self.queue.qsize()})"
            )
            
            return True
        
        except Exception as e:
            logger.exception(f"❌ Failed to add request to queue: {e}")
            return False
    
    async def get_next_request(self) -> Optional[VideoGenerationRequest]:
        """
        Get the next request from queue
        
        Returns:
            Next VideoGenerationRequest or None if queue is empty
        """
        try:
            if self.queue.empty():
                return None
            
            # Check if we've hit concurrency limit
            if len(self.active_requests) >= self.max_concurrent:
                logger.debug(f"⏸️ Max concurrent limit reached ({self.max_concurrent})")
                return None
            
            # Get next request
            priority, request = await self.queue.get()
            
            # Mark as active
            self.active_requests[request.request_id] = request
            
            self.stats["current_queue_size"] = self.queue.qsize()
            self.stats["active_count"] = len(self.active_requests)
            
            logger.info(f"📤 Retrieved request from queue: {request.request_id}")
            
            return request
        
        except Exception as e:
            logger.exception(f"❌ Failed to get next request: {e}")
            return None
    
    async def mark_completed(
        self,
        request_id: str,
        result: Any = None
    ):
        """
        Mark a request as completed
        
        Args:
            request_id: Request identifier
            result: Optional result data
        """
        if request_id in self.active_requests:
            request = self.active_requests.pop(request_id)
            self.completed.append(request_id)
            
            self.stats["total_completed"] += 1
            self.stats["active_count"] = len(self.active_requests)
            
            # Call callback if provided
            if request.callback:
                try:
                    await request.callback(request_id, result, None)
                except Exception as e:
                    logger.exception(f"❌ Error in callback for {request_id}: {e}")
            
            logger.info(f"✅ Request completed: {request_id}")
    
    async def mark_failed(
        self,
        request_id: str,
        error: Optional[str] = None,
        retry: bool = True
    ):
        """
        Mark a request as failed
        
        Args:
            request_id: Request identifier
            error: Optional error message
            retry: Whether to retry the request
        """
        if request_id not in self.active_requests:
            logger.warning(f"⚠️ Request not found in active requests: {request_id}")
            return
        
        request = self.active_requests[request_id]
        
        # Check if we should retry
        if retry and request.retry_count < request.max_retries:
            request.retry_count += 1
            
            logger.warning(
                f"⚠️ Request failed, retrying ({request.retry_count}/{request.max_retries}): {request_id}"
            )
            
            # Re-queue with exponential backoff
            await asyncio.sleep(2 ** request.retry_count)
            await self.queue.put((request.priority.value, request))
            
            self.active_requests.pop(request_id)
            self.stats["active_count"] = len(self.active_requests)
        else:
            # Max retries reached or no retry
            self.active_requests.pop(request_id)
            self.failed.append(request_id)
            
            self.stats["total_failed"] += 1
            self.stats["active_count"] = len(self.active_requests)
            
            # Call callback if provided
            if request.callback:
                try:
                    await request.callback(request_id, None, error)
                except Exception as e:
                    logger.exception(f"❌ Error in callback for {request_id}: {e}")
            
            logger.error(f"❌ Request failed permanently: {request_id} - {error}")
    
    def get_queue_size(self) -> int:
        """Get current queue size"""
        return self.queue.qsize()
    
    def get_active_count(self) -> int:
        """Get number of active requests"""
        return len(self.active_requests)
    
    def get_stats(self) -> Dict:
        """Get queue statistics"""
        return {
            **self.stats,
            "success_rate": (
                self.stats["total_completed"] / 
                (self.stats["total_completed"] + self.stats["total_failed"])
                if (self.stats["total_completed"] + self.stats["total_failed"]) > 0
                else 0.0
            )
        }
    
    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return self.queue.empty() and len(self.active_requests) == 0
    
    async def clear(self):
        """Clear all pending requests"""
        while not self.queue.empty():
            try:
                await self.queue.get()
            except:
                break
        
        self.active_requests.clear()
        self.stats["current_queue_size"] = 0
        self.stats["active_count"] = 0
        
        logger.info("✅ Queue cleared")
