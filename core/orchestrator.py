"""
Autonomous Orchestrator - Main controller for the influencer system
Coordinates all components to run autonomously
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List
import json

from .logger import setup_logger
from .config import Config
from avatar.avatar_generator import AvatarGenerator
from content.content_engine import ContentEngine
from marketing.strategy_planner import MarketingStrategyPlanner
from social.social_manager import SocialMediaManager
from analytics.analytics_engine import AnalyticsEngine

logger = setup_logger(__name__)

class AutonomousOrchestrator:
    """Main orchestrator that runs the entire system autonomously"""
    
    def __init__(self):
        self.config = Config()
        self.running = False
        
        # Initialize core components
        self.avatar_generator = AvatarGenerator(self.config)
        self.content_engine = ContentEngine(self.config)
        self.strategy_planner = MarketingStrategyPlanner(self.config)
        self.social_manager = SocialMediaManager(self.config)
        self.analytics = AnalyticsEngine(self.config)
        
        # State tracking
        self.avatar_created = False
        self.current_strategy = None
        self.content_queue = []
        self.posting_schedule = []
        
        logger.info("✓ Orchestrator initialized")
    
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
    
    async def _process_scheduled_posts(self):
        """Process and post scheduled content"""
        now = datetime.now()
        
        for post in self.posting_schedule:
            if not post["posted"] and post["scheduled_time"] <= now:
                try:
                    logger.info(f"📤 Posting to {post['platform']}...")
                    
                    success = await self.social_manager.post_content(
                        platform=post["platform"],
                        content=post["content"]
                    )
                    
                    if success:
                        post["posted"] = True
                        # Track in analytics
                        await self.analytics.record_post(
                            platform=post["platform"],
                            content_id=post["content"].get("id"),
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
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 Shutting down...")
        self.running = False
        
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
