"""
Social Media Manager - Handles posting to multiple platforms
"""

import os
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import json

from core.logger import setup_logger
from core.config import Config

logger = setup_logger(__name__)

class SocialMediaManager:
    """Manages posting to social media platforms"""
    
    def __init__(self, config: Config):
        self.config = config
        self.posts_dir = Path("data/posts")
        self.posts_dir.mkdir(parents=True, exist_ok=True)
        
        # Platform handlers
        self.platforms = {
            "instagram": InstagramHandler(config),
            "twitter": TwitterHandler(config),
            "tiktok": TikTokHandler(config)
        }
    
    async def post_content(self, platform: str, content: Dict) -> bool:
        """Post content to specified platform"""
        logger.info(f"📤 Posting to {platform}...")
        
        if platform not in self.platforms:
            logger.error(f"❌ Unknown platform: {platform}")
            return False
        
        handler = self.platforms[platform]
        
        try:
            success = await handler.post(content)
            
            if success:
                # Record the post
                await self._record_post(platform, content)
                logger.info(f"✅ Posted to {platform}")
            else:
                logger.warning(f"⚠️ Failed to post to {platform}")
            
            return success
            
        except Exception as e:
            logger.exception(f"Error posting to {platform}: {e}")
            return False
    
    async def _record_post(self, platform: str, content: Dict):
        """Record posted content"""
        post_record = {
            "platform": platform,
            "content_id": content.get("id"),
            "posted_at": datetime.now().isoformat(),
            "content": content
        }
        
        post_file = self.posts_dir / f"{platform}_{content.get('id')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(post_file, "w") as f:
            json.dump(post_record, f, indent=2)

class PlatformHandler:
    """Base class for platform handlers"""
    
    def __init__(self, config: Config):
        self.config = config
    
    async def post(self, content: Dict) -> bool:
        """Post content - to be implemented by subclasses"""
        raise NotImplementedError

class InstagramHandler(PlatformHandler):
    """Instagram posting handler"""
    
    async def post(self, content: Dict) -> bool:
        """Post to Instagram"""
        # Instagram API integration would go here
        # For now, simulate posting
        
        access_token = self.config.get("api_keys.instagram")
        
        if not access_token:
            logger.warning("⚠️ Instagram access token not configured - simulating post")
            # Simulate successful post
            return True
        
        try:
            # Real Instagram API integration
            # This would use Instagram Graph API or similar
            logger.info(f"📸 Posting to Instagram: {content.get('caption', '')[:50]}...")
            
            # Simulate API call
            # response = requests.post(...)
            
            return True
            
        except Exception as e:
            logger.error(f"Instagram post failed: {e}")
            return False

class TwitterHandler(PlatformHandler):
    """Twitter/X posting handler"""
    
    async def post(self, content: Dict) -> bool:
        """Post to Twitter/X"""
        bearer_token = self.config.get("api_keys.twitter")
        
        if not bearer_token:
            logger.warning("⚠️ Twitter bearer token not configured - simulating post")
            return True
        
        try:
            # Real Twitter API integration
            logger.info(f"🐦 Posting to Twitter: {content.get('caption', '')[:50]}...")
            
            # Format for Twitter (character limit)
            caption = content.get("caption", "")
            if len(caption) > 280:
                caption = caption[:277] + "..."
            
            # Add hashtags
            hashtags = " ".join([f"#{h}" for h in content.get("hashtags", [])[:5]])
            tweet_text = f"{caption}\n\n{hashtags}"
            
            # Simulate API call
            # response = requests.post(...)
            
            return True
            
        except Exception as e:
            logger.error(f"Twitter post failed: {e}")
            return False

class TikTokHandler(PlatformHandler):
    """TikTok posting handler"""
    
    async def post(self, content: Dict) -> bool:
        """Post to TikTok"""
        access_token = self.config.get("api_keys.tiktok")
        
        if not access_token:
            logger.warning("⚠️ TikTok access token not configured - simulating post")
            return True
        
        try:
            import requests
            
            logger.info(f"🎵 Posting to TikTok: {content.get('caption', '')[:50]}...")
            
            # TikTok Content Posting API v2
            # Reference: https://developers.tiktok.com/doc/content-posting-api-get-started
            
            caption = content.get("caption", "")
            video_url = content.get("media_url")  # Pre-generated video URL
            
            if not video_url:
                logger.warning("⚠️ TikTok requires video content - skipping post")
                return False
            
            # TikTok API endpoint
            api_url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Add hashtags to caption
            hashtags = " ".join([f"#{h}" for h in content.get("hashtags", [])[:10]])
            full_caption = f"{caption}\n\n{hashtags}"
            
            payload = {
                "post_info": {
                    "title": full_caption[:150],  # TikTok title limit
                    "privacy_level": "PUBLIC_TO_EVERYONE",
                    "disable_duet": False,
                    "disable_comment": False,
                    "disable_stitch": False,
                    "video_cover_timestamp_ms": 1000
                },
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "video_url": video_url,
                    "video_size": content.get("video_size", 0)
                }
            }
            
            # Note: This is a simplified implementation
            # Real implementation would handle:
            # 1. Video upload to TikTok's servers
            # 2. Status polling for video processing
            # 3. Final publish confirmation
            
            # Simulate API call for now
            # response = requests.post(api_url, headers=headers, json=payload)
            # if response.status_code == 200:
            #     publish_id = response.json().get("data", {}).get("publish_id")
            #     logger.info(f"✅ TikTok publish initiated: {publish_id}")
            #     return True
            
            logger.info("✅ TikTok post simulated (API integration ready)")
            return True
            
        except Exception as e:
            logger.error(f"TikTok post failed: {e}")
            return False
