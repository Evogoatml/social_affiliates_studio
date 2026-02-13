"""
Test suite for video generation system
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from content.video_generator import VideoGenerator
from content.video_providers.base_provider import VideoStatus, VideoResult
from content.video_providers import KlingProvider, PikaProvider, RunwayProvider
from content.video_queue import VideoQueue, QueuePriority
from content.video_utils import VideoOptimizer
from analytics.video_analytics import VideoAnalytics
from core.config import Config
from core.database import Database


# Fixtures

@pytest.fixture
def mock_config():
    """Mock configuration"""
    config = Mock(spec=Config)
    config.get.return_value = {
        "video_generation": {
            "enabled": True,
            "default_provider": "kling",
            "fallback_providers": ["pika"],
            "budget": {
                "daily_limit_usd": 10.0,
                "monthly_limit_usd": 200.0,
                "per_video_max_usd": 2.0
            },
            "providers": {
                "kling": {
                    "enabled": True,
                    "priority": 1,
                    "cost_per_video": 0.0
                },
                "pika": {
                    "enabled": True,
                    "priority": 2,
                    "cost_per_video": 0.5
                }
            }
        }
    }
    return config


@pytest.fixture
def mock_db():
    """Mock database"""
    db = Mock(spec=Database)
    db.add_video_generation.return_value = True
    db.get_video_analytics.return_value = {
        "total_videos": 10,
        "completed": 8,
        "failed": 2,
        "total_cost": 5.0,
        "avg_cost": 0.5
    }
    return db


# Base Provider Tests

class TestBaseProvider:
    """Test base provider functionality"""
    
    def test_provider_initialization(self):
        """Test provider can be initialized"""
        provider = KlingProvider(api_key="test-key", config={"priority": 1})
        assert provider.api_key == "test-key"
        assert provider.config["priority"] == 1
        assert provider.provider_name == "kling"
    
    def test_rate_limit_defaults(self):
        """Test default rate limits"""
        provider = KlingProvider(api_key="test-key")
        limits = provider.get_rate_limit()
        assert "per_minute" in limits
        assert "per_day" in limits
    
    def test_max_duration(self):
        """Test max duration setting"""
        provider = KlingProvider(api_key="test-key", config={"max_duration": 30})
        assert provider.get_max_duration() == 30


# Provider Implementations Tests

class TestKlingProvider:
    """Test Kling provider"""
    
    @pytest.mark.asyncio
    async def test_estimate_cost(self):
        """Test cost estimation for free tier"""
        provider = KlingProvider(api_key="test-key")
        cost = await provider.estimate_cost({"duration": 15})
        assert cost == 0.0
    
    @pytest.mark.asyncio
    async def test_generate_video_error_handling(self):
        """Test error handling in video generation"""
        provider = KlingProvider(api_key="invalid-key")
        
        # Mock the session to raise an exception
        with patch.object(provider, '_get_session') as mock_session:
            mock_session.side_effect = Exception("Connection error")
            
            result = await provider.generate_video(
                prompt="Test video",
                duration=15
            )
            
            assert result.status == VideoStatus.FAILED
            assert "Connection error" in result.error_message


class TestPikaProvider:
    """Test Pika provider"""
    
    @pytest.mark.asyncio
    async def test_estimate_cost(self):
        """Test cost estimation"""
        provider = PikaProvider(api_key="test-key", config={"cost_per_second": 0.033})
        cost = await provider.estimate_cost({"duration": 15})
        assert cost == pytest.approx(0.495, 0.01)


# Video Generator Tests

class TestVideoGenerator:
    """Test video generator orchestrator"""
    
    def test_initialization(self, mock_config, mock_db):
        """Test video generator initialization"""
        with patch('content.video_generator.VideoProviderRegistry.create_provider') as mock_create:
            mock_create.return_value = Mock()
            
            generator = VideoGenerator(mock_config, mock_db)
            assert generator.config == mock_config
            assert generator.db == mock_db
            assert generator.daily_spent == 0.0
            assert generator.monthly_spent == 0.0
    
    def test_budget_check(self, mock_config, mock_db):
        """Test budget limit checking"""
        generator = VideoGenerator(mock_config, mock_db)
        
        # Under budget
        assert generator._check_budget() == True
        
        # Exceed daily budget
        generator.daily_spent = 15.0
        assert generator._check_budget() == False
    
    def test_provider_ordering(self, mock_config, mock_db):
        """Test provider priority ordering"""
        generator = VideoGenerator(mock_config, mock_db)
        order = generator._get_provider_order()
        
        # Should be ordered by priority (lower number = higher priority)
        assert isinstance(order, list)
    
    @pytest.mark.asyncio
    async def test_generate_from_trend(self, mock_config, mock_db):
        """Test video generation from trending content"""
        generator = VideoGenerator(mock_config, mock_db)
        
        # Mock provider
        mock_provider = AsyncMock()
        mock_provider.estimate_cost.return_value = 0.0
        mock_provider.generate_video.return_value = VideoResult(
            job_id="test-123",
            status=VideoStatus.QUEUED,
            cost_usd=0.0
        )
        mock_provider.get_status.return_value = VideoResult(
            job_id="test-123",
            status=VideoStatus.COMPLETED,
            video_url="https://example.com/video.mp4",
            cost_usd=0.0
        )
        
        generator.providers["kling"] = mock_provider
        
        trend = {
            "caption": "Test trend",
            "hashtags": ["test", "trend"],
            "theme": "lifestyle"
        }
        
        result = await generator.generate_video_from_trend(
            trend=trend,
            avatar={"personality": "friendly"},
            platform="instagram"
        )
        
        assert result is not None
        assert result.status == VideoStatus.COMPLETED


# Video Queue Tests

class TestVideoQueue:
    """Test video queue management"""
    
    @pytest.mark.asyncio
    async def test_add_request(self):
        """Test adding request to queue"""
        queue = VideoQueue()
        
        success = await queue.add_request(
            request_id="test-1",
            prompt="Test video",
            params={"duration": 15},
            priority=QueuePriority.NORMAL
        )
        
        assert success == True
        assert queue.get_queue_size() == 1
    
    @pytest.mark.asyncio
    async def test_get_next_request(self):
        """Test retrieving request from queue"""
        queue = VideoQueue(max_concurrent=3)
        
        await queue.add_request("test-1", "Video 1", {}, QueuePriority.NORMAL)
        await queue.add_request("test-2", "Video 2", {}, QueuePriority.HIGH)
        
        # High priority should come first
        request = await queue.get_next_request()
        assert request.request_id == "test-2"
        assert request.priority == QueuePriority.HIGH
    
    @pytest.mark.asyncio
    async def test_mark_completed(self):
        """Test marking request as completed"""
        queue = VideoQueue()
        
        await queue.add_request("test-1", "Video 1", {})
        request = await queue.get_next_request()
        
        await queue.mark_completed("test-1", result={"success": True})
        
        assert "test-1" in queue.completed
        assert queue.stats["total_completed"] == 1
    
    @pytest.mark.asyncio
    async def test_retry_logic(self):
        """Test automatic retry on failure"""
        queue = VideoQueue()
        
        await queue.add_request("test-1", "Video 1", {})
        request = await queue.get_next_request()
        
        # Fail with retry
        await queue.mark_failed("test-1", error="Test error", retry=True)
        
        # Should be back in queue
        await asyncio.sleep(2.5)  # Wait for exponential backoff
        assert queue.get_queue_size() > 0


# Video Utils Tests

class TestVideoOptimizer:
    """Test video optimization utilities"""
    
    def test_get_instagram_specs(self):
        """Test Instagram specifications"""
        optimizer = VideoOptimizer()
        specs = optimizer.get_platform_specs("instagram", "reels")
        
        assert specs["aspect_ratio"] == "9:16"
        assert specs["width"] == 1080
        assert specs["height"] == 1920
        assert specs["max_duration"] == 90
    
    def test_validate_params(self):
        """Test parameter validation"""
        optimizer = VideoOptimizer()
        
        # Valid params
        valid, error = optimizer.validate_video_params(
            platform="instagram",
            content_type="reels",
            duration=15,
            aspect_ratio="9:16"
        )
        assert valid == True
        assert error is None
        
        # Invalid duration
        valid, error = optimizer.validate_video_params(
            platform="instagram",
            content_type="reels",
            duration=120  # Too long
        )
        assert valid == False
        assert "too long" in error.lower()
    
    def test_optimal_params(self):
        """Test optimal parameter generation"""
        optimizer = VideoOptimizer()
        params = optimizer.get_optimal_params("instagram", "reels")
        
        assert params["duration"] == 15
        assert params["aspect_ratio"] == "9:16"
        assert params["format"] == "mp4"
    
    def test_file_size_estimation(self):
        """Test file size estimation"""
        optimizer = VideoOptimizer()
        
        size_mb = optimizer.estimate_file_size(
            duration=15,
            width=1080,
            height=1920,
            bitrate="8M"
        )
        
        assert size_mb > 0
        assert size_mb < 100  # Should be under Instagram limit


# Analytics Tests

class TestVideoAnalytics:
    """Test video analytics"""
    
    def test_initialization(self, mock_db):
        """Test analytics initialization"""
        analytics = VideoAnalytics(mock_db)
        assert analytics.db == mock_db
    
    def test_cost_summary(self, mock_db):
        """Test cost summary generation"""
        analytics = VideoAnalytics(mock_db)
        
        mock_db.get_video_analytics.return_value = {
            "total_videos": 10,
            "total_cost": 5.0,
            "avg_cost": 0.5
        }
        mock_db.get_provider_performance.return_value = {}
        
        summary = analytics.get_cost_summary(days=30)
        
        assert summary["total_videos"] == 10
        assert summary["total_cost_usd"] == 5.0
        assert summary["avg_cost_per_video"] == 0.5
    
    def test_budget_alerts(self, mock_db):
        """Test budget alert generation"""
        analytics = VideoAnalytics(mock_db)
        
        # No alerts
        alerts = analytics.check_budget_alerts(
            daily_limit=10.0,
            monthly_limit=200.0,
            current_daily=5.0,
            current_monthly=100.0
        )
        assert len(alerts) == 0
        
        # Warning alert
        alerts = analytics.check_budget_alerts(
            daily_limit=10.0,
            monthly_limit=200.0,
            current_daily=8.0,
            current_monthly=160.0
        )
        assert len(alerts) == 2
        assert all(a["type"] == "warning" for a in alerts)
        
        # Critical alert
        alerts = analytics.check_budget_alerts(
            daily_limit=10.0,
            monthly_limit=200.0,
            current_daily=9.5,
            current_monthly=190.0
        )
        assert len(alerts) == 2
        assert all(a["type"] == "critical" for a in alerts)


# Integration Tests

class TestVideoGenerationIntegration:
    """Test full video generation workflow"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, mock_config, mock_db):
        """Test complete video generation workflow"""
        # This would be a full integration test with mocked external APIs
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
