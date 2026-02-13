"""
Kling AI Video Provider - Free tier option
https://klingai.com/api
"""

import asyncio
import aiohttp
from typing import Dict, Any
from .base_provider import BaseVideoProvider, VideoResult, VideoStatus
from core.logger import setup_logger

logger = setup_logger(__name__)


class KlingProvider(BaseVideoProvider):
    """Kling AI video generation provider (free tier available)"""
    
    API_BASE_URL = "https://api.klingai.com/v1"
    
    def __init__(self, api_key: str, config: Dict[str, Any] = None):
        super().__init__(api_key, config)
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
        return self.session
    
    async def generate_video(
        self, 
        prompt: str, 
        style: str = "default",
        duration: int = 15,
        **kwargs
    ) -> VideoResult:
        """Generate video from text prompt"""
        try:
            session = await self._get_session()
            
            # Build request payload
            payload = {
                "prompt": prompt,
                "duration": duration,
                "aspect_ratio": kwargs.get("aspect_ratio", "9:16"),
                "style": style
            }
            
            logger.info(f"🎬 [Kling] Generating video: {prompt[:50]}...")
            
            async with session.post(
                f"{self.API_BASE_URL}/videos/generate",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    job_id = data.get("job_id", "")
                    
                    logger.info(f"✅ [Kling] Video job created: {job_id}")
                    
                    return VideoResult(
                        job_id=job_id,
                        status=VideoStatus.QUEUED,
                        cost_usd=0.0,  # Free tier
                        metadata=data
                    )
                else:
                    error_text = await response.text()
                    logger.error(f"❌ [Kling] API error: {response.status} - {error_text}")
                    
                    return VideoResult(
                        job_id="",
                        status=VideoStatus.FAILED,
                        error_message=f"API error: {response.status}"
                    )
        
        except Exception as e:
            logger.exception(f"❌ [Kling] Exception during video generation: {e}")
            return VideoResult(
                job_id="",
                status=VideoStatus.FAILED,
                error_message=str(e)
            )
    
    async def generate_from_image(
        self,
        image_url: str,
        animation_prompt: str,
        duration: int = 15,
        **kwargs
    ) -> VideoResult:
        """Generate video by animating an image"""
        try:
            session = await self._get_session()
            
            payload = {
                "image_url": image_url,
                "animation_prompt": animation_prompt,
                "duration": duration,
                "aspect_ratio": kwargs.get("aspect_ratio", "9:16")
            }
            
            logger.info(f"🎬 [Kling] Animating image: {image_url[:50]}...")
            
            async with session.post(
                f"{self.API_BASE_URL}/videos/image-to-video",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    job_id = data.get("job_id", "")
                    
                    logger.info(f"✅ [Kling] Image-to-video job created: {job_id}")
                    
                    return VideoResult(
                        job_id=job_id,
                        status=VideoStatus.QUEUED,
                        cost_usd=0.0,
                        metadata=data
                    )
                else:
                    error_text = await response.text()
                    logger.error(f"❌ [Kling] API error: {response.status} - {error_text}")
                    
                    return VideoResult(
                        job_id="",
                        status=VideoStatus.FAILED,
                        error_message=f"API error: {response.status}"
                    )
        
        except Exception as e:
            logger.exception(f"❌ [Kling] Exception during image-to-video: {e}")
            return VideoResult(
                job_id="",
                status=VideoStatus.FAILED,
                error_message=str(e)
            )
    
    async def get_status(self, job_id: str) -> VideoResult:
        """Get the status of a video generation job"""
        try:
            session = await self._get_session()
            
            async with session.get(
                f"{self.API_BASE_URL}/videos/{job_id}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    status_str = data.get("status", "processing").lower()
                    
                    # Map Kling status to our VideoStatus
                    status_map = {
                        "queued": VideoStatus.QUEUED,
                        "processing": VideoStatus.PROCESSING,
                        "completed": VideoStatus.COMPLETED,
                        "failed": VideoStatus.FAILED,
                        "cancelled": VideoStatus.CANCELLED
                    }
                    status = status_map.get(status_str, VideoStatus.PROCESSING)
                    
                    return VideoResult(
                        job_id=job_id,
                        status=status,
                        video_url=data.get("video_url"),
                        thumbnail_url=data.get("thumbnail_url"),
                        duration=data.get("duration"),
                        cost_usd=0.0,
                        metadata=data
                    )
                else:
                    error_text = await response.text()
                    logger.error(f"❌ [Kling] Status check error: {response.status} - {error_text}")
                    
                    return VideoResult(
                        job_id=job_id,
                        status=VideoStatus.FAILED,
                        error_message=f"Status check failed: {response.status}"
                    )
        
        except Exception as e:
            logger.exception(f"❌ [Kling] Exception during status check: {e}")
            return VideoResult(
                job_id=job_id,
                status=VideoStatus.FAILED,
                error_message=str(e)
            )
    
    async def estimate_cost(self, params: Dict[str, Any]) -> float:
        """Estimate the cost of video generation"""
        # Kling free tier - always 0.0
        return 0.0
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
