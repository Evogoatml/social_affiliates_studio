# Video Generation System Documentation

## 📋 Overview

The AI Influencer Video Generation System provides a scalable, production-ready solution for generating high-quality video content from trending topics. It features multi-provider support, automatic failover, cost tracking, and Instagram optimization.

---

## 🏗️ Architecture

### Components

1. **Video Generator** (`content/video_generator.py`)
   - Main orchestrator for video generation
   - Manages multi-provider failover
   - Tracks costs and enforces budget limits
   - Integrates with trending content system

2. **Provider System** (`content/video_providers/`)
   - Base abstraction for all video APIs
   - Provider implementations (Kling, Pika, Runway, HeyGen)
   - Factory pattern for provider instantiation
   - Rate limiting and cost estimation

3. **Queue Management** (`content/video_queue.py`)
   - Async queue for concurrent generation
   - Priority-based processing
   - Automatic retry with exponential backoff
   - Concurrency control

4. **Video Analytics** (`analytics/video_analytics.py`)
   - Cost tracking and reporting
   - Performance metrics
   - ROI analysis
   - Budget alerts

5. **Video Utilities** (`content/video_utils.py`)
   - Instagram optimization
   - Platform-specific specifications
   - Thumbnail generation
   - Video downloading

---

## 🚀 Quick Start

### 1. Configure API Keys

Edit `.env` file:

```bash
# Free tier (recommended for testing)
KLING_API_KEY=your-kling-api-key

# Mid-tier (paid)
PIKA_API_KEY=your-pika-api-key

# Premium tier (paid)
RUNWAY_API_KEY=your-runway-api-key
HEYGEN_API_KEY=your-heygen-api-key

# Enterprise (paid)
OPENAI_API_KEY=your-openai-api-key  # For Sora
```

### 2. Configure Video Settings

Edit `config/video_config.json`:

```json
{
  "video_generation": {
    "enabled": true,
    "default_provider": "kling",
    "fallback_providers": ["pika", "runway"],
    "budget": {
      "daily_limit_usd": 10.0,
      "monthly_limit_usd": 200.0
    },
    "providers": {
      "kling": {
        "enabled": true,
        "priority": 1
      }
    }
  }
}
```

### 3. Enable Video Generation

Edit `config/config.json`:

```json
{
  "content": {
    "video_ratio": 0.6,
    "video_generation": {
      "trending_topics": true,
      "use_avatar": true,
      "optimize_for_instagram": true
    }
  }
}
```

### 4. Run the System

```python
from core.orchestrator import AutonomousOrchestrator

orchestrator = AutonomousOrchestrator()
await orchestrator.start()
await orchestrator.run_forever()
```

---

## 🎯 Provider Comparison

### Free Tier

#### Kling AI
- **Cost**: Free (with limitations)
- **Rate Limit**: 10 videos/day
- **Quality**: Good
- **Speed**: Moderate
- **Best For**: Testing, low-volume generation
- **Setup**: Get free API key from [klingai.com](https://klingai.com)

### Mid-Tier ($50-200/mo)

#### Pika Labs
- **Cost**: ~$0.50 per 15s video
- **Rate Limit**: 5 videos/minute
- **Quality**: High
- **Speed**: Fast
- **Best For**: Trendy, stylized content
- **Setup**: [pika.art](https://pika.art)

### Premium Tier ($500+/mo)

#### Runway Gen-4.5
- **Cost**: ~$1.50 per 15s video
- **Rate Limit**: 2 videos/minute
- **Quality**: Cinematic
- **Speed**: Fast
- **Best For**: High-quality, professional content
- **Setup**: [runwayml.com](https://runwayml.com)

#### HeyGen
- **Cost**: ~$2.00 per 15s video
- **Rate Limit**: 1 video/minute
- **Quality**: Excellent (AI avatars)
- **Speed**: Moderate
- **Best For**: Talking-head videos, AI influencer content
- **Setup**: [heygen.com](https://heygen.com)

---

## 💰 Cost Management

### Budget Limits

The system enforces three levels of budget control:

1. **Per-Video Limit**: Prevents any single video from exceeding cost
2. **Daily Limit**: Stops generation when daily budget is reached
3. **Monthly Limit**: Tracks cumulative monthly spending

### Cost Tracking

All costs are tracked in the database:

```python
# Get cost summary
analytics = VideoAnalytics(db)
summary = analytics.get_cost_summary(days=30)

print(f"Total spent: ${summary['total_cost_usd']:.2f}")
print(f"Videos generated: {summary['total_videos']}")
print(f"Average cost: ${summary['avg_cost_per_video']:.2f}")
```

### Budget Alerts

Automatic alerts at 75% and 90% of budget limits:

```python
alerts = analytics.check_budget_alerts(
    daily_limit=10.0,
    monthly_limit=200.0,
    current_daily=7.5,
    current_monthly=150.0
)

for alert in alerts:
    print(f"{alert['type']}: {alert['message']}")
```

---

## 📊 Analytics & Reporting

### Performance Metrics

```python
# Get performance metrics
metrics = analytics.get_performance_metrics(days=30)

print(f"Success rate: {metrics['success_rate']:.1f}%")
print(f"Avg engagement: {metrics['avg_engagement']:.2%}")

# Provider comparison
for provider in metrics['provider_comparison']:
    print(f"{provider['provider']}: {provider['success_rate']:.1f}% success")
```

### Cost Reports

```python
# Generate comprehensive report
report_path = analytics.generate_cost_report(days=30)
print(f"Report saved: {report_path}")
```

### ROI Analysis

```python
# Calculate ROI
roi = analytics.get_roi_analysis(days=30)

print(f"Total cost: ${roi['total_cost']:.2f}")
print(f"Estimated value: ${roi['estimated_value']:.2f}")
print(f"ROI: {roi['roi_percentage']:.1f}%")
```

---

## 🎬 Video Generation Workflow

### 1. From Trending Content (Automatic)

The orchestrator automatically:
- Scrapes trending content every 6 hours
- Analyzes patterns with viral intelligence
- Generates videos from top 3 trends
- Adds to content queue

```python
# This happens automatically in orchestrator
await orchestrator._generate_content_batch()
```

### 2. Manual Generation

```python
from content.video_generator import VideoGenerator

video_gen = VideoGenerator(config, db)

# Generate from trend
result = await video_gen.generate_video_from_trend(
    trend={
        "caption": "Amazing lifestyle tips",
        "hashtags": ["lifestyle", "motivation"],
        "theme": "lifestyle"
    },
    avatar=avatar_data,
    platform="instagram"
)

print(f"Video URL: {result.video_url}")
print(f"Cost: ${result.cost_usd:.2f}")
```

### 3. Direct Provider Usage

```python
from content.video_providers import KlingProvider

provider = KlingProvider(api_key="your-key")

result = await provider.generate_video(
    prompt="Create a 15-second Instagram Reel about morning routines",
    style="trendy",
    duration=15,
    aspect_ratio="9:16"
)

# Wait for completion
while result.status == VideoStatus.PROCESSING:
    result = await provider.get_status(result.job_id)
    await asyncio.sleep(5)

print(f"Video: {result.video_url}")
```

---

## 📱 Instagram Optimization

### Automatic Optimization

Videos are automatically optimized for Instagram:

- **Aspect Ratio**: 9:16 (vertical)
- **Resolution**: 1080x1920
- **Duration**: 15-30 seconds (optimal)
- **File Size**: Under 100MB
- **Format**: MP4

### Platform Specifications

```python
from content.video_utils import VideoOptimizer

optimizer = VideoOptimizer()

# Get Instagram Reels specs
specs = optimizer.get_platform_specs("instagram", "reels")
print(specs)
# {
#   "aspect_ratio": "9:16",
#   "width": 1080,
#   "height": 1920,
#   "max_duration": 90,
#   "min_duration": 3,
#   "max_file_size_mb": 100
# }

# Get optimal parameters
params = optimizer.get_optimal_params("instagram", "reels")
print(params)
# {
#   "duration": 15,
#   "aspect_ratio": "9:16",
#   "width": 1080,
#   "height": 1920,
#   "format": "mp4",
#   "fps": 30
# }
```

---

## 🔄 Provider Failover

### Automatic Failover

If a provider fails, the system automatically tries the next provider:

1. **Kling** (priority 1, free) → fails
2. **Pika** (priority 2, $0.50) → tries next
3. **Runway** (priority 3, $1.50) → succeeds

### Configuration

```json
{
  "video_generation": {
    "default_provider": "kling",
    "fallback_providers": ["pika", "runway"],
    "providers": {
      "kling": {"enabled": true, "priority": 1},
      "pika": {"enabled": true, "priority": 2},
      "runway": {"enabled": true, "priority": 3}
    }
  }
}
```

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. "No API key found for provider"

**Solution**: Add API key to `.env` file:
```bash
KLING_API_KEY=your-api-key-here
```

#### 2. "Budget limit reached"

**Solution**: Increase budget limits in `config/video_config.json`:
```json
{
  "budget": {
    "daily_limit_usd": 20.0,
    "monthly_limit_usd": 400.0
  }
}
```

#### 3. "All providers failed"

**Solution**: 
- Check API keys are valid
- Verify provider accounts have credits
- Check rate limits in provider dashboards
- Review error logs for specific failures

#### 4. "Video generation timeout"

**Solution**: Videos take 30-60 seconds to generate. If timeout occurs:
- Increase timeout in code
- Check provider status pages
- Try a different provider

---

## 📈 Scaling Recommendations

### Phase 1: Testing (Free Tier)
- **Provider**: Kling (free)
- **Volume**: 5-10 videos/day
- **Cost**: $0/month
- **Best For**: Development, testing

### Phase 2: Growth ($50-100/mo)
- **Providers**: Kling + Pika
- **Volume**: 50-100 videos/month
- **Cost**: $50-100/month
- **Best For**: Early content creation

### Phase 3: Scale ($200-500/mo)
- **Providers**: Kling + Pika + Runway
- **Volume**: 200-300 videos/month
- **Cost**: $200-500/month
- **Best For**: Regular posting schedule

### Phase 4: Professional ($500+/mo)
- **Providers**: All (including HeyGen for avatar)
- **Volume**: 500+ videos/month
- **Cost**: $500-2000/month
- **Best For**: Multiple accounts, high volume

---

## 🔐 Security Best Practices

1. **Never commit API keys** - Use environment variables only
2. **Rotate keys regularly** - Change API keys every 3-6 months
3. **Monitor usage** - Set up alerts for unusual spending
4. **Use rate limiting** - Prevent API abuse
5. **Validate inputs** - Sanitize prompts and parameters
6. **Secure database** - Encrypt sensitive data at rest

---

## 🧪 Testing

### Unit Tests

```bash
pytest tests/test_video_generator.py -v
```

### Integration Tests

```bash
pytest tests/test_video_integration.py -v
```

### Manual Testing

```python
# Test provider connection
from content.video_providers import KlingProvider

provider = KlingProvider(api_key=os.getenv("KLING_API_KEY"))
result = await provider.generate_video(
    prompt="Test video",
    duration=5
)
print(f"Status: {result.status}")
```

---

## 📞 Support

### Getting Help

1. **Check logs**: Review logs in `logs/` directory
2. **Review analytics**: Check `data/reports/video_analytics/`
3. **Provider docs**: Consult provider-specific documentation
4. **Issue tracker**: Open GitHub issue with logs and config

### Useful Commands

```bash
# View recent logs
tail -f logs/orchestrator.log

# Check database
sqlite3 data/influencer.db "SELECT * FROM video_generations ORDER BY created_at DESC LIMIT 10"

# Generate analytics report
python -c "from analytics.video_analytics import VideoAnalytics; from core.database import Database; analytics = VideoAnalytics(Database()); print(analytics.get_cost_summary(30))"
```

---

## 🎓 Advanced Usage

### Custom Providers

To add a new provider:

1. Create provider class:
```python
from content.video_providers.base_provider import BaseVideoProvider

class MyProvider(BaseVideoProvider):
    async def generate_video(self, prompt, **kwargs):
        # Implementation
        pass
```

2. Register provider:
```python
from content.video_providers import VideoProviderRegistry

VideoProviderRegistry.register_provider("myprovider", MyProvider)
```

3. Configure in `video_config.json`:
```json
{
  "providers": {
    "myprovider": {
      "enabled": true,
      "priority": 5,
      "cost_per_video": 1.0
    }
  }
}
```

### Custom Analytics

```python
from analytics.video_analytics import VideoAnalytics

class CustomVideoAnalytics(VideoAnalytics):
    def get_custom_metrics(self):
        # Custom analysis
        pass
```

---

## 🔮 Future Enhancements

- **A/B Testing**: Automatically test different video styles
- **Predictive Analytics**: Predict which trends will go viral
- **Custom Model Training**: Fine-tune on your best videos
- **Multi-language Support**: Generate videos in multiple languages
- **Advanced Scheduling**: Smart posting times based on engagement
- **Video Editing**: Automated editing and effects
- **Music Integration**: Add trending audio tracks

---

## 📄 License

This video generation system is part of the AI Influencer project. See main project LICENSE for details.

---

## 🙏 Credits

- **Kling AI**: Free tier video generation
- **Pika Labs**: Stylized video generation
- **Runway ML**: Professional video generation
- **HeyGen**: AI avatar videos
- **MoviePy**: Video processing library
- **aiohttp**: Async HTTP client
