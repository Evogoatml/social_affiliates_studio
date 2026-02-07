"""
CrewAI Integration for Multi-Agent Content Creation
Adds role-based agent collaboration to the Autonomous Influencer System
"""

try:
    from crewai import Agent, Task, Crew, Process
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    print("⚠️ CrewAI not installed. Run: pip install crewai crewai-tools")

import logging
from typing import Dict, List, Optional


class ContentCreationCrew:
    """
    Multi-agent crew for collaborative content creation
    Uses CrewAI for role-based agent coordination
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize content creation crew
        
        Args:
            config: System configuration
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        if not CREWAI_AVAILABLE:
            self.logger.error("❌ CrewAI not available")
            return
        
        # Initialize agents
        self.trend_analyzer = self._create_trend_analyzer()
        self.content_creator = self._create_content_creator()
        self.strategist = self._create_strategist()
        self.quality_reviewer = self._create_quality_reviewer()
        
        self.logger.info("✅ Content Creation Crew initialized")
    
    def _create_trend_analyzer(self) -> Agent:
        """Create trend analysis agent"""
        return Agent(
            role='Viral Trend Analyzer',
            goal='Identify and analyze trending content patterns across social media platforms',
            backstory="""You are an expert in social media trends with a keen eye for 
            viral content. You analyze engagement patterns, hashtag trends, and content 
            formats to identify what's working right now. You have access to real-time 
            data from Instagram, TikTok, and Twitter.""",
            verbose=True,
            allow_delegation=True
        )
    
    def _create_content_creator(self) -> Agent:
        """Create content creation agent"""
        return Agent(
            role='Viral Content Creator',
            goal='Create highly engaging, platform-optimized social media content',
            backstory="""You are a creative genius who understands what makes content 
            go viral. You craft compelling captions, choose perfect hashtags, and design 
            content that resonates with target audiences. You specialize in Instagram 
            reels, TikTok videos, and Twitter threads.""",
            verbose=True,
            allow_delegation=False
        )
    
    def _create_strategist(self) -> Agent:
        """Create marketing strategy agent"""
        return Agent(
            role='Marketing Strategist',
            goal='Optimize content strategy for maximum engagement and growth',
            backstory="""You are a data-driven marketing expert who analyzes performance 
            metrics and optimizes content strategy. You understand posting schedules, 
            audience psychology, and platform algorithms. You use analytics to continuously 
            improve content performance.""",
            verbose=True,
            allow_delegation=True
        )
    
    def _create_quality_reviewer(self) -> Agent:
        """Create quality review agent"""
        return Agent(
            role='Content Quality Reviewer',
            goal='Ensure all content meets high quality standards and brand guidelines',
            backstory="""You are a meticulous editor who ensures content quality, 
            brand consistency, and platform compliance. You check for grammar, tone, 
            appropriateness, and viral potential before approving content for publication.""",
            verbose=True,
            allow_delegation=False
        )
    
    def create_viral_content(
        self,
        topic: str,
        platform: str = "instagram",
        content_type: str = "post"
    ) -> Dict:
        """
        Create viral content using multi-agent collaboration
        
        Args:
            topic: Content topic or theme
            platform: Target platform (instagram, tiktok, twitter)
            content_type: Type of content (post, reel, video, thread)
            
        Returns:
            Dictionary with created content
        """
        if not CREWAI_AVAILABLE:
            return {"error": "CrewAI not available"}
        
        self.logger.info(f"🎬 Creating {content_type} for {platform} about: {topic}")
        
        try:
            # Define tasks
            analyze_task = Task(
                description=f"""Analyze current trends for {platform} related to {topic}.
                Identify:
                - Top performing content formats
                - Trending hashtags
                - Optimal posting times
                - Audience preferences
                - Viral content patterns
                
                Provide detailed insights for content creation.""",
                agent=self.trend_analyzer,
                expected_output="Detailed trend analysis with specific recommendations"
            )
            
            create_task = Task(
                description=f"""Based on the trend analysis, create a viral {content_type} 
                for {platform} about {topic}.
                
                Include:
                - Engaging caption (platform-appropriate length)
                - Relevant hashtags (optimal number for platform)
                - Content description or script
                - Call-to-action
                - Visual suggestions
                
                Make it highly engaging and viral-worthy.""",
                agent=self.content_creator,
                expected_output="Complete content package with caption, hashtags, and description"
            )
            
            optimize_task = Task(
                description="""Review the created content and optimize it for maximum 
                engagement. Suggest improvements for:
                - Caption hooks and CTAs
                - Hashtag selection
                - Posting timing
                - Expected engagement
                - A/B testing variations
                
                Provide strategic recommendations.""",
                agent=self.strategist,
                expected_output="Optimized content with strategic recommendations"
            )
            
            review_task = Task(
                description="""Review the optimized content for quality and brand alignment.
                Check:
                - Grammar and spelling
                - Tone and voice consistency
                - Platform guidelines compliance
                - Viral potential score (1-10)
                - Final approval or revision suggestions
                
                Provide final verdict and improvements.""",
                agent=self.quality_reviewer,
                expected_output="Quality review with approval status and suggestions"
            )
            
            # Create crew
            crew = Crew(
                agents=[
                    self.trend_analyzer,
                    self.content_creator,
                    self.strategist,
                    self.quality_reviewer
                ],
                tasks=[analyze_task, create_task, optimize_task, review_task],
                process=Process.sequential,
                verbose=True
            )
            
            # Execute crew workflow
            result = crew.kickoff()
            
            self.logger.info("✅ Content creation complete!")
            
            return {
                "success": True,
                "content": result,
                "platform": platform,
                "content_type": content_type,
                "topic": topic
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error in crew workflow: {e}")
            return {"error": str(e)}
    
    def analyze_competitor_content(
        self,
        competitor_handles: List[str],
        platform: str = "instagram"
    ) -> Dict:
        """
        Analyze competitor content using crew collaboration
        
        Args:
            competitor_handles: List of competitor usernames
            platform: Platform to analyze
            
        Returns:
            Competitor analysis report
        """
        if not CREWAI_AVAILABLE:
            return {"error": "CrewAI not available"}
        
        self.logger.info(f"🔍 Analyzing competitors on {platform}")
        
        try:
            analysis_task = Task(
                description=f"""Analyze content from competitors: {', '.join(competitor_handles)}
                on {platform}.
                
                Identify:
                - Top performing content themes
                - Successful content formats
                - Engagement patterns
                - Posting frequency and timing
                - Unique strategies
                - Gaps and opportunities
                
                Provide actionable insights.""",
                agent=self.trend_analyzer,
                expected_output="Comprehensive competitor analysis with opportunities"
            )
            
            strategy_task = Task(
                description="""Based on the competitor analysis, develop a differentiation 
                strategy. Recommend:
                - Unique positioning
                - Content gaps to fill
                - Better approaches
                - Competitive advantages
                - Growth opportunities
                
                Create a winning strategy.""",
                agent=self.strategist,
                expected_output="Differentiation strategy with specific action items"
            )
            
            crew = Crew(
                agents=[self.trend_analyzer, self.strategist],
                tasks=[analysis_task, strategy_task],
                process=Process.sequential
            )
            
            result = crew.kickoff()
            
            return {
                "success": True,
                "analysis": result,
                "competitors": competitor_handles,
                "platform": platform
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error in competitor analysis: {e}")
            return {"error": str(e)}
    
    def optimize_posting_schedule(self, analytics_data: Dict) -> Dict:
        """
        Optimize posting schedule using crew analysis
        
        Args:
            analytics_data: Historical performance data
            
        Returns:
            Optimized posting schedule
        """
        if not CREWAI_AVAILABLE:
            return {"error": "CrewAI not available"}
        
        try:
            optimization_task = Task(
                description=f"""Analyze the performance data and optimize posting schedule.
                
                Data: {analytics_data}
                
                Determine:
                - Best posting times per platform
                - Optimal posting frequency
                - Content type preferences by time
                - Audience activity patterns
                - Seasonal trends
                
                Provide optimized schedule.""",
                agent=self.strategist,
                expected_output="Detailed posting schedule with timing recommendations"
            )
            
            crew = Crew(
                agents=[self.strategist],
                tasks=[optimization_task],
                process=Process.sequential
            )
            
            result = crew.kickoff()
            
            return {
                "success": True,
                "schedule": result
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error in schedule optimization: {e}")
            return {"error": str(e)}


def quick_test():
    """Quick test of CrewAI integration"""
    if not CREWAI_AVAILABLE:
        print("❌ CrewAI not installed")
        print("Install with: pip install crewai crewai-tools")
        return
    
    print("🚀 Testing CrewAI Integration...")
    
    crew = ContentCreationCrew()
    
    # Test content creation
    result = crew.create_viral_content(
        topic="Morning motivation and productivity",
        platform="instagram",
        content_type="reel"
    )
    
    print("\n" + "="*50)
    print("RESULT:")
    print("="*50)
    print(result)
    print("\n✅ CrewAI integration test complete!")


if __name__ == "__main__":
    quick_test()
