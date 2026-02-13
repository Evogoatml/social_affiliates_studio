"""
Video Utilities - Instagram optimization, thumbnail generation, video processing
"""

import os
import asyncio
from typing import Dict, Optional, Tuple
from pathlib import Path
import tempfile

try:
    from PIL import Image
except ImportError:
    Image = None

from core.logger import setup_logger

logger = setup_logger(__name__)


class VideoOptimizer:
    """Optimize videos for Instagram and other platforms"""
    
    INSTAGRAM_SPECS = {
        "reels": {
            "aspect_ratio": "9:16",
            "width": 1080,
            "height": 1920,
            "max_duration": 90,
            "min_duration": 3,
            "max_file_size_mb": 100,
            "formats": ["mp4", "mov"]
        },
        "stories": {
            "aspect_ratio": "9:16",
            "width": 1080,
            "height": 1920,
            "max_duration": 60,
            "min_duration": 1,
            "max_file_size_mb": 100,
            "formats": ["mp4", "mov"]
        },
        "feed": {
            "aspect_ratio": "1:1",
            "width": 1080,
            "height": 1080,
            "max_duration": 60,
            "min_duration": 3,
            "max_file_size_mb": 100,
            "formats": ["mp4", "mov"]
        }
    }
    
    def __init__(self):
        logger.info("✅ Video Optimizer initialized")
    
    def get_platform_specs(self, platform: str, content_type: str = "reels") -> Dict:
        """
        Get video specifications for a platform
        
        Args:
            platform: Platform name (instagram, tiktok, etc.)
            content_type: Content type (reels, stories, feed)
        
        Returns:
            Dict with video specifications
        """
        if platform == "instagram":
            return self.INSTAGRAM_SPECS.get(content_type, self.INSTAGRAM_SPECS["reels"])
        
        # Default to Instagram Reels specs
        return self.INSTAGRAM_SPECS["reels"]
    
    def validate_video_params(
        self,
        platform: str,
        content_type: str = "reels",
        duration: Optional[int] = None,
        aspect_ratio: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate video parameters for a platform
        
        Args:
            platform: Platform name
            content_type: Content type
            duration: Video duration in seconds
            aspect_ratio: Video aspect ratio (e.g., "9:16")
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        specs = self.get_platform_specs(platform, content_type)
        
        # Validate duration
        if duration is not None:
            if duration < specs["min_duration"]:
                return False, f"Duration {duration}s is too short (min: {specs['min_duration']}s)"
            if duration > specs["max_duration"]:
                return False, f"Duration {duration}s is too long (max: {specs['max_duration']}s)"
        
        # Validate aspect ratio
        if aspect_ratio is not None:
            if aspect_ratio != specs["aspect_ratio"]:
                return False, f"Aspect ratio {aspect_ratio} doesn't match {specs['aspect_ratio']}"
        
        return True, None
    
    def get_optimal_params(
        self,
        platform: str = "instagram",
        content_type: str = "reels"
    ) -> Dict:
        """
        Get optimal video parameters for a platform
        
        Args:
            platform: Platform name
            content_type: Content type
        
        Returns:
            Dict with optimal parameters
        """
        specs = self.get_platform_specs(platform, content_type)
        
        return {
            "duration": 15,  # Optimal for engagement
            "aspect_ratio": specs["aspect_ratio"],
            "width": specs["width"],
            "height": specs["height"],
            "format": "mp4",
            "fps": 30,
            "bitrate": "8M"
        }
    
    async def generate_thumbnail(
        self,
        video_url: Optional[str] = None,
        video_path: Optional[Path] = None,
        output_path: Optional[Path] = None,
        timestamp: float = 0.5
    ) -> Optional[str]:
        """
        Generate thumbnail from video
        
        Args:
            video_url: URL of the video
            video_path: Local path to video
            output_path: Where to save thumbnail
            timestamp: Position in video to extract (0.0-1.0)
        
        Returns:
            Path to generated thumbnail or None if failed
        """
        try:
            # This would use moviepy or ffmpeg in production
            # For now, return a placeholder
            logger.info(f"🖼️ Generating thumbnail for video")
            
            if output_path is None:
                output_path = Path(tempfile.gettempdir()) / f"thumbnail_{os.urandom(8).hex()}.jpg"
            
            # In production, extract frame from video here
            # For now, create a simple placeholder
            if Image:
                img = Image.new('RGB', (1080, 1920), color=(73, 109, 137))
                img.save(str(output_path))
                logger.info(f"✅ Thumbnail generated: {output_path}")
                return str(output_path)
            else:
                logger.warning("⚠️ PIL not available, skipping thumbnail generation")
                return None
        
        except Exception as e:
            logger.exception(f"❌ Failed to generate thumbnail: {e}")
            return None
    
    def estimate_file_size(
        self,
        duration: int,
        width: int,
        height: int,
        bitrate: str = "8M"
    ) -> float:
        """
        Estimate video file size
        
        Args:
            duration: Video duration in seconds
            width: Video width
            height: Video height
            bitrate: Video bitrate (e.g., "8M")
        
        Returns:
            Estimated file size in MB
        """
        # Extract bitrate value
        bitrate_value = float(bitrate.replace("M", ""))
        
        # Calculate: (bitrate in Mbps * duration in seconds) / 8 bits per byte
        estimated_mb = (bitrate_value * duration) / 8
        
        # Add overhead (audio, container, etc.) - roughly 20%
        estimated_mb *= 1.2
        
        return estimated_mb
    
    def format_caption_for_platform(
        self,
        caption: str,
        hashtags: list,
        platform: str = "instagram"
    ) -> str:
        """
        Format caption with hashtags for specific platform
        
        Args:
            caption: Base caption text
            hashtags: List of hashtags
            platform: Platform name
        
        Returns:
            Formatted caption
        """
        if platform == "instagram":
            # Instagram allows up to 30 hashtags
            hashtags_str = " ".join([f"#{tag}" for tag in hashtags[:30]])
            return f"{caption}\n\n{hashtags_str}"
        
        elif platform == "tiktok":
            # TikTok prefers hashtags integrated in caption
            hashtags_str = " ".join([f"#{tag}" for tag in hashtags[:10]])
            return f"{caption} {hashtags_str}"
        
        else:
            # Default format
            hashtags_str = " ".join([f"#{tag}" for tag in hashtags[:10]])
            return f"{caption}\n\n{hashtags_str}"
    
    def get_optimal_posting_times(self, platform: str = "instagram") -> list:
        """
        Get optimal posting times for a platform
        
        Args:
            platform: Platform name
        
        Returns:
            List of optimal posting times (HH:MM format)
        """
        if platform == "instagram":
            return ["09:00", "12:00", "17:00", "20:00"]
        elif platform == "tiktok":
            return ["07:00", "12:00", "19:00", "21:00"]
        else:
            return ["09:00", "12:00", "18:00"]


class VideoDownloader:
    """Download videos from URLs"""
    
    def __init__(self):
        logger.info("✅ Video Downloader initialized")
    
    async def download_video(
        self,
        url: str,
        output_path: Optional[Path] = None
    ) -> Optional[Path]:
        """
        Download video from URL
        
        Args:
            url: Video URL
            output_path: Where to save video
        
        Returns:
            Path to downloaded video or None if failed
        """
        try:
            import aiohttp
            
            if output_path is None:
                output_path = Path(tempfile.gettempdir()) / f"video_{os.urandom(8).hex()}.mp4"
            
            logger.info(f"⬇️ Downloading video from {url[:50]}...")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        with open(output_path, "wb") as f:
                            f.write(await response.read())
                        
                        logger.info(f"✅ Video downloaded: {output_path}")
                        return output_path
                    else:
                        logger.error(f"❌ Failed to download video: {response.status}")
                        return None
        
        except Exception as e:
            logger.exception(f"❌ Exception during video download: {e}")
            return None
