"""
Autonomous Orchestrator - Main controller for the influencer system
Coordinates all components to run autonomously
"""

import asyncio
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional

from .logger import setup_logger
from .config import Config
from .database import Database
from avatar.avatar_generator import AvatarGenerator
from content.content_engine import ContentEngine
from content.video_generator import VideoGenerator
from marketing.strategy_planner import MarketingStrategyPlanner
from social.social_manager import SocialMediaManager
from analytics.analytics_engine import AnalyticsEngine
from analytics.viral_scraper import ViralContentScraper
from analytics.viral_intelligence import ViralIntelligenceOptimizer
from analytics.video_analytics import VideoAnalytics
from content.podcast_generator import PodcastGenerator

logger = setup_logger(__name__)

class AutonomousOrchestrator:
    """Main orchestrator that runs the entire system autonomously"""
    
    def __init__(self):
        self.config = Config()
        self.running = False
        
        # Initialize database
        self.db = Database()
        
        # Initialize core components
        self.avatar_generator = AvatarGenerator(self.config)
        self.content_engine = ContentEngine(self.config)
        self.strategy_planner = MarketingStrategyPlanner(self.config)
        self.social_manager = SocialMediaManager(self.config)
        self.analytics = AnalyticsEngine(self.config)
        
        # Initialize viral intelligence components
        self.viral_scraper = ViralContentScraper(self.config)
        self.viral_optimizer = ViralIntelligenceOptimizer(self.config, self.db)
        
        # Initialize video generation system
        self.video_generator = VideoGenerator(self.config, self.db)
        self.video_analytics = VideoAnalytics(self.db)
        
        # Link video generator to content engine's media generator
        self.content_engine.media_generator.set_video_generator(self.video_generator)
        
        # Initialize podcast generator
        self.podcast_generator = PodcastGenerator(self.config, self.db, self.viral_optimizer)
        
        # State tracking
        self.avatar_created = False
        self.current_strategy = None
        self.content_queue = []
        self.posting_schedule = []
        self.last_viral_scrape = None
        self.last_podcast_generation = None
        self.last_video_generation = None

        # HITL settings - can be overridden at runtime
        self.hitl_enabled: bool = self.config.get("hitl.enabled", True)
        self.hitl_dashboard_url: str = self.config.get("hitl.dashboard_url", "http://localhost:5000")
        self._approval_callback: Optional[Callable] = None

        logger.info("✓ Orchestrator initialized with Viral Intelligence, Video Generation & Podcast Generator")
    
    async def start(self):
        """Initialize and start all systems"""
        logger.info("🔧 Initializing systems...")
        
        # Step 1: Create avatar if not exists
        if not self.avatar_created:
            await self._create_avatar()
        
        # Step 2: Generate initial marketing strategy
        await self._plan_strategy()
        
        # Step 3: Generate initial content batch
        await self._generate_content_batch()
        
        # Step 4: Schedule posts
        await self._schedule_posts()
        
        self.running = True
        logger.info("✅ All systems operational")
    
    async def _create_avatar(self):
        """Create the life-like avatar"""
        logger.info("🎨 Creating life-like avatar...")
        
        avatar_config = {
            "style": "realistic",
            "personality": self.config.get("avatar.personality", "friendly, professional, engaging"),
            "age_range": self.config.get("avatar.age_range", "25-35"),
            "gender": self.config.get("avatar.gender", "neutral"),
            "ethnicity": self.config.get("avatar.ethnicity", "diverse"),
        }
        
        avatar_data = await self.avatar_generator.create_avatar(avatar_config)
        
        if avatar_data:
            self.avatar_created = True
            logger.info("✅ Avatar created successfully")
        else:
            logger.error("❌ Failed to create avatar")
    
    async def _plan_strategy(self):
        """Generate marketing strategy autonomously"""
        logger.info("📊 Planning marketing strategy...")
        
        self.current_strategy = await self.strategy_planner.create_strategy(
            goals=self.config.get("marketing.goals", ["grow followers", "increase engagement"]),
            niche=self.config.get("marketing.niche", "lifestyle"),
            target_audience=self.config.get("marketing.target_audience", "18-35 professionals")
        )
        
        logger.info(f"✅ Strategy created: {self.current_strategy.get('name', 'Unknown')}")
    
    async def _generate_content_batch(self):
        """Generate a batch of content based on strategy"""
        logger.info("📝 Generating content batch...")
        
        if not self.current_strategy:
            await self._plan_strategy()
        
        # Check if we should scrape trending content for video generation
        should_scrape = (
            self.last_viral_scrape is None or
            (datetime.now() - self.last_viral_scrape).total_seconds() > 21600  # 6 hours
        )
        
        if should_scrape:
            logger.info("🔥 Scraping trending content for video generation...")
            try:
                platforms = self.config.get("social.platforms", ["instagram", "tiktok"])
                niche = self.config.get("marketing.niche", "lifestyle")
                viral_data = await self.viral_scraper.scrape_trending_content(
                    platforms=platforms,
                    niche=niche,
                    limit=20
                )
                
                # Analyze patterns
                if viral_data:
                    insights = await self.viral_optimizer.analyze_patterns(viral_data)
                    
                    # Generate videos from top trending topics
                    if self.config.get("content.video_generation.trending_topics", True):
                        await self._generate_videos_from_trends(insights[:3], viral_data[:5])
                
                self.last_viral_scrape = datetime.now()
            except Exception as e:
                logger.exception(f"❌ Error scraping trending content: {e}")
        
        # Generate content for the next week
        content_plan = self.current_strategy.get("content_plan", {})
        
        for day in range(7):
            content_items = await self.content_engine.generate_daily_content(
                strategy=self.current_strategy,
                day_offset=day,
                avatar_data=self.avatar_generator.get_avatar_data()
            )
            self.content_queue.extend(content_items)
        
        logger.info(f"✅ Generated {len(self.content_queue)} content items")
    
    async def _generate_videos_from_trends(self, insights: List[Dict], viral_data: List[Dict]):
        """Generate videos based on trending insights"""
        logger.info(f"🎬 Generating videos from {len(insights)} trending insights...")
        
        video_enabled = self.config.get("content.video_generation.trending_topics", True)
        if not video_enabled:
            logger.info("⏭️ Video generation from trends is disabled")
            return
        
        avatar_data = self.avatar_generator.get_avatar_data()
        
        for idx, insight in enumerate(insights):
            try:
                # Find matching viral content
                trend = viral_data[idx] if idx < len(viral_data) else insight
                
                # Generate video
                logger.info(f"🎬 Generating video {idx + 1}/{len(insights)} from trend: {trend.get('caption', '')[:50]}...")
                
                result = await self.video_generator.generate_video_from_trend(
                    trend=trend,
                    avatar=avatar_data,
                    platform="instagram"
                )
                
                if result and result.video_url:
                    logger.info(f"✅ Video generated: {result.job_id} (cost: ${result.cost_usd:.2f})")
                    
                    # Add to content queue
                    self.content_queue.append({
                        "id": f"video_{result.job_id}",
                        "type": "video",
                        "video_url": result.video_url,
                        "thumbnail_url": result.thumbnail_url,
                        "caption": trend.get("caption", ""),
                        "hashtags": trend.get("hashtags", []),
                        "duration": result.duration,
                        "cost_usd": result.cost_usd,
                        "created_at": datetime.now().isoformat(),
                        "from_trending": True
                    })
                else:
                    logger.warning(f"⚠️ Video generation failed for trend {idx + 1}")
            
            except Exception as e:
                logger.exception(f"❌ Error generating video from trend {idx + 1}: {e}")
        
        self.last_video_generation = datetime.now()
    
    
    async def _schedule_posts(self):
        """Schedule posts across platforms"""
        logger.info("📅 Scheduling posts...")
        
        platforms = self.config.get("social.platforms", ["instagram", "twitter", "tiktok"])
        posting_times = self.config.get("social.posting_times", {
            "instagram": ["09:00", "18:00"],
            "twitter": ["08:00", "12:00", "20:00"],
            #"tiktok": ["19:00"]
        })
        
        for content in self.content_queue:
            for platform in platforms:
                if platform in posting_times:
                    for time_str in posting_times[platform]:
                        post_time = self._parse_time(time_str, content.get("day_offset", 0))
                        self.posting_schedule.append({
                            "content": content,
                            "platform": platform,
                            "scheduled_time": post_time,
                            "posted": False
                        })
        
        # Sort by time
        self.posting_schedule.sort(key=lambda x: x["scheduled_time"])
        logger.info(f"✅ Scheduled {len(self.posting_schedule)} posts")
    
    def _parse_time(self, time_str: str, day_offset: int) -> datetime:
        """Parse time string and add day offset"""
        hour, minute = map(int, time_str.split(":"))
        base_time = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
        return base_time + timedelta(days=day_offset)
    
    async def run_forever(self):
        """Main loop - runs autonomously"""
        logger.info("🔄 Starting autonomous operation loop...")
        
        while self.running:
            try:
                # Check for scheduled posts
                await self._process_scheduled_posts()
                
                # Check analytics and optimize
                await self._optimize_based_on_analytics()
                
                # Generate daily podcast if it's time
                await self._generate_daily_podcast_if_needed()
                
                # Generate more content if queue is low
                if len(self.content_queue) < 10:
                    await self._generate_content_batch()
                    await self._schedule_posts()
                
                # Update strategy if needed
                await self._update_strategy_if_needed()
                
                # Sleep for a minute before next check
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.exception(f"Error in main loop: {e}")
                await asyncio.sleep(60)
    
    def set_approval_callback(self, callback: Callable):
        """Inject a callback used when HITL approval is needed (e.g. from the dashboard server)."""
        self._approval_callback = callback

    def _request_hitl_approval(self, approval_type: str, item: dict, description: str) -> Optional[str]:
        """
        Push an approval request to the dashboard.
        Returns the approval_id on success, None on failure.
        Falls back gracefully if the dashboard is not reachable.
        """
        # Use an injected callback when running in-process with the dashboard
        if self._approval_callback:
            return self._approval_callback(approval_type, item, description)

        # Otherwise call the dashboard HTTP API
        url = f"{self.hitl_dashboard_url}/api/request-approval"
        payload = json.dumps({
            "type": approval_type,
            "item": item,
            "description": description
        }).encode()
        try:
            req = urllib.request.Request(url, data=payload,
                                         headers={"Content-Type": "application/json"},
                                         method="POST")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                return data.get("approval_id")
        except Exception as e:
            logger.warning(f"Could not reach HITL dashboard ({e}); bypassing approval")
            return None

    async def _is_approved(self, content_id: str) -> bool:
        """Check the DB to see if a content item has been approved."""
        content = self.db.get_content(content_id)
        return content is not None and content.get("status") == "approved"

    async def _process_scheduled_posts(self):
        """Process and post scheduled content, gating through HITL approval when enabled."""
        now = datetime.now()

        for post in self.posting_schedule:
            if post["posted"] or post["scheduled_time"] > now:
                continue

            content = post["content"]
            content_id = content.get("id", "")

            try:
                # HITL gate: require approval before posting
                if self.hitl_enabled and self.config.get("hitl.require_posting_approval", True):
                    approved = await self._is_approved(content_id)
                    if not approved:
                        # Request approval if not already in the queue
                        existing = self.db.get_content(content_id)
                        if existing and existing.get("status") == "pending":
                            logger.info(f"⏳ Post {content_id} awaiting HITL approval — skipping")
                            self._request_hitl_approval(
                                "post",
                                {**content, "platform": post["platform"]},
                                f"Approve post to {post['platform']}: {content.get('caption', '')[:60]}"
                            )
                        continue

                logger.info(f"📤 Posting to {post['platform']}...")
                success = await self.social_manager.post_content(
                    platform=post["platform"],
                    content=content
                )

                if success:
                    post["posted"] = True
                    await self.analytics.record_post(
                        platform=post["platform"],
                        content_id=content_id,
                        timestamp=now
                    )
                    logger.info(f"✅ Posted to {post['platform']}")
                else:
                    logger.warning(f"⚠️ Failed to post to {post['platform']}")

            except Exception as e:
                logger.exception(f"Error posting to {post['platform']}: {e}")
    
    async def _optimize_based_on_analytics(self):
        """Analyze performance and optimize strategy"""
        # Check analytics every hour
        if datetime.now().minute == 0:
            logger.info("📊 Analyzing performance...")
            
            insights = await self.analytics.get_insights()
            
            if insights:
                # Adjust strategy based on what's working
                await self.strategy_planner.optimize_strategy(
                    current_strategy=self.current_strategy,
                    insights=insights
                )
                
                logger.info("✅ Strategy optimized based on analytics")
    
    async def _update_strategy_if_needed(self):
        """Update strategy periodically"""
        # Update strategy weekly
        if datetime.now().weekday() == 0 and datetime.now().hour == 9:
            logger.info("🔄 Updating marketing strategy...")
            await self._plan_strategy()
    
    async def _generate_daily_podcast_if_needed(self):
        """Generate daily podcast episode at scheduled time"""
        
        # Check if it's time to generate podcast
        if not self.podcast_generator.should_generate_now():
            return
        
        # Check if we already generated today
        today = datetime.now().date()
        if self.last_podcast_generation and self.last_podcast_generation.date() == today:
            return
        
        logger.info("🎙️ Starting daily podcast generation...")
        
        try:
            # Get duration from config (default 90 minutes)
            duration = self.config.get('podcast.duration_minutes', 90)
            
            # Generate podcast
            result = await self.podcast_generator.generate_daily_podcast(
                duration_minutes=duration
            )
            
            if result.get('success'):
                self.last_podcast_generation = datetime.now()
                
                episode_id = result.get('episode_id')
                audio_count = len(result.get('audio_files', []))
                
                logger.info(f"✅ Podcast episode complete: {episode_id}")
                logger.info(f"🎤 Generated {audio_count} audio segments")
                logger.info(f"📝 Script: {result.get('script_path')}")
                
                # TODO: Upload to podcast platforms (Spotify, Apple Podcasts, YouTube)
                # TODO: Post announcement on social media
                
            else:
                error = result.get('error', 'Unknown error')
                logger.error(f"❌ Podcast generation failed: {error}")
                
        except Exception as e:
            logger.exception(f"Error generating podcast: {e}")
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 Shutting down...")
        self.running = False
        
        # Close video generator sessions
        try:
            await self.video_generator.close()
            logger.info("✅ Video generator closed")
        except Exception as e:
            logger.exception(f"Error closing video generator: {e}")
        
        # Save state
        await self._save_state()
        
        logger.info("✅ Shutdown complete")
    
    async def _save_state(self):
        """Save current state to disk"""
        state = {
            "avatar_created": self.avatar_created,
            "strategy": self.current_strategy,
            "content_queue_size": len(self.content_queue),
            "scheduled_posts": len([p for p in self.posting_schedule if not p["posted"]]),
            "last_updated": datetime.now().isoformat()
        }
        
        state_file = Path("data/system_state.json")
        state_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)
        
        logger.info("💾 State saved")
