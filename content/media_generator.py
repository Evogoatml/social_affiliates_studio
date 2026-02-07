"""
Media Generator - Creates images and videos for social media content
"""

import os
import requests
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
import json

from core.logger import setup_logger
from core.config import Config

logger = setup_logger(__name__)

class MediaGenerator:
    """Generates media (images/videos) for social content"""
    
    def __init__(self, config: Config):
        self.config = config
        self.media_dir = Path("data/media")
        self.media_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.media_dir / "images").mkdir(exist_ok=True)
        (self.media_dir / "videos").mkdir(exist_ok=True)
        (self.media_dir / "thumbnails").mkdir(exist_ok=True)
    
    async def generate_image(
        self, 
        prompt: str, 
        content_id: str,
        size: str = "1024x1024"
    ) -> Optional[Dict]:
        """Generate an image using AI"""
        logger.info(f"🎨 Generating image for content {content_id}...")
        
        openai_key = self.config.get("api_keys.openai")
        
        if openai_key:
            return await self._generate_with_dalle(prompt, content_id, size)
        
        stability_key = self.config.get("api_keys.stability")
        if stability_key:
            return await self._generate_with_stability(prompt, content_id)
        
        # Fallback to placeholder
        return await self._create_placeholder_image(content_id)
    
    async def _generate_with_dalle(
        self, 
        prompt: str, 
        content_id: str,
        size: str = "1024x1024"
    ) -> Optional[Dict]:
        """Generate image using DALL-E"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.config.get("api_keys.openai"))
            
            logger.info("🖼️ Generating with DALL-E 3...")
            
            response = client.images.generate(
                prompt=prompt,
                n=1,
                size=size,
                model="dall-e-3",
                quality="standard"
            )
            
            image_url = response.data[0].url
            
            # Download and save
            image_path = await self._download_image(image_url, f"{content_id}.png")
            
            return {
                "type": "image",
                "path": str(image_path),
                "url": image_url,
                "prompt": prompt,
                "generator": "dalle-3",
                "size": size,
                "content_id": content_id,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"DALL-E generation failed: {e}")
            return None
    
    async def _generate_with_stability(
        self, 
        prompt: str, 
        content_id: str
    ) -> Optional[Dict]:
        """Generate image using Stability AI"""
        try:
            api_key = self.config.get("api_keys.stability")
            
            logger.info("🖼️ Generating with Stability AI...")
            
            response = requests.post(
                "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "text_prompts": [{"text": prompt, "weight": 1}],
                    "cfg_scale": 7,
                    "height": 1024,
                    "width": 1024,
                    "samples": 1,
                    "steps": 30
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                image_base64 = result["artifacts"][0]["base64"]
                
                image_path = await self._save_base64_image(image_base64, f"{content_id}.png")
                
                return {
                    "type": "image",
                    "path": str(image_path),
                    "prompt": prompt,
                    "generator": "stability-ai",
                    "content_id": content_id,
                    "created_at": datetime.now().isoformat()
                }
            else:
                logger.warning(f"Stability AI failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Stability AI generation failed: {e}")
            return None
    
    async def _create_placeholder_image(self, content_id: str) -> Dict:
        """Create placeholder image metadata"""
        return {
            "type": "image",
            "path": None,
            "placeholder": True,
            "content_id": content_id,
            "created_at": datetime.now().isoformat(),
            "note": "Use stock images or manual upload"
        }
    
    async def generate_video(
        self, 
        script: Dict, 
        content_id: str,
        avatar_data: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Generate video content"""
        logger.info(f"🎥 Generating video for content {content_id}...")
        
        # Video generation is complex and requires specialized services
        # Options: D-ID, Synthesia, Runway ML, etc.
        
        video_data = {
            "type": "video",
            "content_id": content_id,
            "script": script,
            "duration": script.get("duration_estimate", "30-60 seconds"),
            "status": "pending_generation",
            "created_at": datetime.now().isoformat(),
            "note": "Video generation requires integration with D-ID, Synthesia, or similar service"
        }
        
        # For now, return metadata - actual generation would happen via external service
        return video_data
    
    async def generate_carousel_images(
        self, 
        prompts: List[str], 
        content_id: str
    ) -> List[Dict]:
        """Generate multiple images for carousel post"""
        logger.info(f"🎨 Generating carousel images for content {content_id}...")
        
        images = []
        for i, prompt in enumerate(prompts):
            image = await self.generate_image(
                prompt=prompt,
                content_id=f"{content_id}_slide_{i+1}",
                size="1080x1080"
            )
            if image:
                images.append(image)
        
        logger.info(f"✅ Generated {len(images)} carousel images")
        return images
    
    async def _download_image(self, url: str, filename: str) -> Path:
        """Download image from URL"""
        response = requests.get(url)
        image_path = self.media_dir / "images" / filename
        image_path.write_bytes(response.content)
        logger.info(f"💾 Image saved: {image_path}")
        return image_path
    
    async def _save_base64_image(self, base64_data: str, filename: str) -> Path:
        """Save base64 encoded image"""
        import base64
        
        image_data = base64.b64decode(base64_data)
        image_path = self.media_dir / "images" / filename
        image_path.write_bytes(image_data)
        logger.info(f"💾 Image saved: {image_path}")
        return image_path
    
    async def create_thumbnail(self, image_path: Path, content_id: str) -> Path:
        """Create thumbnail from image"""
        try:
            from PIL import Image
            
            # Load and resize image
            img = Image.open(image_path)
            img.thumbnail((400, 400))
            
            thumbnail_path = self.media_dir / "thumbnails" / f"{content_id}_thumb.jpg"
            img.save(thumbnail_path, "JPEG", quality=85)
            
            logger.info(f"📸 Thumbnail created: {thumbnail_path}")
            return thumbnail_path
            
        except ImportError:
            logger.warning("PIL not available - skipping thumbnail creation")
            return image_path
        except Exception as e:
            logger.error(f"Thumbnail creation failed: {e}")
            return image_path
    
    async def optimize_for_platform(
        self, 
        image_path: Path, 
        platform: str,
        content_id: str
    ) -> Path:
        """Optimize image for specific platform requirements"""
        try:
            from PIL import Image
            
            # Platform-specific requirements
            requirements = {
                "instagram": {
                    "feed": (1080, 1080),
                    "story": (1080, 1920),
                    "reel": (1080, 1920)
                },
                "twitter": {
                    "post": (1200, 675)
                },
                "tiktok": {
                    "video": (1080, 1920)
                }
            }
            
            if platform not in requirements:
                return image_path
            
            img = Image.open(image_path)
            target_size = requirements[platform].get("feed", (1080, 1080))
            
            # Resize maintaining aspect ratio
            img.thumbnail(target_size, Image.Resampling.LANCZOS)
            
            # Create new image with target size and paste resized image centered
            optimized = Image.new("RGB", target_size, (255, 255, 255))
            offset = ((target_size[0] - img.size[0]) // 2, (target_size[1] - img.size[1]) // 2)
            optimized.paste(img, offset)
            
            optimized_path = self.media_dir / "images" / f"{content_id}_{platform}.jpg"
            optimized.save(optimized_path, "JPEG", quality=90)
            
            logger.info(f"✅ Image optimized for {platform}: {optimized_path}")
            return optimized_path
            
        except ImportError:
            logger.warning("PIL not available - skipping optimization")
            return image_path
        except Exception as e:
            logger.error(f"Image optimization failed: {e}")
            return image_path
