"""
AI Podcast Generator
Generates daily podcast episodes about viral trends and trendsetting strategies
"""

import os
import json
import logging
from datetime import datetime, time
from pathlib import Path
from typing import Dict, List, Optional, Any
import asyncio

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


class PodcastGenerator:
    """
    Generates AI-powered podcast episodes analyzing viral trends
    """
    
    def __init__(self, config: Any, database: Any, viral_intelligence: Any):
        """
        Initialize podcast generator
        
        Args:
            config: System configuration
            database: Database instance
            viral_intelligence: Viral intelligence system
        """
        self.config = config
        self.database = database
        self.viral_intelligence = viral_intelligence
        self.logger = logging.getLogger(__name__)
        
        # Paths
        self.podcasts_dir = Path("data/podcasts")
        self.scripts_dir = self.podcasts_dir / "scripts"
        self.audio_dir = self.podcasts_dir / "audio"
        self.metadata_dir = self.podcasts_dir / "metadata"
        
        # Create directories
        self.podcasts_dir.mkdir(parents=True, exist_ok=True)
        self.scripts_dir.mkdir(exist_ok=True)
        self.audio_dir.mkdir(exist_ok=True)
        self.metadata_dir.mkdir(exist_ok=True)
        
        # OpenAI client for script generation and TTS
        self.client = None
        if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            self.client = OpenAI()
        
        # Podcast configuration
        self.default_duration = 90  # minutes (1.5 hours)
        self.default_schedule = time(21, 0)  # 9 PM
        
        self.logger.info("🎙️ Podcast Generator initialized")
    
    async def generate_daily_podcast(
        self,
        duration_minutes: int = 90,
        topic_focus: Optional[str] = None
    ) -> Dict:
        """
        Generate a complete podcast episode
        
        Args:
            duration_minutes: Target duration in minutes (60-120)
            topic_focus: Optional focus topic
            
        Returns:
            Podcast metadata and file paths
        """
        self.logger.info(f"🎙️ Generating {duration_minutes}-minute podcast episode")
        
        try:
            # Step 1: Gather viral trends data
            viral_data = await self._gather_viral_trends()
            
            # Step 2: Generate podcast script
            script = await self._generate_podcast_script(
                viral_data=viral_data,
                duration_minutes=duration_minutes,
                topic_focus=topic_focus
            )
            
            # Step 3: Generate audio segments
            audio_files = await self._generate_audio(script)
            
            # Step 4: Create metadata
            metadata = self._create_podcast_metadata(
                script=script,
                audio_files=audio_files,
                duration_minutes=duration_minutes
            )
            
            # Step 5: Save everything
            episode_id = self._save_episode(script, metadata)
            
            self.logger.info(f"✅ Podcast episode complete: {episode_id}")
            
            return {
                'success': True,
                'episode_id': episode_id,
                'script_path': str(self.scripts_dir / f"{episode_id}.json"),
                'audio_files': audio_files,
                'metadata': metadata,
                'duration_minutes': duration_minutes
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error generating podcast: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _gather_viral_trends(self) -> Dict:
        """Gather today's viral trends and insights"""
        self.logger.info("📊 Gathering viral trends data...")
        
        # Get viral content from last 24 hours
        viral_posts = self.database.get_viral_content(
            min_engagement=10000,
            limit=50
        )
        
        # Get trending hashtags
        trending_hashtags = self.database.get_trending_hashtags(limit=20)
        
        # Get trending topics
        trending_topics = self.database.get_trending_topics(limit=15)
        
        # Get AI insights
        insights = self.viral_intelligence.get_latest_insights() if self.viral_intelligence else []
        
        return {
            'viral_posts': viral_posts[:20],  # Top 20
            'trending_hashtags': trending_hashtags,
            'trending_topics': trending_topics,
            'ai_insights': insights,
            'date': datetime.now().isoformat()
        }
    
    async def _generate_podcast_script(
        self,
        viral_data: Dict,
        duration_minutes: int,
        topic_focus: Optional[str] = None
    ) -> Dict:
        """
        Generate structured podcast script
        
        Returns:
            Complete podcast script with segments
        """
        self.logger.info("📝 Generating podcast script...")
        
        if not self.client:
            return self._generate_fallback_script(viral_data, duration_minutes)
        
        # Build context from viral data
        context = self._build_script_context(viral_data)
        
        # Create prompt for GPT-4
        prompt = self._create_script_prompt(
            context=context,
            duration_minutes=duration_minutes,
            topic_focus=topic_focus
        )
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert podcast host and trendsetting influencer. 
                        Create engaging, insightful podcast scripts that analyze viral content, 
                        discuss trendsetting strategies, and provide actionable advice for content creators.
                        Your tone is enthusiastic, knowledgeable, and conversational."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                max_tokens=8000
            )
            
            script_content = response.choices[0].message.content
            
            # Parse script into structured format
            script = self._parse_script(script_content, duration_minutes)
            
            return script
            
        except Exception as e:
            self.logger.error(f"❌ Error generating script with AI: {e}")
            return self._generate_fallback_script(viral_data, duration_minutes)
    
    def _create_script_prompt(
        self,
        context: str,
        duration_minutes: int,
        topic_focus: Optional[str] = None
    ) -> str:
        """Create prompt for script generation"""
        
        focus_text = f"\n\nSpecial focus topic: {topic_focus}" if topic_focus else ""
        
        return f"""Create a {duration_minutes}-minute podcast episode script analyzing today's viral trends.

VIRAL CONTENT DATA:
{context}
{focus_text}

PODCAST STRUCTURE (return as JSON):
{{
    "title": "Episode title",
    "subtitle": "Episode subtitle",
    "segments": [
        {{
            "segment_number": 1,
            "title": "Intro & Welcome",
            "duration_minutes": 5,
            "content": "Full script for this segment...",
            "key_points": ["point 1", "point 2"],
            "voice_notes": "enthusiastic, welcoming tone"
        }},
        {{
            "segment_number": 2,
            "title": "Today's Viral Breakdown",
            "duration_minutes": 20,
            "content": "Analyze top 5 viral posts...",
            "examples": ["specific examples from data"],
            "key_points": ["why it went viral", "lessons learned"],
            "voice_notes": "analytical, insightful"
        }},
        {{
            "segment_number": 3,
            "title": "Trending Hashtags & Topics",
            "duration_minutes": 15,
            "content": "Discuss trending hashtags and topics...",
            "hashtags": ["#trending1", "#trending2"],
            "voice_notes": "excited, trend-focused"
        }},
        {{
            "segment_number": 4,
            "title": "Trendsetting Strategies",
            "duration_minutes": 25,
            "content": "How to become a trendsetter, not a follower...",
            "strategies": ["strategy 1", "strategy 2", "strategy 3"],
            "action_steps": ["step 1", "step 2"],
            "voice_notes": "motivational, actionable"
        }},
        {{
            "segment_number": 5,
            "title": "Platform Deep Dive",
            "duration_minutes": 15,
            "content": "Platform-specific insights (Instagram, TikTok, Twitter)...",
            "platforms": {{"instagram": "...", "tiktok": "...", "twitter": "..."}},
            "voice_notes": "detailed, educational"
        }},
        {{
            "segment_number": 6,
            "title": "Listener Q&A & Tips",
            "duration_minutes": 7,
            "content": "Answer common questions and rapid-fire tips...",
            "tips": ["tip 1", "tip 2", "tip 3"],
            "voice_notes": "quick-paced, helpful"
        }},
        {{
            "segment_number": 7,
            "title": "Wrap-Up & Challenge",
            "duration_minutes": 3,
            "content": "Summary and tomorrow's challenge...",
            "challenge": "Your trendsetting challenge for tomorrow",
            "voice_notes": "motivational, inspiring"
        }}
    ],
    "show_notes": "Summary of episode with timestamps and resources",
    "call_to_action": "How listeners can engage"
}}

Make it engaging, insightful, and actionable. Reference specific viral content from the data.
Use natural podcast language - conversational, not overly formal.
Include humor, storytelling, and real examples."""
    
    def _build_script_context(self, viral_data: Dict) -> str:
        """Build context string from viral data"""
        
        context_parts = []
        
        # Viral posts summary
        if viral_data.get('viral_posts'):
            context_parts.append("TOP VIRAL POSTS TODAY:")
            for i, post in enumerate(viral_data['viral_posts'][:10], 1):
                platform = post.get('platform', 'unknown')
                caption = post.get('caption', '')[:200]
                engagement = post.get('engagement_score', 0)
                hashtags = ', '.join(post.get('hashtags', [])[:5])
                context_parts.append(
                    f"{i}. [{platform.upper()}] {caption}... "
                    f"(Engagement: {engagement:,}, Tags: {hashtags})"
                )
        
        # Trending hashtags
        if viral_data.get('trending_hashtags'):
            context_parts.append("\nTRENDING HASHTAGS:")
            for hashtag in viral_data['trending_hashtags'][:15]:
                tag = hashtag.get('hashtag', '')
                usage = hashtag.get('usage_count', 0)
                context_parts.append(f"- {tag} (used {usage:,} times)")
        
        # Trending topics
        if viral_data.get('trending_topics'):
            context_parts.append("\nTRENDING TOPICS:")
            for topic in viral_data['trending_topics'][:10]:
                name = topic.get('topic', '')
                score = topic.get('trend_score', 0)
                context_parts.append(f"- {name} (score: {score:.1f})")
        
        # AI insights
        if viral_data.get('ai_insights'):
            context_parts.append("\nAI INSIGHTS:")
            for insight in viral_data['ai_insights'][:5]:
                context_parts.append(f"- {insight}")
        
        return "\n".join(context_parts)
    
    def _parse_script(self, script_content: str, duration_minutes: int) -> Dict:
        """Parse AI-generated script into structured format"""
        
        try:
            # Try to parse as JSON
            if script_content.strip().startswith('{'):
                script = json.loads(script_content)
                return script
            
            # Otherwise, extract JSON from markdown code block
            if '```json' in script_content:
                json_start = script_content.find('```json') + 7
                json_end = script_content.find('```', json_start)
                json_str = script_content[json_start:json_end].strip()
                script = json.loads(json_str)
                return script
            
            # Fallback: treat as plain text and structure it
            return {
                'title': f"Viral Trends Daily - {datetime.now().strftime('%B %d, %Y')}",
                'subtitle': 'Analyzing today\'s viral content and trendsetting strategies',
                'segments': [
                    {
                        'segment_number': 1,
                        'title': 'Full Episode',
                        'duration_minutes': duration_minutes,
                        'content': script_content,
                        'voice_notes': 'conversational, engaging'
                    }
                ],
                'show_notes': 'Full episode transcript',
                'call_to_action': 'Follow for daily viral trends analysis'
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing script: {e}")
            return self._generate_fallback_script({}, duration_minutes)
    
    def _generate_fallback_script(self, viral_data: Dict, duration_minutes: int) -> Dict:
        """Generate basic script when AI is unavailable"""
        
        date_str = datetime.now().strftime('%B %d, %Y')
        
        # Build content from viral data
        viral_posts = viral_data.get('viral_posts', [])
        hashtags = viral_data.get('trending_hashtags', [])
        topics = viral_data.get('trending_topics', [])
        
        intro_content = f"""Welcome to Viral Trends Daily for {date_str}! 
        I'm your AI host, and today we're diving deep into what's trending across social media.
        We've analyzed thousands of posts, and I'm excited to share the most important insights with you."""
        
        viral_breakdown = "Let's break down today's top viral content. "
        if viral_posts:
            viral_breakdown += f"We've identified {len(viral_posts)} major viral posts with over 10,000 engagements each. "
            top_post = viral_posts[0]
            viral_breakdown += f"The top performer is on {top_post.get('platform', 'social media')} with {top_post.get('engagement_score', 0):,} engagement points. "
        
        hashtag_segment = "Now, trending hashtags. "
        if hashtags:
            top_tags = [h.get('hashtag', '') for h in hashtags[:5]]
            hashtag_segment += f"The top hashtags today are: {', '.join(top_tags)}. "
        
        return {
            'title': f"Viral Trends Daily - {date_str}",
            'subtitle': 'Your daily dose of viral content analysis',
            'segments': [
                {
                    'segment_number': 1,
                    'title': 'Welcome & Intro',
                    'duration_minutes': 5,
                    'content': intro_content,
                    'voice_notes': 'enthusiastic, welcoming'
                },
                {
                    'segment_number': 2,
                    'title': 'Viral Content Breakdown',
                    'duration_minutes': 30,
                    'content': viral_breakdown,
                    'voice_notes': 'analytical, detailed'
                },
                {
                    'segment_number': 3,
                    'title': 'Trending Hashtags',
                    'duration_minutes': 20,
                    'content': hashtag_segment,
                    'voice_notes': 'energetic, trend-focused'
                },
                {
                    'segment_number': 4,
                    'title': 'Trendsetting Strategies',
                    'duration_minutes': 25,
                    'content': 'How to become a trendsetter instead of just following trends...',
                    'voice_notes': 'motivational, actionable'
                },
                {
                    'segment_number': 5,
                    'title': 'Wrap-Up',
                    'duration_minutes': 10,
                    'content': 'That wraps up today\'s episode. Keep creating, keep trending!',
                    'voice_notes': 'inspiring, energetic'
                }
            ],
            'show_notes': f'Episode for {date_str} analyzing viral trends',
            'call_to_action': 'Follow for daily trend analysis'
        }
    
    async def _generate_audio(self, script: Dict) -> List[str]:
        """
        Generate audio for podcast segments using TTS
        
        Returns:
            List of audio file paths
        """
        self.logger.info("🎤 Generating audio...")
        
        if not self.client:
            self.logger.warning("⚠️ OpenAI not available, skipping audio generation")
            return []
        
        audio_files = []
        episode_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            for segment in script.get('segments', []):
                segment_num = segment.get('segment_number', 0)
                content = segment.get('content', '')
                
                if not content:
                    continue
                
                # Generate audio with OpenAI TTS
                self.logger.info(f"  Generating segment {segment_num}...")
                
                response = self.client.audio.speech.create(
                    model="tts-1-hd",  # High quality
                    voice="nova",  # Female voice (or: alloy, echo, fable, onyx, shimmer)
                    input=content[:4096],  # Max 4096 characters per request
                    speed=1.0
                )
                
                # Save audio file
                audio_path = self.audio_dir / f"{episode_id}_segment_{segment_num}.mp3"
                response.stream_to_file(str(audio_path))
                
                audio_files.append(str(audio_path))
                self.logger.info(f"  ✅ Saved: {audio_path.name}")
            
            self.logger.info(f"✅ Generated {len(audio_files)} audio segments")
            
        except Exception as e:
            self.logger.error(f"❌ Error generating audio: {e}")
        
        return audio_files
    
    def _create_podcast_metadata(
        self,
        script: Dict,
        audio_files: List[str],
        duration_minutes: int
    ) -> Dict:
        """Create podcast episode metadata"""
        
        return {
            'episode_id': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'title': script.get('title', 'Viral Trends Daily'),
            'subtitle': script.get('subtitle', ''),
            'description': script.get('show_notes', ''),
            'duration_minutes': duration_minutes,
            'segment_count': len(script.get('segments', [])),
            'audio_files_count': len(audio_files),
            'created_at': datetime.now().isoformat(),
            'status': 'generated',
            'platforms': ['spotify', 'apple_podcasts', 'youtube', 'soundcloud'],
            'tags': ['viral trends', 'social media', 'trendsetting', 'content creation'],
            'language': 'en'
        }
    
    def _save_episode(self, script: Dict, metadata: Dict) -> str:
        """Save episode script and metadata"""
        
        episode_id = metadata['episode_id']
        
        # Save script
        script_path = self.scripts_dir / f"{episode_id}.json"
        with open(script_path, 'w') as f:
            json.dump(script, f, indent=2)
        
        # Save metadata
        metadata_path = self.metadata_dir / f"{episode_id}.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.logger.info(f"💾 Saved episode: {episode_id}")
        
        return episode_id
    
    def get_scheduled_time(self) -> time:
        """Get podcast scheduled time (default 9 PM)"""
        return self.config.get('podcast', {}).get('scheduled_time', self.default_schedule)
    
    def should_generate_now(self) -> bool:
        """Check if it's time to generate today's podcast"""
        scheduled = self.get_scheduled_time()
        now = datetime.now().time()
        
        # Check if we're within 5 minutes of scheduled time
        time_diff = abs(
            (now.hour * 60 + now.minute) - 
            (scheduled.hour * 60 + scheduled.minute)
        )
        
        return time_diff <= 5


# Quick test function
async def test_podcast_generator():
    """Test podcast generation"""
    
    from core.config import Config
    from core.database import Database
    
    print("🎙️ Testing Podcast Generator...")
    
    config = Config()
    database = Database()
    
    generator = PodcastGenerator(config, database, None)
    
    # Generate test podcast
    result = await generator.generate_daily_podcast(
        duration_minutes=90,
        topic_focus="How to create viral TikTok content"
    )
    
    print("\n" + "="*50)
    print("RESULT:")
    print("="*50)
    print(json.dumps(result, indent=2))
    
    if result.get('success'):
        print(f"\n✅ Podcast generated successfully!")
        print(f"📝 Script: {result['script_path']}")
        print(f"🎤 Audio files: {len(result.get('audio_files', []))}")


if __name__ == "__main__":
    asyncio.run(test_podcast_generator())
