"""
Viral Intelligence Optimizer - Uses viral content data to optimize AI strategy
Analyzes patterns and trends to improve content performance
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter
import json

from core.logger import setup_logger
from core.config import Config
from core.database import Database

logger = setup_logger(__name__)

class ViralIntelligenceOptimizer:
    """Optimizes content strategy based on viral content analysis"""
    
    def __init__(self, config: Config, database: Database):
        self.config = config
        self.db = database
        self.openai_key = config.get("api_keys.openai")
    
    async def analyze_and_optimize(
        self,
        current_strategy: Dict,
        platforms: List[str] = ["instagram", "tiktok", "twitter"]
    ) -> Dict:
        """
        Analyze viral content and generate optimization recommendations
        
        Args:
            current_strategy: Current marketing strategy
            platforms: Platforms to analyze
        
        Returns:
            Optimized strategy with recommendations
        """
        logger.info("🔍 Analyzing viral content for strategy optimization...")
        
        # Get viral content data
        viral_data = await self._gather_viral_data(platforms)
        
        # Analyze patterns
        patterns = await self._analyze_patterns(viral_data)
        
        # Generate insights with AI
        insights = await self._generate_ai_insights(patterns, current_strategy)
        
        # Create optimized strategy
        optimized_strategy = await self._create_optimized_strategy(
            current_strategy,
            patterns,
            insights
        )
        
        # Save insights to database
        for insight in insights:
            self.db.save_content_insight(insight)
        
        logger.info("✅ Strategy optimization complete")
        return optimized_strategy
    
    async def _gather_viral_data(self, platforms: List[str]) -> Dict:
        """Gather viral content data from database"""
        data = {
            "content": [],
            "hashtags": [],
            "stats": {}
        }
        
        for platform in platforms:
            # Get top viral content
            viral_content = self.db.get_top_viral_content(platform=platform, limit=50)
            data["content"].extend(viral_content)
            
            # Get trending hashtags
            trending_tags = self.db.get_trending_hashtags(platform=platform, limit=30)
            data["hashtags"].extend(trending_tags)
            
            # Get platform stats
            stats = self.db.get_viral_content_stats(days=7)
            data["stats"][platform] = stats.get(platform, {})
        
        logger.info(f"📊 Gathered {len(data['content'])} viral posts, {len(data['hashtags'])} trending hashtags")
        return data
    
    async def _analyze_patterns(self, viral_data: Dict) -> Dict:
        """Analyze patterns in viral content"""
        logger.info("🔬 Analyzing viral content patterns...")
        
        patterns = {
            "content_types": self._analyze_content_types(viral_data["content"]),
            "optimal_timing": self._analyze_posting_times(viral_data["content"]),
            "hashtag_patterns": self._analyze_hashtag_patterns(viral_data["hashtags"]),
            "caption_length": self._analyze_caption_length(viral_data["content"]),
            "engagement_drivers": self._identify_engagement_drivers(viral_data["content"]),
            "trending_topics": self._extract_trending_topics(viral_data["content"]),
            "platform_performance": self._analyze_platform_performance(viral_data["stats"])
        }
        
        logger.info("✅ Pattern analysis complete")
        return patterns
    
    def _analyze_content_types(self, content: List[Dict]) -> Dict:
        """Analyze which content types perform best"""
        type_performance = {}
        
        for item in content:
            content_type = item.get("content_type", item.get("type", "unknown"))
            if content_type not in type_performance:
                type_performance[content_type] = {
                    "count": 0,
                    "total_engagement": 0,
                    "avg_engagement": 0
                }
            
            type_performance[content_type]["count"] += 1
            type_performance[content_type]["total_engagement"] += item.get("engagement_rate", 0)
        
        # Calculate averages
        for ctype in type_performance:
            count = type_performance[ctype]["count"]
            if count > 0:
                type_performance[ctype]["avg_engagement"] = \
                    type_performance[ctype]["total_engagement"] / count
        
        # Sort by average engagement
        sorted_types = sorted(
            type_performance.items(),
            key=lambda x: x[1]["avg_engagement"],
            reverse=True
        )
        
        return {
            "performance": dict(sorted_types),
            "top_type": sorted_types[0][0] if sorted_types else "video",
            "recommendation": self._get_content_type_recommendation(sorted_types)
        }
    
    def _analyze_posting_times(self, content: List[Dict]) -> Dict:
        """Analyze optimal posting times"""
        hourly_performance = {}
        
        for item in content:
            if item.get("posted_at"):
                try:
                    posted_time = datetime.fromisoformat(item["posted_at"].replace('Z', '+00:00'))
                    hour = posted_time.hour
                    
                    if hour not in hourly_performance:
                        hourly_performance[hour] = {
                            "count": 0,
                            "total_engagement": 0
                        }
                    
                    hourly_performance[hour]["count"] += 1
                    hourly_performance[hour]["total_engagement"] += item.get("engagement_rate", 0)
                except:
                    continue
        
        # Calculate average engagement per hour
        for hour in hourly_performance:
            count = hourly_performance[hour]["count"]
            if count > 0:
                hourly_performance[hour]["avg_engagement"] = \
                    hourly_performance[hour]["total_engagement"] / count
        
        # Get top 3 hours
        sorted_hours = sorted(
            hourly_performance.items(),
            key=lambda x: x[1].get("avg_engagement", 0),
            reverse=True
        )
        
        top_hours = [f"{hour:02d}:00" for hour, _ in sorted_hours[:3]]
        
        return {
            "hourly_performance": hourly_performance,
            "top_posting_times": top_hours,
            "recommendation": f"Post at {', '.join(top_hours)} for maximum engagement"
        }
    
    def _analyze_hashtag_patterns(self, hashtags: List[Dict]) -> Dict:
        """Analyze hashtag patterns"""
        # Get top hashtags by usage
        top_by_usage = sorted(hashtags, key=lambda x: x.get("usage_count", 0), reverse=True)[:10]
        
        # Get top hashtags by engagement
        top_by_engagement = sorted(hashtags, key=lambda x: x.get("avg_engagement_rate", 0), reverse=True)[:10]
        
        # Get hashtags that appear in both lists (sweet spot)
        sweet_spot = []
        usage_tags = set(h["hashtag"] for h in top_by_usage)
        engagement_tags = set(h["hashtag"] for h in top_by_engagement)
        sweet_spot_tags = usage_tags.intersection(engagement_tags)
        
        for hashtag in hashtags:
            if hashtag["hashtag"] in sweet_spot_tags:
                sweet_spot.append(hashtag)
        
        return {
            "top_by_usage": [h["hashtag"] for h in top_by_usage],
            "top_by_engagement": [h["hashtag"] for h in top_by_engagement],
            "sweet_spot": [h["hashtag"] for h in sweet_spot],
            "recommendation": f"Use hashtags: {', '.join(['#' + h['hashtag'] for h in sweet_spot[:5]])}"
        }
    
    def _analyze_caption_length(self, content: List[Dict]) -> Dict:
        """Analyze optimal caption length"""
        length_buckets = {
            "short": {"range": (0, 100), "engagement": [], "count": 0},
            "medium": {"range": (100, 300), "engagement": [], "count": 0},
            "long": {"range": (300, 1000), "engagement": [], "count": 0}
        }
        
        for item in content:
            caption = item.get("caption", "")
            length = len(caption)
            engagement = item.get("engagement_rate", 0)
            
            if length < 100:
                length_buckets["short"]["engagement"].append(engagement)
                length_buckets["short"]["count"] += 1
            elif length < 300:
                length_buckets["medium"]["engagement"].append(engagement)
                length_buckets["medium"]["count"] += 1
            else:
                length_buckets["long"]["engagement"].append(engagement)
                length_buckets["long"]["count"] += 1
        
        # Calculate averages
        for bucket in length_buckets.values():
            if bucket["engagement"]:
                bucket["avg_engagement"] = sum(bucket["engagement"]) / len(bucket["engagement"])
            else:
                bucket["avg_engagement"] = 0
        
        # Find best performing length
        best_bucket = max(length_buckets.items(), key=lambda x: x[1]["avg_engagement"])
        
        return {
            "performance_by_length": length_buckets,
            "optimal_length": best_bucket[0],
            "recommendation": f"Use {best_bucket[0]} captions ({best_bucket[1]['range'][0]}-{best_bucket[1]['range'][1]} chars)"
        }
    
    def _identify_engagement_drivers(self, content: List[Dict]) -> Dict:
        """Identify what drives engagement"""
        drivers = {
            "has_call_to_action": {"yes": [], "no": []},
            "uses_emojis": {"yes": [], "no": []},
            "asks_question": {"yes": [], "no": []}
        }
        
        for item in content:
            caption = item.get("caption", "").lower()
            engagement = item.get("engagement_rate", 0)
            
            # Check for CTAs
            has_cta = any(word in caption for word in ["click", "link", "bio", "comment", "share", "tag"])
            drivers["has_call_to_action"]["yes" if has_cta else "no"].append(engagement)
            
            # Check for emojis (simplified check)
            has_emojis = any(ord(char) > 127 for char in caption)
            drivers["uses_emojis"]["yes" if has_emojis else "no"].append(engagement)
            
            # Check for questions
            has_question = "?" in caption
            drivers["asks_question"]["yes" if has_question else "no"].append(engagement)
        
        # Calculate impact
        impact = {}
        for driver, values in drivers.items():
            yes_avg = sum(values["yes"]) / len(values["yes"]) if values["yes"] else 0
            no_avg = sum(values["no"]) / len(values["no"]) if values["no"] else 0
            impact[driver] = {
                "with": yes_avg,
                "without": no_avg,
                "impact": yes_avg - no_avg,
                "recommendation": "Include" if yes_avg > no_avg else "Optional"
            }
        
        return impact
    
    def _extract_trending_topics(self, content: List[Dict]) -> List[str]:
        """Extract trending topics from captions"""
        all_words = []
        
        for item in content:
            caption = item.get("caption", "")
            # Simple word extraction (could be enhanced with NLP)
            words = [w.lower() for w in caption.split() if len(w) > 4 and not w.startswith("#")]
            all_words.extend(words)
        
        # Get most common words
        word_counts = Counter(all_words)
        trending = [word for word, count in word_counts.most_common(20) if count > 5]
        
        return trending
    
    def _analyze_platform_performance(self, stats: Dict) -> Dict:
        """Analyze which platforms perform best"""
        return {
            "stats": stats,
            "top_platform": max(stats.items(), key=lambda x: x[1].get("avg_engagement", 0))[0] if stats else "instagram",
            "recommendation": "Focus more content on top-performing platforms"
        }
    
    def _get_content_type_recommendation(self, sorted_types: List) -> str:
        """Generate content type recommendation"""
        if not sorted_types:
            return "Create varied content types"
        
        top_type = sorted_types[0][0]
        top_engagement = sorted_types[0][1]["avg_engagement"]
        
        if top_engagement > 10:
            return f"Focus heavily on {top_type} content (very high engagement)"
        elif top_engagement > 5:
            return f"Prioritize {top_type} content (strong engagement)"
        else:
            return f"Include more {top_type} content in mix"
    
    async def _generate_ai_insights(self, patterns: Dict, current_strategy: Dict) -> List[Dict]:
        """Generate AI-powered insights from patterns"""
        if not self.openai_key:
            logger.warning("⚠️ OpenAI key not available, using rule-based insights")
            return self._generate_rule_based_insights(patterns)
        
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.openai_key)
            
            prompt = f"""Analyze this viral content data and provide 5 actionable insights:

PATTERNS DETECTED:
- Top Content Type: {patterns['content_types']['top_type']}
- Best Posting Times: {', '.join(patterns['optimal_timing']['top_posting_times'])}
- Trending Hashtags: {', '.join(patterns['hashtag_patterns']['sweet_spot'][:5])}
- Optimal Caption Length: {patterns['caption_length']['optimal_length']}
- Trending Topics: {', '.join(patterns['trending_topics'][:10])}

CURRENT STRATEGY:
- Niche: {current_strategy.get('niche', 'lifestyle')}
- Target Audience: {current_strategy.get('target_audience', 'general')}
- Current Themes: {', '.join(current_strategy.get('content_plan', {}).get('themes', []))}

Provide 5 specific, actionable insights with confidence scores (0-1) in JSON format:
[{{"type": "content_type", "pattern": "description", "confidence": 0.9, "recommendation": "specific action"}}]
"""
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a social media strategy expert analyzing viral content patterns."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            insights_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON
            try:
                insights = json.loads(insights_text)
                return insights
            except:
                # Fallback to rule-based
                return self._generate_rule_based_insights(patterns)
            
        except Exception as e:
            logger.error(f"AI insight generation failed: {e}")
            return self._generate_rule_based_insights(patterns)
    
    def _generate_rule_based_insights(self, patterns: Dict) -> List[Dict]:
        """Generate insights using rules"""
        insights = []
        
        # Content type insight
        insights.append({
            "type": "content_type",
            "platform": "all",
            "niche": None,
            "pattern": f"'{patterns['content_types']['top_type']}' content performs best",
            "confidence": 0.8,
            "recommendation": patterns['content_types']['recommendation']
        })
        
        # Posting time insight
        insights.append({
            "type": "timing",
            "platform": "all",
            "niche": None,
            "pattern": "Optimal posting times identified",
            "confidence": 0.75,
            "recommendation": patterns['optimal_timing']['recommendation']
        })
        
        # Hashtag insight
        insights.append({
            "type": "hashtags",
            "platform": "all",
            "niche": None,
            "pattern": "High-performing hashtags identified",
            "confidence": 0.85,
            "recommendation": patterns['hashtag_patterns']['recommendation']
        })
        
        # Caption length insight
        insights.append({
            "type": "caption",
            "platform": "all",
            "niche": None,
            "pattern": f"'{patterns['caption_length']['optimal_length']}' captions drive more engagement",
            "confidence": 0.7,
            "recommendation": patterns['caption_length']['recommendation']
        })
        
        # Engagement driver insight
        top_driver = max(
            patterns['engagement_drivers'].items(),
            key=lambda x: x[1]["impact"]
        )
        insights.append({
            "type": "engagement",
            "platform": "all",
            "niche": None,
            "pattern": f"Content with '{top_driver[0]}' shows {top_driver[1]['impact']:.1f}% higher engagement",
            "confidence": 0.8,
            "recommendation": f"{top_driver[1]['recommendation']} {top_driver[0].replace('_', ' ')}"
        })
        
        return insights
    
    async def _create_optimized_strategy(
        self,
        current_strategy: Dict,
        patterns: Dict,
        insights: List[Dict]
    ) -> Dict:
        """Create optimized strategy based on insights"""
        logger.info("🎯 Creating optimized strategy...")
        
        optimized = current_strategy.copy()
        
        # Update content plan
        if "content_plan" not in optimized:
            optimized["content_plan"] = {}
        
        # Update content mix based on viral patterns
        top_type = patterns["content_types"]["top_type"]
        optimized["content_plan"]["content_mix"] = self._optimize_content_mix(top_type)
        
        # Update posting times
        optimized["platforms"] = optimized.get("platforms", {})
        for platform in ["instagram", "twitter", "tiktok"]:
            if platform not in optimized["platforms"]:
                optimized["platforms"][platform] = {}
            
            optimized["platforms"][platform]["optimal_times"] = patterns["optimal_timing"]["top_posting_times"]
        
        # Update hashtag strategy
        optimized["hashtag_strategy"] = {
            "recommended_hashtags": patterns["hashtag_patterns"]["sweet_spot"][:15],
            "count_per_platform": {
                "instagram": 20,
                "twitter": 5,
                "tiktok": 10
            }
        }
        
        # Update themes based on trending topics
        trending_topics = patterns["trending_topics"][:5]
        current_themes = optimized.get("content_plan", {}).get("themes", [])
        
        # Merge trending with current, prioritizing trending
        updated_themes = trending_topics + [t for t in current_themes if t not in trending_topics]
        optimized["content_plan"]["themes"] = updated_themes[:7]
        
        # Add optimization metadata
        optimized["optimized_at"] = datetime.now().isoformat()
        optimized["optimization_source"] = "viral_intelligence"
        optimized["insights_applied"] = len(insights)
        optimized["confidence_score"] = sum(i.get("confidence", 0) for i in insights) / len(insights)
        
        logger.info("✅ Optimized strategy created")
        return optimized
    
    def _optimize_content_mix(self, top_type: str) -> Dict:
        """Optimize content mix based on top performing type"""
        # Give more weight to top performing type
        if top_type == "video" or top_type == "reel":
            return {"video": 0.5, "carousel": 0.3, "image": 0.2}
        elif top_type == "carousel":
            return {"carousel": 0.5, "video": 0.3, "image": 0.2}
        else:
            return {"image": 0.4, "video": 0.3, "carousel": 0.3}
    
    async def get_content_recommendations(self, niche: str, platform: str) -> List[str]:
        """Get specific content recommendations"""
        # Get recent insights
        insights = self.db.get_content_insights(platform=platform, niche=niche, limit=10)
        
        recommendations = []
        for insight in insights:
            if insight.get("recommendation"):
                recommendations.append(insight["recommendation"])
        
        # Add pattern-based recommendations
        viral_content = self.db.get_top_viral_content(platform=platform, limit=20)
        
        if viral_content:
            # Analyze and add recommendations
            trending_hashtags = self.db.get_trending_hashtags(platform=platform, limit=10)
            if trending_hashtags:
                tags = ", ".join([f"#{h['hashtag']}" for h in trending_hashtags[:5]])
                recommendations.append(f"Use trending hashtags: {tags}")
        
        return recommendations
