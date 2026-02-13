"""
Video Analytics - Track video generation costs, performance, and ROI
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json

from core.logger import setup_logger
from core.database import Database

logger = setup_logger(__name__)


class VideoAnalytics:
    """Track and analyze video generation performance"""
    
    def __init__(self, db: Database):
        self.db = db
        self.reports_dir = Path("data/reports/video_analytics")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("✅ Video Analytics initialized")
    
    def get_cost_summary(self, days: int = 30) -> Dict:
        """
        Get cost summary for video generation
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Dict with cost breakdown
        """
        analytics = self.db.get_video_analytics(days=days)
        provider_performance = self.db.get_provider_performance()
        
        summary = {
            "period_days": days,
            "total_videos": analytics.get("total_videos", 0),
            "total_cost_usd": analytics.get("total_cost", 0.0),
            "avg_cost_per_video": analytics.get("avg_cost", 0.0),
            "by_provider": {}
        }
        
        for provider, perf in provider_performance.items():
            summary["by_provider"][provider] = {
                "videos": perf.get("total_videos", 0),
                "cost": perf.get("total_spent_usd", 0.0),
                "success_rate": perf.get("success_rate", 0.0)
            }
        
        return summary
    
    def get_performance_metrics(self, days: int = 30) -> Dict:
        """
        Get performance metrics for video generation
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Dict with performance metrics
        """
        analytics = self.db.get_video_analytics(days=days)
        provider_performance = self.db.get_provider_performance()
        
        total = analytics.get("total_videos", 0)
        completed = analytics.get("completed", 0)
        failed = analytics.get("failed", 0)
        
        metrics = {
            "period_days": days,
            "total_videos": total,
            "completed_videos": completed,
            "failed_videos": failed,
            "success_rate": (completed / total * 100) if total > 0 else 0.0,
            "avg_engagement": analytics.get("avg_engagement", 0.0),
            "avg_duration": analytics.get("avg_duration", 0.0),
            "provider_comparison": []
        }
        
        # Add provider comparison
        for provider, perf in provider_performance.items():
            metrics["provider_comparison"].append({
                "provider": provider,
                "success_rate": perf.get("success_rate", 0.0),
                "avg_cost": perf.get("avg_cost_usd", 0.0),
                "total_videos": perf.get("total_videos", 0),
                "last_used": perf.get("last_used", "")
            })
        
        # Sort by success rate
        metrics["provider_comparison"].sort(key=lambda x: x["success_rate"], reverse=True)
        
        return metrics
    
    def check_budget_alerts(
        self,
        daily_limit: float,
        monthly_limit: float,
        current_daily: float,
        current_monthly: float
    ) -> List[Dict]:
        """
        Check for budget alerts
        
        Args:
            daily_limit: Daily budget limit in USD
            monthly_limit: Monthly budget limit in USD
            current_daily: Current daily spending
            current_monthly: Current monthly spending
        
        Returns:
            List of alert messages
        """
        alerts = []
        
        # Daily budget alerts
        daily_pct = (current_daily / daily_limit * 100) if daily_limit > 0 else 0
        if daily_pct >= 90:
            alerts.append({
                "type": "critical",
                "message": f"Daily budget at {daily_pct:.1f}% (${current_daily:.2f} / ${daily_limit:.2f})",
                "timestamp": datetime.now().isoformat()
            })
        elif daily_pct >= 75:
            alerts.append({
                "type": "warning",
                "message": f"Daily budget at {daily_pct:.1f}% (${current_daily:.2f} / ${daily_limit:.2f})",
                "timestamp": datetime.now().isoformat()
            })
        
        # Monthly budget alerts
        monthly_pct = (current_monthly / monthly_limit * 100) if monthly_limit > 0 else 0
        if monthly_pct >= 90:
            alerts.append({
                "type": "critical",
                "message": f"Monthly budget at {monthly_pct:.1f}% (${current_monthly:.2f} / ${monthly_limit:.2f})",
                "timestamp": datetime.now().isoformat()
            })
        elif monthly_pct >= 75:
            alerts.append({
                "type": "warning",
                "message": f"Monthly budget at {monthly_pct:.1f}% (${current_monthly:.2f} / ${monthly_limit:.2f})",
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts
    
    def generate_cost_report(self, days: int = 30) -> str:
        """
        Generate cost report and save to file
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Path to report file
        """
        cost_summary = self.get_cost_summary(days=days)
        performance = self.get_performance_metrics(days=days)
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "period_days": days,
            "cost_summary": cost_summary,
            "performance_metrics": performance,
            "recommendations": self._generate_recommendations(cost_summary, performance)
        }
        
        # Save report
        filename = f"video_cost_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.reports_dir / filename
        
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"✅ Cost report generated: {filepath}")
        return str(filepath)
    
    def _generate_recommendations(
        self,
        cost_summary: Dict,
        performance: Dict
    ) -> List[str]:
        """Generate recommendations based on analytics"""
        recommendations = []
        
        # Cost optimization
        total_cost = cost_summary.get("total_cost_usd", 0.0)
        if total_cost > 150:
            recommendations.append(
                "Consider using free tier providers (Kling) for non-critical content to reduce costs"
            )
        
        # Success rate optimization
        success_rate = performance.get("success_rate", 0.0)
        if success_rate < 80:
            recommendations.append(
                f"Success rate is {success_rate:.1f}%. Review failed generations and adjust prompts or providers"
            )
        
        # Provider recommendations
        best_provider = None
        best_rate = 0.0
        
        for provider_data in performance.get("provider_comparison", []):
            if provider_data["success_rate"] > best_rate:
                best_rate = provider_data["success_rate"]
                best_provider = provider_data["provider"]
        
        if best_provider and best_rate > 90:
            recommendations.append(
                f"Provider '{best_provider}' has the best success rate ({best_rate:.1f}%). "
                "Consider prioritizing it for important content"
            )
        
        # Engagement recommendations
        avg_engagement = performance.get("avg_engagement", 0.0)
        if avg_engagement > 0 and avg_engagement < 0.03:
            recommendations.append(
                f"Average engagement is {avg_engagement:.2%}. Consider A/B testing different video styles"
            )
        
        return recommendations
    
    def get_roi_analysis(self, days: int = 30) -> Dict:
        """
        Calculate ROI for video generation
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Dict with ROI metrics
        """
        analytics = self.db.get_video_analytics(days=days)
        
        total_cost = analytics.get("total_cost", 0.0)
        total_videos = analytics.get("total_videos", 0)
        avg_engagement = analytics.get("avg_engagement", 0.0)
        
        # Estimated value per engagement (configurable)
        value_per_engagement = 0.05  # $0.05 per engagement
        
        # Get videos with engagement data
        videos = self.db.get_video_generations(status="completed", limit=1000)
        total_engagement = sum(
            v.get("views", 0) * v.get("engagement_rate", 0.0)
            for v in videos
            if v.get("created_at", "") >= (datetime.now() - timedelta(days=days)).isoformat()
        )
        
        estimated_value = total_engagement * value_per_engagement
        roi = ((estimated_value - total_cost) / total_cost * 100) if total_cost > 0 else 0
        
        return {
            "period_days": days,
            "total_cost": total_cost,
            "total_videos": total_videos,
            "total_engagement": int(total_engagement),
            "estimated_value": estimated_value,
            "roi_percentage": roi,
            "cost_per_engagement": (total_cost / total_engagement) if total_engagement > 0 else 0
        }
    
    def get_trending_video_insights(self, limit: int = 10) -> List[Dict]:
        """
        Get insights on best-performing videos
        
        Args:
            limit: Number of top videos to analyze
        
        Returns:
            List of video insights
        """
        # Get top performing videos
        videos = self.db.get_video_generations(status="completed", limit=1000)
        
        # Sort by engagement
        videos.sort(
            key=lambda v: v.get("views", 0) * v.get("engagement_rate", 0.0),
            reverse=True
        )
        
        insights = []
        for video in videos[:limit]:
            engagement_count = video.get("views", 0) * video.get("engagement_rate", 0.0)
            insights.append({
                "job_id": video.get("job_id"),
                "provider": video.get("provider"),
                "views": video.get("views", 0),
                "engagement_rate": video.get("engagement_rate", 0.0),
                "engagement_count": int(engagement_count),
                "cost": video.get("cost_usd", 0.0),
                "duration": video.get("duration_seconds", 0),
                "created_at": video.get("created_at"),
                "prompt_preview": video.get("prompt", "")[:100]
            })
        
        return insights
