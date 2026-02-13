"""
Pika Labs Video Provider - Mid-tier option
https://pika.art
"""

import asyncio
import aiohttp
from typing import Dict, Any
from .base_provider import BaseVideoProvider, VideoResult, VideoStatus
from core.logger import setup_logger

logger = setup_logger(__name__)


class PikaProvider(BaseVideoProvider):
    """Pika Labs video generation provider"""
    
    API_BASE_URL = "https://api.pika.art/v1"
    
    def __init__(self, api_key: str, config: Dict[str, Any] = None):
        super().__init__(api_key, config)
        self.session = None
        self.cost_per_second = self.config.get("cost_per_second", 0.033)  # ~$0.50 per 15s video
    
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
            
            payload = {
                "prompt": prompt,
                "duration": duration,
                "aspect_ratio": kwargs.get("aspect_ratio", "9:16"),
                "style": style,
                "fps": kwargs.get("fps", 24)
            }
            
            logger.info(f"🎬 [Pika] Generating video: {prompt[:50]}...")
            
            async with session.post(
                f"{self.API_BASE_URL}/generate",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    job_id = data.get("id", "")
                    estimated_cost = self.cost_per_second * duration
                    
                    logger.info(f"✅ [Pika] Video job created: {job_id} (est. ${estimated_cost:.2f})")
                    
                    return VideoResult(
                        job_id=job_id,
                        status=VideoStatus.QUEUED,
                        cost_usd=estimated_cost,
                        metadata=data
                    )
                else:
                    error_text = await response.text()
                    logger.error(f"❌ [Pika] API error: {response.status} - {error_text}")
                    
                    return VideoResult(
                        job_id="",
                        status=VideoStatus.FAILED,
                        error_message=f"API error: {response.status}"
                    )
        
        except Exception as e:
            logger.exception(f"❌ [Pika] Exception during video generation: {e}")
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
                "image": image_url,
                "prompt": animation_prompt,
                "duration": duration,
                "aspect_ratio": kwargs.get("aspect_ratio", "9:16"),
                "motion": kwargs.get("motion", 2)  # Motion strength 1-4
            }
            
            logger.info(f"🎬 [Pika] Animating image: {image_url[:50]}...")
            
            async with session.post(
                f"{self.API_BASE_URL}/animate",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    job_id = data.get("id", "")
                    estimated_cost = self.cost_per_second * duration
                    
                    logger.info(f"✅ [Pika] Image-to-video job created: {job_id}")
                    
                    return VideoResult(
                        job_id=job_id,
                        status=VideoStatus.QUEUED,
                        cost_usd=estimated_cost,
                        metadata=data
                    )
                else:
                    error_text = await response.text()
                    logger.error(f"❌ [Pika] API error: {response.status} - {error_text}")
                    
                    return VideoResult(
                        job_id="",
                        status=VideoStatus.FAILED,
                        error_message=f"API error: {response.status}"
                    )
        
        except Exception as e:
            logger.exception(f"❌ [Pika] Exception during image-to-video: {e}")
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
                    
                    status_map = {
                        "pending": VideoStatus.QUEUED,
                        "processing": VideoStatus.PROCESSING,
                        "completed": VideoStatus.COMPLETED,
                        "failed": VideoStatus.FAILED
                    }
                    status = status_map.get(status_str, VideoStatus.PROCESSING)
                    
                    duration = data.get("duration", 0)
                    actual_cost = self.cost_per_second * duration if duration else None
                    
                    return VideoResult(
                        job_id=job_id,
                        status=status,
                        video_url=data.get("video", {}).get("url"),
                        thumbnail_url=data.get("thumbnail"),
                        duration=duration,
                        cost_usd=actual_cost,
                        metadata=data
                    )
                else:
                    error_text = await response.text()
                    logger.error(f"❌ [Pika] Status check error: {response.status} - {error_text}")
                    
                    return VideoResult(
                        job_id=job_id,
                        status=VideoStatus.FAILED,
                        error_message=f"Status check failed: {response.status}"
                    )
        
        except Exception as e:
            logger.exception(f"❌ [Pika] Exception during status check: {e}")
            return VideoResult(
                job_id=job_id,
                status=VideoStatus.FAILED,
                error_message=str(e)
            )
    
    async def estimate_cost(self, params: Dict[str, Any]) -> float:
        """Estimate the cost of video generation"""
        duration = params.get("duration", 15)
        return self.cost_per_second * duration
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
