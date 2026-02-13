"""
Base provider abstraction for video generation APIs
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional, Any
from enum import Enum


class VideoStatus(Enum):
    """Video generation status"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class VideoResult:
    """Result from video generation"""
    job_id: str
    status: VideoStatus
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = None
    cost_usd: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseVideoProvider(ABC):
    """Abstract base class for video generation providers"""
    
    def __init__(self, api_key: str, config: Dict[str, Any] = None):
        """
        Initialize provider
        
        Args:
            api_key: API key for the provider
            config: Provider-specific configuration
        """
        self.api_key = api_key
        self.config = config or {}
        self.provider_name = self.__class__.__name__.replace("Provider", "").lower()
    
    @abstractmethod
    async def generate_video(
        self, 
        prompt: str, 
        style: str = "default",
        duration: int = 15,
        **kwargs
    ) -> VideoResult:
        """
        Generate video from text prompt
        
        Args:
            prompt: Text description of the video
            style: Visual style (e.g., "cinematic", "trendy", "professional")
            duration: Video duration in seconds
            **kwargs: Additional provider-specific parameters
        
        Returns:
            VideoResult with job information
        """
        pass
    
    @abstractmethod
    async def generate_from_image(
        self,
        image_url: str,
        animation_prompt: str,
        duration: int = 15,
        **kwargs
    ) -> VideoResult:
        """
        Generate video by animating an image
        
        Args:
            image_url: URL of the source image
            animation_prompt: Description of how to animate
            duration: Video duration in seconds
            **kwargs: Additional provider-specific parameters
        
        Returns:
            VideoResult with job information
        """
        pass
    
    @abstractmethod
    async def get_status(self, job_id: str) -> VideoResult:
        """
        Get the status of a video generation job
        
        Args:
            job_id: Job identifier from generate_video or generate_from_image
        
        Returns:
            VideoResult with current status
        """
        pass
    
    @abstractmethod
    async def estimate_cost(self, params: Dict[str, Any]) -> float:
        """
        Estimate the cost of video generation
        
        Args:
            params: Generation parameters (prompt, duration, style, etc.)
        
        Returns:
            Estimated cost in USD
        """
        pass
    
    async def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a video generation job (optional)
        
        Args:
            job_id: Job identifier
        
        Returns:
            True if cancelled successfully
        """
        # Default implementation - override if provider supports cancellation
        return False
    
    def get_rate_limit(self) -> Dict[str, int]:
        """
        Get rate limit information for this provider
        
        Returns:
            Dict with 'per_minute' and 'per_day' limits
        """
        return self.config.get("rate_limit", {
            "per_minute": 5,
            "per_day": 100
        })
    
    def get_max_duration(self) -> int:
        """
        Get maximum video duration supported by this provider
        
        Returns:
            Maximum duration in seconds
        """
        return self.config.get("max_duration", 60)
    
    def supports_image_to_video(self) -> bool:
        """
        Check if provider supports image-to-video generation
        
        Returns:
            True if supported
        """
        return True
    
    def get_supported_styles(self) -> list:
        """
        Get list of supported video styles
        
        Returns:
            List of style names
        """
        return self.config.get("supported_styles", [
            "default", "cinematic", "trendy", "professional", "casual"
        ])
