"""
Marketing Strategy Planner - Autonomous marketing strategy creation and optimization
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import json

from core.logger import setup_logger
from core.config import Config

logger = setup_logger(__name__)

class MarketingStrategyPlanner:
    """Creates and optimizes marketing strategies autonomously"""
    
    def __init__(self, config: Config):
        self.config = config
        self.strategy_dir = Path("data/strategies")
        self.strategy_dir.mkdir(parents=True, exist_ok=True)
    
    async def create_strategy(
        self,
        goals: List[str],
        niche: str,
        target_audience: str
    ) -> Dict:
        """Create a comprehensive marketing strategy"""
        logger.info(f"📊 Creating strategy for niche: {niche}, audience: {target_audience}")
        
        openai_key = self.config.get("api_keys.openai")
        
        if openai_key:
            strategy = await self._create_ai_strategy(goals, niche, target_audience)
        else:
            strategy = await self._create_template_strategy(goals, niche, target_audience)
        
        # Add metadata
        strategy["id"] = f"strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        strategy["created_at"] = datetime.now().isoformat()
        strategy["goals"] = goals
        strategy["niche"] = niche
        strategy["target_audience"] = target_audience
        
        # Save strategy
        await self._save_strategy(strategy)
        
        logger.info(f"✅ Strategy created: {strategy.get('name', 'Unknown')}")
        return strategy
    
    async def _create_ai_strategy(
        self,
        goals: List[str],
        niche: str,
        target_audience: str
    ) -> Dict:
        """Create strategy using AI"""
        try:
            from openai import OpenAI
            
            openai_key = self.config.get("api_keys.openai")
            client = OpenAI(api_key=openai_key)
            
            prompt = f"""Create a comprehensive social media marketing strategy for an influencer.

Goals: {', '.join(goals)}
Niche: {niche}
Target Audience: {target_audience}

Provide a detailed strategy including:
1. Content themes and topics
2. Posting schedule recommendations
3. Engagement tactics
4. Growth strategies
5. Platform-specific approaches
6. Content mix (videos, images, carousels)
7. Hashtag strategy
8. Collaboration opportunities

Format as JSON with clear structure."""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert social media marketing strategist."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            strategy_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON from response
            try:
                strategy = json.loads(strategy_text)
            except:
                # If not valid JSON, create structure from text
                strategy = self._parse_strategy_from_text(strategy_text, goals, niche, target_audience)
            
            return strategy
            
        except Exception as e:
            logger.warning(f"AI strategy generation failed: {e}")
            return await self._create_template_strategy(goals, niche, target_audience)
    
    def _parse_strategy_from_text(
        self,
        text: str,
        goals: List[str],
        niche: str,
        target_audience: str
    ) -> Dict:
        """Parse strategy from AI text response"""
        return {
            "name": f"{niche.title()} Influencer Strategy",
            "content_plan": {
                "themes": ["motivation", "lifestyle", "tips", "behind-the-scenes"],
                "topics": self._extract_topics_from_text(text),
                "posting_frequency": "daily",
                "content_mix": {
                    "video": 0.3,
                    "carousel": 0.4,
                    "image": 0.3
                }
            },
            "engagement_tactics": [
                "Respond to all comments",
                "Ask questions in captions",
                "Use polls and stories",
                "Collaborate with similar accounts"
            ],
            "growth_strategies": [
                "Consistent posting schedule",
                "Engage with niche community",
                "Use trending hashtags",
                "Cross-platform promotion"
            ],
            "platforms": {
                "instagram": {"focus": "visual content", "stories": True},
                "twitter": {"focus": "quick tips", "threads": True},
                "tiktok": {"focus": "short videos", "trending_sounds": True}
            },
            "tone": "friendly, professional, authentic"
        }
    
    def _extract_topics_from_text(self, text: str) -> List[str]:
        """Extract topics from text (simple implementation)"""
        # This is a simplified version - could be enhanced with NLP
        keywords = ["motivation", "lifestyle", "tips", "productivity", "wellness", 
                   "fitness", "mindset", "goals", "success", "inspiration"]
        found = [kw for kw in keywords if kw.lower() in text.lower()]
        return found[:10] if found else ["general", "lifestyle", "tips"]
    
    async def _create_template_strategy(
        self,
        goals: List[str],
        niche: str,
        target_audience: str
    ) -> Dict:
        """Create strategy from template"""
        return {
            "name": f"{niche.title()} Influencer Strategy",
            "content_plan": {
                "themes": ["motivation", "lifestyle", "tips", "behind-the-scenes"],
                "topics": self._get_topics_for_niche(niche),
                "posting_frequency": "daily",
                "content_mix": {
                    "video": 0.3,
                    "carousel": 0.4,
                    "image": 0.3
                }
            },
            "engagement_tactics": [
                "Respond to all comments within 24 hours",
                "Ask engaging questions in captions",
                "Use Instagram Stories polls and questions",
                "Collaborate with accounts in similar niche",
                "Engage with followers' content"
            ],
            "growth_strategies": [
                "Post consistently at optimal times",
                "Engage with niche community hashtags",
                "Use mix of trending and niche-specific hashtags",
                "Cross-promote across platforms",
                "Create shareable, valuable content"
            ],
            "platforms": {
                "instagram": {
                    "focus": "high-quality visual content",
                    "stories": True,
                    "reels": True,
                    "optimal_times": ["09:00", "18:00"]
                },
                "twitter": {
                    "focus": "quick tips and engagement",
                    "threads": True,
                    "optimal_times": ["08:00", "12:00", "20:00"]
                },
                "tiktok": {
                    "focus": "trending short-form videos",
                    "trending_sounds": True,
                    "optimal_times": ["19:00"]
                }
            },
            "hashtag_strategy": {
                "mix": "70% niche-specific, 30% trending",
                "count_per_platform": {
                    "instagram": 20,
                    "twitter": 5,
                    "tiktok": 10
                }
            },
            "tone": "friendly, professional, authentic, relatable",
            "cta_strategy": "Include soft CTAs in every post"
        }
    
    def _get_topics_for_niche(self, niche: str) -> List[str]:
        """Get topics based on niche"""
        niche_topics = {
            "lifestyle": ["daily routines", "self-care", "productivity", "wellness", "mindfulness"],
            "fitness": ["workouts", "nutrition", "motivation", "transformation", "tips"],
            "tech": ["gadgets", "apps", "tips", "reviews", "tutorials"],
            "business": ["entrepreneurship", "productivity", "tips", "motivation", "success"],
            "fashion": ["outfits", "styling", "trends", "tips", "inspiration"],
            "food": ["recipes", "cooking", "restaurants", "tips", "inspiration"]
        }
        
        return niche_topics.get(niche.lower(), ["tips", "lifestyle", "motivation", "daily"])
    
    async def optimize_strategy(self, current_strategy: Dict, insights: Dict) -> Dict:
        """Optimize strategy based on analytics insights"""
        logger.info("🔄 Optimizing strategy based on insights...")
        
        # Analyze what's working
        top_performing = insights.get("top_performing_content", [])
        low_performing = insights.get("low_performing_content", [])
        
        # Adjust content themes
        if top_performing:
            successful_themes = [c.get("theme") for c in top_performing[:3]]
            current_strategy["content_plan"]["themes"] = successful_themes + \
                [t for t in current_strategy["content_plan"]["themes"] if t not in successful_themes]
        
        # Adjust posting times if data available
        best_times = insights.get("best_posting_times", {})
        if best_times:
            for platform, times in best_times.items():
                if platform in current_strategy.get("platforms", {}):
                    current_strategy["platforms"][platform]["optimal_times"] = times
        
        # Update strategy
        current_strategy["optimized_at"] = datetime.now().isoformat()
        current_strategy["optimization_count"] = current_strategy.get("optimization_count", 0) + 1
        
        await self._save_strategy(current_strategy)
        
        logger.info("✅ Strategy optimized")
        return current_strategy
    
    async def _save_strategy(self, strategy: Dict):
        """Save strategy to file"""
        strategy_file = self.strategy_dir / f"{strategy['id']}.json"
        with open(strategy_file, "w") as f:
            json.dump(strategy, f, indent=2)
        
        # Also save as current strategy
        current_file = self.strategy_dir / "current_strategy.json"
        with open(current_file, "w") as f:
            json.dump(strategy, f, indent=2)
