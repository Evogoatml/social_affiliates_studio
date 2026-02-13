"""
HeyGen AI Avatar Video Provider - Premium tier for talking head videos
https://heygen.com/api
"""

import asyncio
import aiohttp
from typing import Dict, Any
from .base_provider import BaseVideoProvider, VideoResult, VideoStatus
from core.logger import setup_logger

logger = setup_logger(__name__)


class HeyGenProvider(BaseVideoProvider):
    """HeyGen AI avatar/talking head video generation provider"""
    
    API_BASE_URL = "https://api.heygen.com/v2"
    
    def __init__(self, api_key: str, config: Dict[str, Any] = None):
        super().__init__(api_key, config)
        self.session = None
        self.cost_per_minute = self.config.get("cost_per_minute", 8.0)  # ~$2.00 per 15s video
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "X-Api-Key": self.api_key,
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
        """Generate talking head video from text script"""
        try:
            session = await self._get_session()
            
            # HeyGen requires avatar_id and voice_id
            avatar_id = kwargs.get("avatar_id", self.config.get("default_avatar_id", "default"))
            voice_id = kwargs.get("voice_id", self.config.get("default_voice_id", "en-US-JennyNeural"))
            
            payload = {
                "video_inputs": [{
                    "character": {
                        "type": "avatar",
                        "avatar_id": avatar_id,
                        "avatar_style": style
                    },
                    "voice": {
                        "type": "text",
                        "input_text": prompt,
                        "voice_id": voice_id
                    },
                    "background": kwargs.get("background", "#000000")
                }],
                "dimension": {
                    "width": 1080,
                    "height": 1920
                },
                "aspect_ratio": "9:16"
            }
            
            logger.info(f"🎬 [HeyGen] Generating avatar video: {prompt[:50]}...")
            
            async with session.post(
                f"{self.API_BASE_URL}/video/generate",
                json=payload
            ) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    job_id = data.get("data", {}).get("video_id", "")
                    estimated_cost = (self.cost_per_minute / 60) * duration
                    
                    logger.info(f"✅ [HeyGen] Video job created: {job_id} (est. ${estimated_cost:.2f})")
                    
                    return VideoResult(
                        job_id=job_id,
                        status=VideoStatus.QUEUED,
                        cost_usd=estimated_cost,
                        metadata=data
                    )
                else:
                    error_text = await response.text()
                    logger.error(f"❌ [HeyGen] API error: {response.status} - {error_text}")
                    
                    return VideoResult(
                        job_id="",
                        status=VideoStatus.FAILED,
                        error_message=f"API error: {response.status}"
                    )
        
        except Exception as e:
            logger.exception(f"❌ [HeyGen] Exception during video generation: {e}")
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
        """HeyGen doesn't support image-to-video, use generate_video instead"""
        logger.warning("⚠️ [HeyGen] Image-to-video not supported, using text-to-video")
        return await self.generate_video(
            prompt=animation_prompt,
            duration=duration,
            **kwargs
        )
    
    async def get_status(self, job_id: str) -> VideoResult:
        """Get the status of a video generation job"""
        try:
            session = await self._get_session()
            
            async with session.get(
                f"{self.API_BASE_URL}/video_status.get?video_id={job_id}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    status_str = data.get("data", {}).get("status", "processing").lower()
                    
                    status_map = {
                        "pending": VideoStatus.QUEUED,
                        "processing": VideoStatus.PROCESSING,
                        "completed": VideoStatus.COMPLETED,
                        "failed": VideoStatus.FAILED
                    }
                    status = status_map.get(status_str, VideoStatus.PROCESSING)
                    
                    video_data = data.get("data", {})
                    duration = video_data.get("duration", 0)
                    actual_cost = (self.cost_per_minute / 60) * duration if duration else None
                    
                    return VideoResult(
                        job_id=job_id,
                        status=status,
                        video_url=video_data.get("video_url"),
                        thumbnail_url=video_data.get("thumbnail_url"),
                        duration=duration,
                        cost_usd=actual_cost,
                        metadata=data
                    )
                else:
                    error_text = await response.text()
                    logger.error(f"❌ [HeyGen] Status check error: {response.status} - {error_text}")
                    
                    return VideoResult(
                        job_id=job_id,
                        status=VideoStatus.FAILED,
                        error_message=f"Status check failed: {response.status}"
                    )
        
        except Exception as e:
            logger.exception(f"❌ [HeyGen] Exception during status check: {e}")
            return VideoResult(
                job_id=job_id,
                status=VideoStatus.FAILED,
                error_message=str(e)
            )
    
    async def estimate_cost(self, params: Dict[str, Any]) -> float:
        """Estimate the cost of video generation"""
        duration = params.get("duration", 15)
        return (self.cost_per_minute / 60) * duration
    
    def supports_image_to_video(self) -> bool:
        """HeyGen doesn't support image-to-video"""
        return False
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
