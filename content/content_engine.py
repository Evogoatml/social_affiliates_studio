"""
Content Engine - Generates posts, captions, scripts autonomously
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

from core.logger import setup_logger
from core.config import Config
from content.media_generator import MediaGenerator

logger = setup_logger(__name__)

class ContentEngine:
    """Generates content for social media posts"""
    
    def __init__(self, config: Config):
        self.config = config
        self.content_dir = Path("data/content")
        self.content_dir.mkdir(parents=True, exist_ok=True)
        self.content_counter = 0
        self.media_generator = MediaGenerator(config)
    
    async def generate_daily_content(
        self, 
        strategy: Dict, 
        day_offset: int = 0,
        avatar_data: Optional[Dict] = None
    ) -> List[Dict]:
        """Generate content for a specific day"""
        logger.info(f"📝 Generating content for day {day_offset}...")
        
        content_items = []
        
        # Get content themes from strategy
        themes = strategy.get("content_plan", {}).get("themes", ["motivation", "lifestyle"])
        
        # Generate different types of content
        content_types = self.config.get("content.post_frequency", "daily")
        
        # Generate 2-3 posts per day
        for i in range(3):
            theme = themes[i % len(themes)] if themes else "general"
            
            content = await self._generate_single_content(
                theme=theme,
                strategy=strategy,
                day_offset=day_offset,
                post_index=i,
                avatar_data=avatar_data
            )
            
            if content:
                content_items.append(content)
        
        logger.info(f"✅ Generated {len(content_items)} content items")
        return content_items
    
    async def _generate_single_content(
        self,
        theme: str,
        strategy: Dict,
        day_offset: int,
        post_index: int,
        avatar_data: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Generate a single content item"""
        
        # Determine content type
        content_type = self._select_content_type()
        
        # Generate caption
        caption = await self._generate_caption(theme, strategy, content_type)
        
        # Generate hashtags
        hashtags = await self._generate_hashtags(theme, strategy)
        
        # Create content object
        self.content_counter += 1
        content = {
            "id": f"content_{self.content_counter:04d}",
            "type": content_type,
            "theme": theme,
            "caption": caption,
            "hashtags": hashtags,
            "day_offset": day_offset,
            "post_index": post_index,
            "created_at": datetime.now().isoformat(),
            "avatar_data": avatar_data,
            "strategy_id": strategy.get("id", "unknown")
        }
        
        # Generate media description if needed
        if content_type in ["video", "carousel", "image"]:
            content["media_prompt"] = await self._generate_media_prompt(theme, caption, avatar_data)
            
            # Generate actual media
            if content_type == "image":
                media_data = await self.media_generator.generate_image(
                    prompt=content["media_prompt"],
                    content_id=content["id"]
                )
                content["media"] = media_data
            
            elif content_type == "carousel":
                # Generate 3-5 carousel slides
                carousel_prompts = await self._generate_carousel_prompts(theme, caption)
                carousel_images = await self.media_generator.generate_carousel_images(
                    prompts=carousel_prompts,
                    content_id=content["id"]
                )
                content["media"] = {
                    "type": "carousel",
                    "slides": carousel_images
                }
            
            elif content_type == "video":
                video_script = await self.generate_video_script(content)
                video_data = await self.media_generator.generate_video(
                    script=video_script,
                    content_id=content["id"],
                    avatar_data=avatar_data
                )
                content["media"] = video_data
        
        # Save content
        await self._save_content(content)
        
        return content
    
    def _select_content_type(self) -> str:
        """Select content type based on ratios"""
        import random
        
        video_ratio = self.config.get("content.video_ratio", 0.3)
        carousel_ratio = self.config.get("content.carousel_ratio", 0.4)
        
        rand = random.random()
        
        if rand < video_ratio:
            return "video"
        elif rand < video_ratio + carousel_ratio:
            return "carousel"
        else:
            return "image"
    
    async def _generate_caption(self, theme: str, strategy: Dict, content_type: str) -> str:
        """Generate caption using AI"""
        openai_key = self.config.get("api_keys.openai")
        
        if not openai_key:
            # Fallback to template-based generation
            return self._generate_template_caption(theme, content_type)
        
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=openai_key)
            
            prompt = f"""Create an engaging social media caption for a {theme} post.
            
Content type: {content_type}
Target audience: {strategy.get('target_audience', 'general')}
Tone: {strategy.get('tone', 'friendly and professional')}
Platform: Instagram/Twitter/TikTok

Requirements:
- Engaging and authentic
- Include a call-to-action
- 2-4 sentences
- Emoji usage appropriate for the platform
- Relatable and shareable

Caption:"""
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert social media content creator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.8
            )
            
            caption = response.choices[0].message.content.strip()
            return caption
            
        except Exception as e:
            logger.warning(f"AI caption generation failed: {e}")
            return self._generate_template_caption(theme, content_type)
    
    def _generate_template_caption(self, theme: str, content_type: str) -> str:
        """Generate caption from template"""
        templates = {
            "motivation": [
                "💪 Starting the day with purpose! What's your goal today?",
                "🌟 Every small step counts. Keep pushing forward!",
                "✨ You've got this! Remember why you started."
            ],
            "lifestyle": [
                "☕ Simple moments, big happiness. What's making you smile today?",
                "🌿 Living intentionally, one day at a time.",
                "✨ Finding beauty in the everyday."
            ],
            "tips": [
                "💡 Quick tip that changed my routine!",
                "📚 Learning something new every day. Here's what I discovered:",
                "🎯 Game-changer alert! This simple trick..."
            ]
        }
        
        import random
        theme_templates = templates.get(theme, templates["lifestyle"])
        base_caption = random.choice(theme_templates)
        
        # Add CTA
        ctas = ["What do you think?", "Try it and let me know!", "Share your experience below!"]
        return f"{base_caption} {random.choice(ctas)}"
    
    async def _generate_hashtags(self, theme: str, strategy: Dict) -> List[str]:
        """Generate relevant hashtags"""
        openai_key = self.config.get("api_keys.openai")
        
        base_hashtags = {
            "motivation": ["motivation", "inspiration", "mindset", "goals", "success"],
            "lifestyle": ["lifestyle", "daily", "life", "living", "wellness"],
            "tips": ["tips", "advice", "howto", "learn", "productivity"]
        }
        
        hashtags = base_hashtags.get(theme, ["lifestyle", "daily"])
        
        # Add niche-specific hashtags
        niche = strategy.get("niche", "lifestyle")
        hashtags.extend([niche, f"{niche}life", f"{niche}inspo"])
        
        # Add trending/generic
        hashtags.extend(["viral", "fyp", "trending", "explore"])
        
        # Limit to reasonable number
        return hashtags[:20]
    
    async def _generate_media_prompt(
        self, 
        theme: str, 
        caption: str, 
        avatar_data: Optional[Dict]
    ) -> str:
        """Generate prompt for media generation"""
        avatar_desc = ""
        if avatar_data:
            avatar_desc = "featuring the same person from the avatar, "
        
        prompt = f"A {theme} social media post image, {avatar_desc}"
        prompt += f"related to: {caption[:100]}, "
        prompt += "high quality, professional, Instagram-worthy, "
        prompt += "bright and engaging, modern aesthetic"
        
        return prompt
    
    async def _save_content(self, content: Dict):
        """Save content to file"""
        content_file = self.content_dir / f"{content['id']}.json"
        with open(content_file, "w") as f:
            json.dump(content, f, indent=2)
    
    async def _generate_carousel_prompts(self, theme: str, caption: str) -> List[str]:
        """Generate prompts for carousel slides"""
        # Generate 3-5 related prompts for carousel
        base_elements = {
            "motivation": ["success mindset", "goal achievement", "personal growth"],
            "lifestyle": ["daily routine", "wellness habits", "life balance"],
            "tips": ["practical advice", "quick wins", "actionable steps"]
        }
        
        elements = base_elements.get(theme, ["content", "information", "value"])
        
        prompts = []
        for i, element in enumerate(elements[:5]):
            prompt = f"Social media carousel slide {i+1}: {element}, related to {caption[:50]}, "
            prompt += "clean design, modern aesthetic, Instagram-worthy, professional"
            prompts.append(prompt)
        
        return prompts
    
    async def generate_video_script(self, content: Dict) -> Dict:
        """Generate script for video content"""
        script = {
            "hook": f"Hey! {content['caption'][:50]}...",
            "main_content": content['caption'],
            "cta": "Follow for more tips! Like and share if this helped!",
            "duration_estimate": "30-60 seconds",
            "scenes": [
                {"type": "intro", "duration": 5, "description": "Hook the viewer"},
                {"type": "main", "duration": 20, "description": "Main content"},
                {"type": "cta", "duration": 5, "description": "Call to action"}
            ]
        }
        
        return script
