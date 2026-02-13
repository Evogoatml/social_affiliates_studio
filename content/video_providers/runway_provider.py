"""
Runway Gen-4.5 Video Provider - Premium tier
https://runwayml.com/api
"""

import asyncio
import aiohttp
from typing import Dict, Any
from .base_provider import BaseVideoProvider, VideoResult, VideoStatus
from core.logger import setup_logger

logger = setup_logger(__name__)


class RunwayProvider(BaseVideoProvider):
    """Runway ML video generation provider (premium quality)"""
    
    API_BASE_URL = "https://api.runwayml.com/v1"
    
    def __init__(self, api_key: str, config: Dict[str, Any] = None):
        super().__init__(api_key, config)
        self.session = None
        self.cost_per_second = self.config.get("cost_per_second", 0.1)  # ~$1.50 per 15s video
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "X-Runway-Version": "2024-01-01"
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
        """Generate video from text prompt using Gen-4.5"""
        try:
            session = await self._get_session()
            
            payload = {
                "model": "gen4_5",
                "prompt": prompt,
                "duration": duration,
                "aspect_ratio": kwargs.get("aspect_ratio", "9:16"),
                "resolution": kwargs.get("resolution", "1080p"),
                "style_preset": style
            }
            
            logger.info(f"🎬 [Runway] Generating high-quality video: {prompt[:50]}...")
            
            async with session.post(
                f"{self.API_BASE_URL}/generate",
                json=payload
            ) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    job_id = data.get("id", "")
                    estimated_cost = self.cost_per_second * duration
                    
                    logger.info(f"✅ [Runway] Video job created: {job_id} (est. ${estimated_cost:.2f})")
                    
                    return VideoResult(
                        job_id=job_id,
                        status=VideoStatus.QUEUED,
                        cost_usd=estimated_cost,
                        metadata=data
                    )
                else:
                    error_text = await response.text()
                    logger.error(f"❌ [Runway] API error: {response.status} - {error_text}")
                    
                    return VideoResult(
                        job_id="",
                        status=VideoStatus.FAILED,
                        error_message=f"API error: {response.status}"
                    )
        
        except Exception as e:
            logger.exception(f"❌ [Runway] Exception during video generation: {e}")
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
                "model": "gen4_5",
                "image": image_url,
                "prompt": animation_prompt,
                "duration": duration,
                "aspect_ratio": kwargs.get("aspect_ratio", "9:16"),
                "motion_intensity": kwargs.get("motion_intensity", 5)  # 1-10 scale
            }
            
            logger.info(f"🎬 [Runway] Animating image: {image_url[:50]}...")
            
            async with session.post(
                f"{self.API_BASE_URL}/image-to-video",
                json=payload
            ) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    job_id = data.get("id", "")
                    estimated_cost = self.cost_per_second * duration
                    
                    logger.info(f"✅ [Runway] Image-to-video job created: {job_id}")
                    
                    return VideoResult(
                        job_id=job_id,
                        status=VideoStatus.QUEUED,
                        cost_usd=estimated_cost,
                        metadata=data
                    )
                else:
                    error_text = await response.text()
                    logger.error(f"❌ [Runway] API error: {response.status} - {error_text}")
                    
                    return VideoResult(
                        job_id="",
                        status=VideoStatus.FAILED,
                        error_message=f"API error: {response.status}"
                    )
        
        except Exception as e:
            logger.exception(f"❌ [Runway] Exception during image-to-video: {e}")
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
                f"{self.API_BASE_URL}/tasks/{job_id}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    status_str = data.get("status", "PROCESSING").upper()
                    
                    status_map = {
                        "PENDING": VideoStatus.QUEUED,
                        "RUNNING": VideoStatus.PROCESSING,
                        "SUCCEEDED": VideoStatus.COMPLETED,
                        "FAILED": VideoStatus.FAILED,
                        "CANCELLED": VideoStatus.CANCELLED
                    }
                    status = status_map.get(status_str, VideoStatus.PROCESSING)
                    
                    # Get output from artifacts
                    artifacts = data.get("output", {}).get("artifacts", [])
                    video_url = artifacts[0] if artifacts else None
                    
                    duration = data.get("metadata", {}).get("duration", 0)
                    actual_cost = self.cost_per_second * duration if duration else None
                    
                    return VideoResult(
                        job_id=job_id,
                        status=status,
                        video_url=video_url,
                        thumbnail_url=data.get("output", {}).get("thumbnail"),
                        duration=duration,
                        cost_usd=actual_cost,
                        metadata=data
                    )
                else:
                    error_text = await response.text()
                    logger.error(f"❌ [Runway] Status check error: {response.status} - {error_text}")
                    
                    return VideoResult(
                        job_id=job_id,
                        status=VideoStatus.FAILED,
                        error_message=f"Status check failed: {response.status}"
                    )
        
        except Exception as e:
            logger.exception(f"❌ [Runway] Exception during status check: {e}")
            return VideoResult(
                job_id=job_id,
                status=VideoStatus.FAILED,
                error_message=str(e)
            )
    
    async def estimate_cost(self, params: Dict[str, Any]) -> float:
        """Estimate the cost of video generation"""
        duration = params.get("duration", 15)
        return self.cost_per_second * duration
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a video generation job"""
        try:
            session = await self._get_session()
            
            async with session.post(
                f"{self.API_BASE_URL}/tasks/{job_id}/cancel"
            ) as response:
                if response.status == 200:
                    logger.info(f"✅ [Runway] Job cancelled: {job_id}")
                    return True
                else:
                    logger.warning(f"⚠️ [Runway] Failed to cancel job: {job_id}")
                    return False
        
        except Exception as e:
            logger.exception(f"❌ [Runway] Exception during job cancellation: {e}")
            return False
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
