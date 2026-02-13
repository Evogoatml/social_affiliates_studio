"""
Video Generator - Main orchestrator for video generation
Handles multi-provider failover, cost tracking, and queue management
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import json

from core.logger import setup_logger
from core.config import Config
from .video_providers import VideoProviderRegistry, BaseVideoProvider
from .video_providers.base_provider import VideoResult, VideoStatus
from .video_queue import VideoQueue
from .video_utils import VideoOptimizer

logger = setup_logger(__name__)


class VideoGenerator:
    """Main video generation orchestrator with multi-provider support"""
    
    def __init__(self, config: Config, db=None):
        self.config = config
        self.db = db
        
        # Load video configuration
        self.video_config = self._load_video_config()
        
        # Initialize providers
        self.providers: Dict[str, BaseVideoProvider] = {}
        self._initialize_providers()
        
        # Initialize queue and optimizer
        self.queue = VideoQueue(config=self.video_config)
        self.optimizer = VideoOptimizer()
        
        # Budget tracking
        self.daily_spent = 0.0
        self.monthly_spent = 0.0
        self.last_budget_reset = datetime.now()
        
        # Statistics
        self.stats = {
            "total_generated": 0,
            "total_cost": 0.0,
            "by_provider": {}
        }
        
        logger.info("✅ Video Generator initialized")
    
    def _load_video_config(self) -> Dict:
        """Load video configuration from config file"""
        config_path = Path("config/video_config.json")
        
        if config_path.exists():
            with open(config_path, "r") as f:
                return json.load(f)
        else:
            logger.warning("⚠️ video_config.json not found, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default video configuration"""
        return {
            "video_generation": {
                "enabled": True,
                "default_provider": "kling",
                "fallback_providers": ["pika", "runway"],
                "budget": {
                    "daily_limit_usd": 10.0,
                    "monthly_limit_usd": 200.0,
                    "per_video_max_usd": 2.0
                },
                "instagram_settings": {
                    "reels_duration": 15,
                    "stories_duration": 15,
                    "aspect_ratio": "9:16",
                    "resolution": "1080x1920",
                    "max_file_size_mb": 100
                },
                "providers": {
                    "kling": {
                        "enabled": True,
                        "priority": 1,
                        "cost_per_video": 0.0,
                        "rate_limit_per_day": 10
                    },
                    "pika": {
                        "enabled": False,
                        "priority": 2,
                        "cost_per_video": 0.5,
                        "rate_limit_per_minute": 5
                    },
                    "runway": {
                        "enabled": False,
                        "priority": 3,
                        "cost_per_video": 1.5,
                        "rate_limit_per_minute": 2
                    },
                    "heygen": {
                        "enabled": False,
                        "priority": 4,
                        "cost_per_video": 2.0,
                        "rate_limit_per_minute": 1
                    }
                }
            }
        }
    
    def _initialize_providers(self):
        """Initialize enabled video providers"""
        api_keys = self.config.get("api_keys.video", {})
        providers_config = self.video_config.get("video_generation", {}).get("providers", {})
        
        for provider_name, provider_config in providers_config.items():
            if not provider_config.get("enabled", False):
                logger.info(f"⏭️ Skipping disabled provider: {provider_name}")
                continue
            
            api_key = api_keys.get(provider_name, "")
            if not api_key:
                logger.warning(f"⚠️ No API key found for {provider_name}, skipping")
                continue
            
            provider = VideoProviderRegistry.create_provider(
                name=provider_name,
                api_key=api_key,
                config=provider_config
            )
            
            if provider:
                self.providers[provider_name] = provider
                logger.info(f"✅ Initialized provider: {provider_name}")
    
    async def generate_video_from_trend(
        self,
        trend: Dict,
        avatar: Optional[Dict] = None,
        platform: str = "instagram"
    ) -> Optional[VideoResult]:
        """
        Generate video based on trending content
        
        Args:
            trend: Trending content data from viral_intelligence
            avatar: Avatar data for personalization
            platform: Target platform (instagram, tiktok, etc.)
        
        Returns:
            VideoResult or None if generation failed
        """
        # Check if video generation is enabled
        if not self.video_config.get("video_generation", {}).get("enabled", True):
            logger.info("⏭️ Video generation is disabled")
            return None
        
        # Check budget limits
        if not self._check_budget():
            logger.warning("⚠️ Budget limit reached, skipping video generation")
            return None
        
        # Build video prompt from trend
        prompt = self._build_prompt_from_trend(trend, avatar, platform)
        
        # Get video parameters based on platform
        params = self._get_platform_params(platform)
        
        # Generate video with failover
        result = await self._generate_with_failover(
            prompt=prompt,
            **params
        )
        
        # Track in database if successful
        if result and result.status != VideoStatus.FAILED and self.db:
            await self._track_generation(result, trend, prompt)
        
        return result
    
    def _build_prompt_from_trend(
        self,
        trend: Dict,
        avatar: Optional[Dict],
        platform: str
    ) -> str:
        """Build video generation prompt from trending content"""
        caption = trend.get("caption", "")
        hashtags = trend.get("hashtags", [])
        theme = trend.get("theme", "lifestyle")
        
        # Extract avatar characteristics
        avatar_style = "friendly, professional"
        if avatar:
            personality = avatar.get("personality", "")
            avatar_style = personality or avatar_style
        
        # Build platform-specific prompt
        if platform == "instagram":
            duration = self.video_config.get("video_generation", {}).get(
                "instagram_settings", {}
            ).get("reels_duration", 15)
            
            prompt = f"""Create a {duration}-second Instagram Reel about {theme}.
Content: {caption[:200]}
Style: Trendy vertical video with engaging hooks and text overlays.
Avatar: {avatar_style}
Hashtags: {', '.join(hashtags[:5])}
Visual: Eye-catching, fast-paced, optimized for mobile viewing."""
        else:
            prompt = f"""Create engaging social media video about {theme}.
Content: {caption[:200]}
Style: Professional yet trendy.
Hashtags: {', '.join(hashtags[:5])}"""
        
        return prompt
    
    def _get_platform_params(self, platform: str) -> Dict:
        """Get platform-specific video parameters"""
        instagram_settings = self.video_config.get("video_generation", {}).get(
            "instagram_settings", {}
        )
        
        if platform == "instagram":
            return {
                "duration": instagram_settings.get("reels_duration", 15),
                "aspect_ratio": instagram_settings.get("aspect_ratio", "9:16"),
                "style": "trendy"
            }
        
        # Default parameters
        return {
            "duration": 15,
            "aspect_ratio": "9:16",
            "style": "default"
        }
    
    async def _generate_with_failover(
        self,
        prompt: str,
        **kwargs
    ) -> Optional[VideoResult]:
        """
        Generate video with automatic provider failover
        
        Args:
            prompt: Video description
            **kwargs: Generation parameters
        
        Returns:
            VideoResult or None if all providers failed
        """
        # Get ordered list of providers
        provider_order = self._get_provider_order()
        
        if not provider_order:
            logger.error("❌ No video providers available")
            return None
        
        # Try each provider in order
        for provider_name in provider_order:
            provider = self.providers.get(provider_name)
            if not provider:
                continue
            
            try:
                logger.info(f"🎬 Trying provider: {provider_name}")
                
                # Estimate cost
                estimated_cost = await provider.estimate_cost({
                    "duration": kwargs.get("duration", 15),
                    "prompt": prompt
                })
                
                # Check if within budget
                budget_limit = self.video_config.get("video_generation", {}).get(
                    "budget", {}
                ).get("per_video_max_usd", 2.0)
                
                if estimated_cost > budget_limit:
                    logger.warning(
                        f"⚠️ {provider_name} cost ${estimated_cost:.2f} exceeds "
                        f"limit ${budget_limit:.2f}, trying next provider"
                    )
                    continue
                
                # Generate video
                result = await provider.generate_video(
                    prompt=prompt,
                    **kwargs
                )
                
                if result.status != VideoStatus.FAILED:
                    # Wait for completion
                    result = await self._wait_for_completion(provider, result.job_id)
                    
                    if result.status == VideoStatus.COMPLETED:
                        # Update budget tracking
                        self._update_budget(result.cost_usd or estimated_cost)
                        
                        # Update stats
                        self._update_stats(provider_name, result)
                        
                        logger.info(
                            f"✅ Video generated successfully with {provider_name} "
                            f"(cost: ${result.cost_usd:.2f})"
                        )
                        return result
                    else:
                        logger.warning(
                            f"⚠️ {provider_name} generation failed, trying next provider"
                        )
                else:
                    logger.warning(
                        f"⚠️ {provider_name} returned error: {result.error_message}"
                    )
            
            except Exception as e:
                logger.exception(f"❌ Exception with {provider_name}: {e}")
                continue
        
        logger.error("❌ All video providers failed")
        return None
    
    def _get_provider_order(self) -> List[str]:
        """Get providers ordered by priority"""
        providers_config = self.video_config.get("video_generation", {}).get("providers", {})
        
        # Filter enabled providers and sort by priority
        enabled = [
            (name, config.get("priority", 999))
            for name, config in providers_config.items()
            if config.get("enabled", False) and name in self.providers
        ]
        
        # Sort by priority (lower number = higher priority)
        enabled.sort(key=lambda x: x[1])
        
        return [name for name, _ in enabled]
    
    async def _wait_for_completion(
        self,
        provider: BaseVideoProvider,
        job_id: str,
        timeout: int = 300,
        poll_interval: int = 5
    ) -> VideoResult:
        """
        Wait for video generation to complete
        
        Args:
            provider: Provider instance
            job_id: Job ID to poll
            timeout: Maximum wait time in seconds
            poll_interval: Time between status checks
        
        Returns:
            Final VideoResult
        """
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < timeout:
            result = await provider.get_status(job_id)
            
            if result.status in [VideoStatus.COMPLETED, VideoStatus.FAILED, VideoStatus.CANCELLED]:
                return result
            
            logger.info(f"⏳ Video generation in progress... ({result.status.value})")
            await asyncio.sleep(poll_interval)
        
        logger.warning(f"⚠️ Video generation timed out after {timeout}s")
        return VideoResult(
            job_id=job_id,
            status=VideoStatus.FAILED,
            error_message="Timeout waiting for video completion"
        )
    
    def _check_budget(self) -> bool:
        """Check if we're within budget limits"""
        budget = self.video_config.get("video_generation", {}).get("budget", {})
        daily_limit = budget.get("daily_limit_usd", 10.0)
        monthly_limit = budget.get("monthly_limit_usd", 200.0)
        
        # Reset daily budget if needed
        if (datetime.now() - self.last_budget_reset).days >= 1:
            self.daily_spent = 0.0
            self.last_budget_reset = datetime.now()
        
        # Check limits
        if self.daily_spent >= daily_limit:
            logger.warning(f"⚠️ Daily budget limit reached: ${self.daily_spent:.2f} / ${daily_limit:.2f}")
            return False
        
        if self.monthly_spent >= monthly_limit:
            logger.warning(f"⚠️ Monthly budget limit reached: ${self.monthly_spent:.2f} / ${monthly_limit:.2f}")
            return False
        
        return True
    
    def _update_budget(self, cost: float):
        """Update budget tracking"""
        self.daily_spent += cost
        self.monthly_spent += cost
        logger.info(f"💰 Budget: Daily ${self.daily_spent:.2f}, Monthly ${self.monthly_spent:.2f}")
    
    def _update_stats(self, provider_name: str, result: VideoResult):
        """Update generation statistics"""
        self.stats["total_generated"] += 1
        self.stats["total_cost"] += result.cost_usd or 0.0
        
        if provider_name not in self.stats["by_provider"]:
            self.stats["by_provider"][provider_name] = {
                "count": 0,
                "cost": 0.0,
                "success": 0,
                "failed": 0
            }
        
        provider_stats = self.stats["by_provider"][provider_name]
        provider_stats["count"] += 1
        provider_stats["cost"] += result.cost_usd or 0.0
        
        if result.status == VideoStatus.COMPLETED:
            provider_stats["success"] += 1
        else:
            provider_stats["failed"] += 1
    
    async def _track_generation(self, result: VideoResult, trend: Dict, prompt: str):
        """Track video generation in database"""
        try:
            if not self.db:
                return
            
            self.db.add_video_generation({
                "job_id": result.job_id,
                "prompt": prompt,
                "cost_usd": result.cost_usd or 0.0,
                "duration_seconds": result.duration or 0,
                "status": result.status.value,
                "video_url": result.video_url or "",
                "trend_id": trend.get("id", ""),
                "created_at": datetime.now().isoformat()
            })
            
            logger.info(f"✅ Video generation tracked in database")
        except Exception as e:
            logger.exception(f"❌ Failed to track video generation: {e}")
    
    def get_stats(self) -> Dict:
        """Get generation statistics"""
        return {
            **self.stats,
            "budget": {
                "daily_spent": self.daily_spent,
                "monthly_spent": self.monthly_spent,
                "daily_limit": self.video_config.get("video_generation", {}).get(
                    "budget", {}
                ).get("daily_limit_usd", 10.0),
                "monthly_limit": self.video_config.get("video_generation", {}).get(
                    "budget", {}
                ).get("monthly_limit_usd", 200.0)
            }
        }
    
    async def close(self):
        """Close all provider sessions"""
        for provider in self.providers.values():
            try:
                await provider.close()
            except Exception as e:
                logger.exception(f"❌ Error closing provider: {e}")
