"""
Viral Content Scraper - Scrapes trending content from social media platforms
Analyzes viral posts, reels, and topics to inform AI strategy
"""

import os
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path

from core.logger import setup_logger
from core.config import Config
from core.utils import retry_with_backoff, RateLimiter

logger = setup_logger(__name__)

class ViralContentScraper:
    """Scrapes and analyzes viral content from multiple platforms"""
    
    def __init__(self, config: Config):
        self.config = config
        self.data_dir = Path("data/viral_content")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Rate limiters for each platform
        self.rate_limiters = {
            "instagram": RateLimiter(calls_per_minute=30),
            "tiktok": RateLimiter(calls_per_minute=30),
            "twitter": RateLimiter(calls_per_minute=45)
        }
        
        self.scraped_content = []
    
    async def scrape_trending_content(
        self, 
        platforms: List[str] = ["instagram", "tiktok", "twitter"],
        niche: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Scrape trending content from specified platforms
        
        Args:
            platforms: List of platforms to scrape
            niche: Specific niche to focus on
            limit: Number of trending posts per platform
        
        Returns:
            List of viral content data
        """
        logger.info(f"🔥 Starting viral content scraping for platforms: {platforms}")
        
        all_content = []
        
        for platform in platforms:
            logger.info(f"📱 Scraping {platform.upper()}...")
            
            if platform == "instagram":
                content = await self._scrape_instagram_trending(niche, limit)
            elif platform == "tiktok":
                content = await self._scrape_tiktok_trending(niche, limit)
            elif platform == "twitter":
                content = await self._scrape_twitter_trending(niche, limit)
            else:
                logger.warning(f"⚠️ Unknown platform: {platform}")
                continue
            
            all_content.extend(content)
            logger.info(f"✅ Scraped {len(content)} items from {platform}")
        
        # Save raw data
        await self._save_scraped_content(all_content)
        
        logger.info(f"✅ Total viral content scraped: {len(all_content)}")
        return all_content
    
    @retry_with_backoff(max_retries=3)
    async def _scrape_instagram_trending(self, niche: Optional[str], limit: int) -> List[Dict]:
        """Scrape trending Instagram content"""
        await self.rate_limiters["instagram"].wait()
        
        # Method 1: Using Instaloader (if available)
        try:
            import instaloader
            
            L = instaloader.Instaloader()
            
            # Get trending hashtags for niche
            hashtags = self._get_trending_hashtags(niche or "lifestyle")
            
            content = []
            for hashtag in hashtags[:5]:  # Top 5 hashtags
                try:
                    posts = L.get_hashtag_posts(hashtag)
                    
                    for post in list(posts)[:limit // 5]:
                        content.append({
                            "platform": "instagram",
                            "type": "reel" if post.is_video else "image",
                            "url": f"https://www.instagram.com/p/{post.shortcode}/",
                            "caption": post.caption if post.caption else "",
                            "hashtags": post.caption_hashtags,
                            "likes": post.likes,
                            "comments": post.comments,
                            "engagement_rate": self._calculate_engagement(post.likes, post.comments, 1000),
                            "posted_at": post.date_utc.isoformat(),
                            "scraped_at": datetime.now().isoformat(),
                            "is_viral": post.likes > 10000,
                            "niche": niche or "general"
                        })
                except Exception as e:
                    logger.warning(f"Error scraping hashtag {hashtag}: {e}")
                    continue
            
            return content
            
        except ImportError:
            logger.warning("Instaloader not available, using API method")
            return await self._scrape_instagram_api(niche, limit)
    
    async def _scrape_instagram_api(self, niche: Optional[str], limit: int) -> List[Dict]:
        """Scrape Instagram using official Graph API"""
        api_token = self.config.get("api_keys.instagram")
        
        if not api_token:
            logger.warning("⚠️ Instagram API token not configured")
            return await self._scrape_instagram_simulation(niche, limit)
        
        try:
            import requests
            
            # Get trending hashtags
            hashtags = self._get_trending_hashtags(niche or "lifestyle")
            
            content = []
            for hashtag in hashtags[:3]:
                url = f"https://graph.instagram.com/ig_hashtag_search"
                params = {
                    "user_id": "me",
                    "q": hashtag,
                    "access_token": api_token
                }
                
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    # Process Instagram API response
                    # Note: Actual implementation depends on API access level
                    
            return content
            
        except Exception as e:
            logger.error(f"Instagram API scraping failed: {e}")
            return await self._scrape_instagram_simulation(niche, limit)
    
    async def _scrape_instagram_simulation(self, niche: Optional[str], limit: int) -> List[Dict]:
        """Simulate Instagram scraping with realistic data"""
        logger.info("📊 Simulating Instagram trending content...")
        
        themes = ["fitness", "lifestyle", "motivation", "fashion", "food", "travel"]
        target_theme = niche or "lifestyle"
        
        content = []
        for i in range(limit):
            engagement = self._generate_viral_metrics()
            
            content.append({
                "platform": "instagram",
                "type": "reel" if i % 3 == 0 else "image",
                "url": f"https://www.instagram.com/p/simulated_{i}/",
                "caption": f"Trending {target_theme} content #{i+1}",
                "hashtags": self._get_trending_hashtags(target_theme),
                "likes": engagement["likes"],
                "comments": engagement["comments"],
                "shares": engagement["shares"],
                "views": engagement["views"],
                "engagement_rate": engagement["rate"],
                "posted_at": (datetime.now() - timedelta(hours=i)).isoformat(),
                "scraped_at": datetime.now().isoformat(),
                "is_viral": engagement["likes"] > 50000,
                "niche": target_theme,
                "simulated": True
            })
        
        return content
    
    @retry_with_backoff(max_retries=3)
    async def _scrape_tiktok_trending(self, niche: Optional[str], limit: int) -> List[Dict]:
        """Scrape trending TikTok content"""
        await self.rate_limiters["tiktok"].wait()
        
        # TikTok API integration
        api_key = self.config.get("api_keys.tiktok")
        
        if not api_key:
            logger.warning("⚠️ TikTok API key not configured, using simulation")
            return await self._scrape_tiktok_simulation(niche, limit)
        
        try:
            import requests
            
            # TikTok Research API or TikTok for Business API
            # Note: Requires approved TikTok developer account
            
            url = "https://open.tiktokapis.com/v2/research/video/query/"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Get trending videos
            payload = {
                "query": {
                    "and": [
                        {"field_name": "region_code", "operation": "IN", "field_values": ["US"]},
                        {"field_name": "video_length", "operation": "EQ", "field_values": ["SHORT"]}
                    ]
                },
                "max_count": limit,
                "cursor": 0
            }
            
            # Note: This is a placeholder - actual implementation depends on API access
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                # Process TikTok API response
                return self._process_tiktok_data(data)
            
        except Exception as e:
            logger.error(f"TikTok API scraping failed: {e}")
        
        return await self._scrape_tiktok_simulation(niche, limit)
    
    async def _scrape_tiktok_simulation(self, niche: Optional[str], limit: int) -> List[Dict]:
        """Simulate TikTok trending content"""
        logger.info("📊 Simulating TikTok trending content...")
        
        target_theme = niche or "lifestyle"
        
        content = []
        for i in range(limit):
            engagement = self._generate_viral_metrics(platform="tiktok")
            
            content.append({
                "platform": "tiktok",
                "type": "video",
                "url": f"https://www.tiktok.com/@user/video/simulated_{i}",
                "caption": f"Trending {target_theme} TikTok #{i+1}",
                "hashtags": self._get_trending_hashtags(target_theme),
                "likes": engagement["likes"],
                "comments": engagement["comments"],
                "shares": engagement["shares"],
                "views": engagement["views"],
                "engagement_rate": engagement["rate"],
                "sound_name": f"Trending Sound {i % 10}",
                "posted_at": (datetime.now() - timedelta(hours=i)).isoformat(),
                "scraped_at": datetime.now().isoformat(),
                "is_viral": engagement["views"] > 1000000,
                "niche": target_theme,
                "simulated": True
            })
        
        return content
    
    @retry_with_backoff(max_retries=3)
    async def _scrape_twitter_trending(self, niche: Optional[str], limit: int) -> List[Dict]:
        """Scrape trending Twitter content"""
        await self.rate_limiters["twitter"].wait()
        
        api_key = self.config.get("api_keys.twitter")
        
        if not api_key:
            logger.warning("⚠️ Twitter API key not configured, using simulation")
            return await self._scrape_twitter_simulation(niche, limit)
        
        try:
            import requests
            
            # Twitter API v2
            url = "https://api.twitter.com/2/tweets/search/recent"
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            
            # Search for trending tweets in niche
            keywords = self._get_trending_hashtags(niche or "lifestyle")
            query = " OR ".join([f"#{tag}" for tag in keywords[:3]])
            
            params = {
                "query": f"{query} -is:retweet has:media",
                "max_results": min(limit, 100),
                "tweet.fields": "public_metrics,created_at,entities",
                "expansions": "author_id",
                "sort_order": "relevancy"
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return self._process_twitter_data(data, niche)
            
        except Exception as e:
            logger.error(f"Twitter API scraping failed: {e}")
        
        return await self._scrape_twitter_simulation(niche, limit)
    
    async def _scrape_twitter_simulation(self, niche: Optional[str], limit: int) -> List[Dict]:
        """Simulate Twitter trending content"""
        logger.info("📊 Simulating Twitter trending content...")
        
        target_theme = niche or "lifestyle"
        
        content = []
        for i in range(limit):
            engagement = self._generate_viral_metrics(platform="twitter")
            
            content.append({
                "platform": "twitter",
                "type": "tweet",
                "url": f"https://twitter.com/user/status/simulated_{i}",
                "caption": f"Trending {target_theme} tweet #{i+1}",
                "hashtags": self._get_trending_hashtags(target_theme),
                "likes": engagement["likes"],
                "comments": engagement["comments"],
                "retweets": engagement["shares"],
                "views": engagement["views"],
                "engagement_rate": engagement["rate"],
                "posted_at": (datetime.now() - timedelta(hours=i)).isoformat(),
                "scraped_at": datetime.now().isoformat(),
                "is_viral": engagement["likes"] > 10000,
                "niche": target_theme,
                "simulated": True
            })
        
        return content
    
    def _get_trending_hashtags(self, niche: str) -> List[str]:
        """Get trending hashtags for a niche"""
        hashtag_map = {
            "lifestyle": ["lifestyle", "dailylife", "motivation", "wellness", "selfcare"],
            "fitness": ["fitness", "workout", "fitnessmotivation", "gym", "health"],
            "fashion": ["fashion", "style", "ootd", "fashionista", "trendy"],
            "food": ["foodie", "food", "instafood", "cooking", "recipe"],
            "travel": ["travel", "wanderlust", "travelgram", "adventure", "explore"],
            "tech": ["tech", "technology", "innovation", "gadgets", "ai"],
            "business": ["business", "entrepreneur", "startup", "success", "motivation"]
        }
        
        return hashtag_map.get(niche.lower(), ["viral", "trending", "fyp", "explore", "popular"])
    
    def _generate_viral_metrics(self, platform: str = "instagram") -> Dict:
        """Generate realistic viral engagement metrics"""
        import random
        
        if platform == "instagram":
            likes = random.randint(50000, 500000)
            comments = int(likes * random.uniform(0.02, 0.05))
            shares = int(likes * random.uniform(0.01, 0.03))
            views = int(likes * random.uniform(5, 10))
        elif platform == "tiktok":
            views = random.randint(1000000, 10000000)
            likes = int(views * random.uniform(0.05, 0.15))
            comments = int(likes * random.uniform(0.05, 0.1))
            shares = int(likes * random.uniform(0.02, 0.05))
        else:  # twitter
            likes = random.randint(10000, 100000)
            comments = int(likes * random.uniform(0.05, 0.1))
            shares = int(likes * random.uniform(0.1, 0.3))
            views = int(likes * random.uniform(10, 20))
        
        engagement_rate = ((likes + comments * 2 + shares * 3) / max(views, 1)) * 100
        
        return {
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "views": views,
            "rate": round(engagement_rate, 2)
        }
    
    def _calculate_engagement(self, likes: int, comments: int, followers: int) -> float:
        """Calculate engagement rate"""
        if followers == 0:
            return 0.0
        return round(((likes + comments * 2) / followers) * 100, 2)
    
    def _process_tiktok_data(self, data: Dict) -> List[Dict]:
        """Process TikTok API response"""
        # Implementation depends on actual API response structure
        return []
    
    def _process_twitter_data(self, data: Dict, niche: Optional[str]) -> List[Dict]:
        """Process Twitter API response"""
        content = []
        
        if "data" in data:
            for tweet in data["data"]:
                metrics = tweet.get("public_metrics", {})
                
                content.append({
                    "platform": "twitter",
                    "type": "tweet",
                    "url": f"https://twitter.com/user/status/{tweet['id']}",
                    "caption": tweet.get("text", ""),
                    "hashtags": self._extract_hashtags(tweet.get("entities", {})),
                    "likes": metrics.get("like_count", 0),
                    "comments": metrics.get("reply_count", 0),
                    "retweets": metrics.get("retweet_count", 0),
                    "views": metrics.get("impression_count", 0),
                    "engagement_rate": self._calculate_engagement(
                        metrics.get("like_count", 0),
                        metrics.get("reply_count", 0),
                        1000
                    ),
                    "posted_at": tweet.get("created_at"),
                    "scraped_at": datetime.now().isoformat(),
                    "is_viral": metrics.get("like_count", 0) > 10000,
                    "niche": niche or "general"
                })
        
        return content
    
    def _extract_hashtags(self, entities: Dict) -> List[str]:
        """Extract hashtags from tweet entities"""
        if "hashtags" in entities:
            return [tag["tag"] for tag in entities["hashtags"]]
        return []
    
    async def _save_scraped_content(self, content: List[Dict]):
        """Save scraped content to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.data_dir / f"viral_content_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(content, f, indent=2)
        
        logger.info(f"💾 Saved {len(content)} items to {filename}")
    
    async def get_top_performing_content(
        self, 
        platform: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """Get top performing viral content"""
        # Load recent scraped content
        files = sorted(self.data_dir.glob("viral_content_*.json"), reverse=True)
        
        all_content = []
        for file in files[:5]:  # Last 5 scrapes
            with open(file) as f:
                data = json.load(f)
                all_content.extend(data)
        
        # Filter by platform if specified
        if platform:
            all_content = [c for c in all_content if c.get("platform") == platform]
        
        # Sort by engagement rate
        sorted_content = sorted(
            all_content,
            key=lambda x: x.get("engagement_rate", 0),
            reverse=True
        )
        
        return sorted_content[:limit]
