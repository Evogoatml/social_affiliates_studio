"""
Analytics Engine - Tracks performance and provides insights
"""

import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json

from core.logger import setup_logger
from core.config import Config

logger = setup_logger(__name__)

class AnalyticsEngine:
    """Tracks and analyzes social media performance"""
    
    def __init__(self, config: Config):
        self.config = config
        self.analytics_dir = Path("data/analytics")
        self.analytics_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_file = self.analytics_dir / "metrics.json"
        self.metrics = self._load_metrics()
    
    def _load_metrics(self) -> Dict:
        """Load existing metrics"""
        if self.metrics_file.exists():
            with open(self.metrics_file, "r") as f:
                return json.load(f)
        return {
            "posts": [],
            "engagement": {},
            "growth": {},
            "insights": {}
        }
    
    async def record_post(self, platform: str, content_id: str, timestamp: datetime):
        """Record a post"""
        post_record = {
            "platform": platform,
            "content_id": content_id,
            "timestamp": timestamp.isoformat(),
            "engagement": {
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "views": 0
            }
        }
        
        self.metrics["posts"].append(post_record)
        await self._save_metrics()
    
    async def update_engagement(self, content_id: str, platform: str, engagement: Dict):
        """Update engagement metrics for a post"""
        for post in self.metrics["posts"]:
            if post["content_id"] == content_id and post["platform"] == platform:
                post["engagement"].update(engagement)
                break
        
        await self._save_metrics()
    
    async def get_insights(self) -> Optional[Dict]:
        """Get analytics insights"""
        logger.info("📊 Generating insights...")
        
        if not self.metrics["posts"]:
            return None
        
        # Calculate engagement rates
        engagement_rates = self._calculate_engagement_rates()
        
        # Identify top performing content
        top_performing = self._get_top_performing_content()
        
        # Identify low performing content
        low_performing = self._get_low_performing_content()
        
        # Best posting times
        best_times = self._analyze_posting_times()
        
        # Growth trends
        growth = self._analyze_growth()
        
        insights = {
            "engagement_rates": engagement_rates,
            "top_performing_content": top_performing,
            "low_performing_content": low_performing,
            "best_posting_times": best_times,
            "growth": growth,
            "generated_at": datetime.now().isoformat()
        }
        
        self.metrics["insights"] = insights
        await self._save_metrics()
        
        return insights
    
    def _calculate_engagement_rates(self) -> Dict:
        """Calculate engagement rates by platform and content type"""
        rates = {}
        
        for post in self.metrics["posts"]:
            platform = post["platform"]
            if platform not in rates:
                rates[platform] = {
                    "total_posts": 0,
                    "total_engagement": 0,
                    "average_engagement": 0
                }
            
            engagement = post.get("engagement", {})
            total_engagement = (
                engagement.get("likes", 0) +
                engagement.get("comments", 0) * 2 +  # Comments weighted more
                engagement.get("shares", 0) * 3       # Shares weighted most
            )
            
            rates[platform]["total_posts"] += 1
            rates[platform]["total_engagement"] += total_engagement
        
        # Calculate averages
        for platform in rates:
            if rates[platform]["total_posts"] > 0:
                rates[platform]["average_engagement"] = (
                    rates[platform]["total_engagement"] / rates[platform]["total_posts"]
                )
        
        return rates
    
    def _get_top_performing_content(self, limit: int = 5) -> List[Dict]:
        """Get top performing content"""
        posts_with_scores = []
        
        for post in self.metrics["posts"]:
            engagement = post.get("engagement", {})
            score = (
                engagement.get("likes", 0) +
                engagement.get("comments", 0) * 2 +
                engagement.get("shares", 0) * 3 +
                engagement.get("views", 0) * 0.1
            )
            
            posts_with_scores.append({
                **post,
                "score": score
            })
        
        # Sort by score and return top
        posts_with_scores.sort(key=lambda x: x["score"], reverse=True)
        return posts_with_scores[:limit]
    
    def _get_low_performing_content(self, limit: int = 5) -> List[Dict]:
        """Get low performing content"""
        posts_with_scores = []
        
        for post in self.metrics["posts"]:
            engagement = post.get("engagement", {})
            score = (
                engagement.get("likes", 0) +
                engagement.get("comments", 0) * 2 +
                engagement.get("shares", 0) * 3
            )
            
            posts_with_scores.append({
                **post,
                "score": score
            })
        
        # Sort by score and return bottom
        posts_with_scores.sort(key=lambda x: x["score"])
        return posts_with_scores[:limit]
    
    def _analyze_posting_times(self) -> Dict:
        """Analyze best posting times"""
        time_performance = {}
        
        for post in self.metrics["posts"]:
            timestamp = datetime.fromisoformat(post["timestamp"])
            hour = timestamp.hour
            platform = post["platform"]
            
            key = f"{platform}_{hour}"
            if key not in time_performance:
                time_performance[key] = {
                    "posts": 0,
                    "total_engagement": 0
                }
            
            engagement = post.get("engagement", {})
            total = (
                engagement.get("likes", 0) +
                engagement.get("comments", 0) * 2 +
                engagement.get("shares", 0) * 3
            )
            
            time_performance[key]["posts"] += 1
            time_performance[key]["total_engagement"] += total
        
        # Find best times per platform
        best_times = {}
        for platform in ["instagram", "twitter", "tiktok"]:
            platform_times = {
                k.split("_")[1]: v["total_engagement"] / max(v["posts"], 1)
                for k, v in time_performance.items()
                if k.startswith(platform)
            }
            
            if platform_times:
                # Get top 3 hours
                sorted_times = sorted(platform_times.items(), key=lambda x: x[1], reverse=True)
                best_times[platform] = [f"{int(h):02d}:00" for h, _ in sorted_times[:3]]
        
        return best_times
    
    def _analyze_growth(self) -> Dict:
        """Analyze growth trends"""
        # This would integrate with platform APIs to get follower counts
        # For now, return placeholder
        return {
            "follower_growth": "tracking...",
            "engagement_growth": "tracking...",
            "reach_growth": "tracking..."
        }
    
    async def _save_metrics(self):
        """Save metrics to file"""
        with open(self.metrics_file, "w") as f:
            json.dump(self.metrics, f, indent=2)
