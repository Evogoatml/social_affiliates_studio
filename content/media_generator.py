"""
Media Generator - Generates images, carousels, and videos for social media
"""

import asyncio
from typing import Dict, Optional, Any
from pathlib import Path

from core.logger import setup_logger
from core.config import Config

logger = setup_logger(__name__)


class MediaGenerator:
    """Generate media content for social media posts"""
    
    def __init__(self, config: Config, video_generator=None):
        """
        Initialize media generator
        
        Args:
            config: Configuration object
            video_generator: Optional VideoGenerator instance (injected to avoid circular imports)
        """
        self.config = config
        self.video_generator = video_generator
        logger.info("✅ Media Generator initialized")
    
    def set_video_generator(self, video_generator):
        """Set video generator (for dependency injection)"""
        self.video_generator = video_generator
        logger.info("✅ Video Generator linked to Media Generator")
    
    async def generate_image(self, image_params: Dict) -> Optional[Dict]:
        """
        Generate a single image based on the provided parameters.
        
        Args:
            image_params: Dict with 'prompt', 'style', etc.
        
        Returns:
            Dict with image data or None if generation failed
        """
        try:
            logger.info(f"🖼️ Generating image: {image_params.get('prompt', '')[:50]}...")
            
            # This would integrate with actual image generation API
            # For now, return placeholder
            return {
                "type": "image",
                "url": "placeholder_image_url",
                "prompt": image_params.get("prompt", ""),
                "status": "placeholder"
            }
        except Exception as e:
            logger.exception(f"❌ Failed to generate image: {e}")
            return None
    
    async def generate_carousel_images(self, carousel_params: Dict) -> Optional[Dict]:
        """
        Generate multiple images for a carousel based on the provided parameters.
        
        Args:
            carousel_params: Dict with 'prompts', 'style', 'count', etc.
        
        Returns:
            Dict with carousel image data or None if generation failed
        """
        try:
            count = carousel_params.get("count", 3)
            logger.info(f"🖼️ Generating carousel with {count} images...")
            
            # This would integrate with actual image generation API
            # For now, return placeholder
            return {
                "type": "carousel",
                "images": [
                    {
                        "url": f"placeholder_carousel_image_{i}",
                        "index": i
                    }
                    for i in range(count)
                ],
                "status": "placeholder"
            }
        except Exception as e:
            logger.exception(f"❌ Failed to generate carousel: {e}")
            return None
    
    async def generate_video(self, video_params: Dict) -> Optional[Dict]:
        """
        Generate a video based on the provided parameters.
        
        Args:
            video_params: Dict with 'prompt', 'duration', 'style', 'trend', etc.
        
        Returns:
            Dict with video data or None if generation failed
        """
        try:
            if not self.video_generator:
                logger.warning("⚠️ Video generator not available, skipping video generation")
                return None
            
            logger.info(f"🎬 Generating video: {video_params.get('prompt', '')[:50]}...")
            
            # Check if we have trend data to use
            trend = video_params.get("trend")
            avatar = video_params.get("avatar")
            platform = video_params.get("platform", "instagram")
            
            if trend:
                # Generate from trending content
                result = await self.video_generator.generate_video_from_trend(
                    trend=trend,
                    avatar=avatar,
                    platform=platform
                )
            else:
                # Generate from direct parameters
                prompt = video_params.get("prompt", "")
                duration = video_params.get("duration", 15)
                style = video_params.get("style", "default")
                
                # This would call video generator directly
                logger.warning("⚠️ Direct video generation not yet implemented, use trend-based generation")
                return None
            
            if result and result.video_url:
                return {
                    "type": "video",
                    "url": result.video_url,
                    "thumbnail_url": result.thumbnail_url,
                    "duration": result.duration,
                    "cost_usd": result.cost_usd,
                    "job_id": result.job_id,
                    "status": result.status.value
                }
            else:
                logger.warning("⚠️ Video generation failed or returned no URL")
                return None
        
        except Exception as e:
            logger.exception(f"❌ Failed to generate video: {e}")
            return None
    
    def get_generation_stats(self) -> Dict:
        """Get media generation statistics"""
        stats = {
            "video_generator_available": self.video_generator is not None
        }
        
        if self.video_generator:
            stats["video_stats"] = self.video_generator.get_stats()
        
        return stats

