# 🤖 Autonomous Influencer System with AI Training

A complete AI-powered system that creates and manages a life-like social media influencer autonomously. This system generates avatars, creates engaging content, posts to multiple platforms, scrapes viral content, trains ML models, and optimizes strategy based on analytics — all running autonomously with continuous learning from trending content.

## ✨ Features

### 🎨 Avatar Generation
- Creates photorealistic AI avatars using DALL-E 3 or Stability AI
- Customizable personality, age, gender, and style
- Generates variations for different content types

### 📝 Content Creation
- **Autonomous Content Generation**: Creates posts, captions, and hashtags
- **Multi-Format Support**: Images, carousels, and videos
- **AI-Powered Writing**: Uses GPT-4 for engaging, platform-optimized content
- **Media Generation**: Automatic image creation for every post
- **Theme-Based Content**: Motivation, lifestyle, tips, and more

### 📱 Multi-Platform Posting
- **Instagram**: Feed posts, stories, and reels
- **Twitter/X**: Tweets and threads
- **TikTok**: Short-form videos
- **Scheduled Posting**: Optimal timing for each platform
- **Simulation Mode**: Test without actual posting

### 📊 Analytics & Optimization
- Tracks engagement metrics (likes, comments, shares)
- Identifies top and low-performing content
- Analyzes best posting times
- Automatically optimizes strategy based on performance
- Growth tracking

### 🔥 Viral Content Intelligence
- **Automated Scraping**: Collects trending content from Instagram, TikTok, Twitter
- **Pattern Analysis**: Identifies what makes content go viral
- **Trend Tracking**: Monitors hashtags, topics, and posting times
- **Database Storage**: Stores all viral data for training
- **AI Strategy Optimization**: Uses GPT-4 to analyze trends and optimize content strategy

### 🎓 Machine Learning & Training
- **Hugging Face Integration**: Fine-tune models on viral content
- **Caption Generation**: Train custom models for platform-specific captions
- **Engagement Prediction**: ML models predict content performance
- **Hashtag Recommendation**: AI-powered hashtag suggestions
- **Continuous Learning**: Automatically retrains models weekly on new data
- **Model Management**: Version control, A/B testing, deployment

### 🎛️ Human-in-the-Loop Dashboard
- **Web Interface**: Real-time monitoring and control
- **Approval Workflow**: Review and approve content before posting
- **Live Metrics**: View engagement, content queue, and system status
- **Manual Override**: Take control when needed
- **Notification System**: Get alerts for pending approvals

### 🔄 Autonomous Operation
- Runs continuously without human intervention
- Generates content batches ahead of time
- Schedules and posts automatically
- Adapts strategy based on analytics
- Self-optimizing marketing approach

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key (recommended)
- Optional: Stability AI, social media API credentials

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd webapp
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the setup wizard**
```bash
python setup_wizard.py
```

The setup wizard will guide you through:
- API key configuration
- Avatar customization
- Marketing strategy setup
- Social media platform connection
- Content preferences

4. **Start the system**
```bash
python app.py
```

5. **Optional: Start the HITL Dashboard**
```bash
cd dashboard
python server.py
# Visit http://localhost:5000 for web interface
```

6. **Optional: Train ML Models**
```bash
# See docs/ML_TRAINING_GUIDE.md for full guide
python -c "from ml.training import setup_training_pipeline; from core.config import Config; from core.database import Database; setup_training_pipeline(Config(), Database())"
```

### Manual Configuration

If you prefer manual setup, create a `.env` file:

```env
# API Keys
OPENAI_API_KEY=your_openai_key_here
STABILITY_API_KEY=your_stability_key_here

# Social Media (optional - leave empty for simulation mode)
INSTAGRAM_ACCESS_TOKEN=your_instagram_token
TWITTER_BEARER_TOKEN=your_twitter_token
TIKTOK_ACCESS_TOKEN=your_tiktok_token

# Avatar Configuration
AVATAR_PERSONALITY=friendly, professional, engaging
AVATAR_AGE_RANGE=25-35
AVATAR_GENDER=neutral
AVATAR_STYLE=realistic

# Marketing Strategy
MARKETING_NICHE=lifestyle
TARGET_AUDIENCE=18-35 professionals
CONTENT_THEMES=motivation,lifestyle,tips,behind-the-scenes

# Content Preferences
VIDEO_RATIO=0.3
CAROUSEL_RATIO=0.4
POSTING_FREQUENCY=daily
```

## 📁 Project Structure

```
webapp/
├── app.py                      # Main entry point
├── setup_wizard.py             # Interactive setup
├── README.md                   # This file
├── requirements.txt            # Python dependencies
│
├── core/                       # Core system components
│   ├── orchestrator.py         # Main system orchestrator
│   ├── config.py               # Configuration management
│   ├── logger.py               # Logging setup
│   ├── database.py             # SQLite database
│   └── utils.py                # Utility functions
│
├── avatar/                     # Avatar generation
│   └── avatar_generator.py     # AI avatar creation
│
├── content/                    # Content generation
│   ├── content_engine.py       # Content generation
│   └── media_generator.py      # Image/video generation
│
├── marketing/                  # Marketing strategy
│   └── strategy_planner.py     # Marketing strategy
│
├── social/                     # Social media posting
│   └── social_manager.py       # Multi-platform posting
│
├── analytics/                  # Analytics & intelligence
│   ├── analytics_engine.py     # Performance tracking
│   ├── viral_scraper.py        # Viral content scraper
│   └── viral_intelligence.py   # AI strategy optimizer
│
├── ml/                         # Machine learning
│   ├── training.py             # Model training
│   ├── dataset_builder.py      # Dataset preparation
│   ├── model_manager.py        # Model versioning
│   ├── models/                 # Trained models
│   ├── datasets/               # Training datasets
│   └── logs/                   # Training logs
│
├── dashboard/                  # HITL dashboard
│   ├── server.py               # Flask server
│   ├── templates/              # HTML templates
│   └── static/                 # CSS/JS assets
│
├── docs/                       # Documentation
│   ├── ML_TRAINING_GUIDE.md    # ML training setup
│   ├── VIRAL_INTELLIGENCE.md   # Viral scraping docs
│   ├── HITL_DASHBOARD.md       # Dashboard docs
│   ├── PROJECT_STATUS.md       # Project status
│   └── HUGGINGFACE_INTEGRATION.md  # HF integration
│
├── config/                     # Configuration files
│   ├── config.json             # System config
│   ├── agents.yaml             # Agent definitions
│   └── *.json                  # Other configs
│
├── scripts/                    # Utility scripts
│   ├── python_utils/           # Python utilities
│   └── *.sh                    # Shell scripts
│
├── data/                       # Generated data
│   ├── avatars/                # Avatar images
│   ├── content/                # Generated content
│   ├── media/                  # Generated media
│   ├── posts/                  # Posted content records
│   ├── analytics/              # Analytics data
│   ├── strategies/             # Marketing strategies
│   └── influencer.db           # SQLite database
│
└── logs/                       # System logs
```

## 🎯 Usage

### Running in Simulation Mode

Perfect for testing without actual social media posting:

```bash
# No API credentials required - system will simulate posts
python app.py
```

The system will:
- Generate avatar (placeholder if no API keys)
- Create content with captions and hashtags
- Generate media descriptions
- Simulate posting to platforms
- Track metrics locally

### Running with Live Posting

Configure API credentials in `.env` and the system will:
- Actually post to connected platforms
- Track real engagement metrics
- Optimize based on actual performance

### Monitoring the System

Check the logs:
```bash
tail -f logs/influencer_*.log
```

View generated content:
```bash
ls -la data/content/
```

Check posted content:
```bash
ls -la data/posts/
```

## 🔧 Configuration

### Avatar Customization

Edit `config/config.json` or use environment variables:

```json
{
  "avatar": {
    "personality": "friendly, professional, engaging",
    "age_range": "25-35",
    "gender": "neutral",
    "ethnicity": "diverse",
    "style": "realistic"
  }
}
```

### Content Strategy

```json
{
  "content": {
    "post_frequency": "daily",
    "video_ratio": 0.3,
    "carousel_ratio": 0.4,
    "single_image_ratio": 0.3
  }
}
```

### Posting Schedule

```json
{
  "social": {
    "posting_times": {
      "instagram": ["09:00", "18:00"],
      "twitter": ["08:00", "12:00", "20:00"],
      "tiktok": ["19:00"]
    }
  }
}
```

## 🔌 API Integration

### Instagram

1. Create a Facebook Developer account
2. Set up an Instagram Business Account
3. Generate access token via Graph API
4. Add to `.env`: `INSTAGRAM_ACCESS_TOKEN=your_token`

[Instagram API Documentation](https://developers.facebook.com/docs/instagram-api/)

### Twitter/X

1. Apply for Twitter Developer access
2. Create a project and app
3. Generate Bearer Token
4. Add to `.env`: `TWITTER_BEARER_TOKEN=your_token`

[Twitter API Documentation](https://developer.twitter.com/en/docs)

### TikTok

1. Register for TikTok for Developers
2. Create an app
3. Request Content Posting API access
4. Add to `.env`: `TIKTOK_ACCESS_TOKEN=your_token`

[TikTok API Documentation](https://developers.tiktok.com/doc/content-posting-api-get-started)

## 📊 Analytics

The system automatically tracks:
- **Engagement Metrics**: Likes, comments, shares, views
- **Performance Analysis**: Top and low-performing content
- **Timing Optimization**: Best posting times per platform
- **Growth Tracking**: Follower and reach trends

View analytics:
```bash
cat data/analytics/metrics.json
```

## 🤝 Advanced Features

### Custom Content Themes

Add custom themes in `marketing/strategy_planner.py`:

```python
niche_topics = {
    "your_niche": ["topic1", "topic2", "topic3"]
}
```

### Custom Posting Logic

Modify `social/social_manager.py` to add custom posting logic for each platform.

### Content Filtering

Add content approval workflow before posting in `core/orchestrator.py`.

## 🧪 Development

### Running Tests

```bash
python -m pytest tests/
```

### Adding New Features

1. Create feature branch
2. Implement changes
3. Add tests
4. Update documentation
5. Submit pull request

## 📝 System Requirements

### Minimum
- Python 3.8+
- 2GB RAM
- 1GB disk space

### Recommended
- Python 3.10+
- 4GB RAM
- 5GB disk space (for media storage)
- OpenAI API access

## 🐛 Troubleshooting

### "No API key configured"
- Run `python setup_wizard.py` to configure API keys
- Or manually add keys to `.env` file

### "Failed to generate avatar"
- Check OpenAI or Stability AI API key
- System will use placeholder mode if APIs unavailable

### "Post failed"
- Check social media API credentials
- Verify platform API quotas
- System runs in simulation mode if credentials missing

### Log files not created
- Ensure `logs/` directory exists
- Check file permissions

## 🔒 Security

- **API Keys**: Never commit `.env` file to version control
- **Credentials**: Store securely, rotate regularly
- **Rate Limiting**: System respects platform API limits
- **Data Privacy**: All data stored locally

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

- Documentation: Check `docs/` folder
- Issues: Submit via GitHub Issues
- Questions: See FAQ in `docs/FAQ.md`

## 🙏 Acknowledgments

- OpenAI for GPT and DALL-E APIs
- Stability AI for image generation
- Social media platform APIs

## 🎯 Roadmap

- [x] ✅ Web dashboard for monitoring (HITL Dashboard)
- [x] ✅ Advanced image/video generation
- [x] ✅ Viral content scraping
- [x] ✅ ML model training and fine-tuning
- [x] ✅ Database integration (SQLite)
- [ ] Multi-language support
- [ ] Community management features
- [ ] A/B testing for content
- [ ] Influencer collaboration tools
- [ ] Mobile app
- [ ] Advanced video generation with AI
- [ ] Real-time engagement tracking
- [ ] Competitor analysis module

## ⚡ Performance Tips

1. **Batch Content Generation**: System generates content in batches for efficiency
2. **Media Caching**: Reuse generated media when appropriate
3. **API Rate Limits**: System automatically handles rate limiting
4. **Resource Management**: Monitor disk space for media storage

## 🌟 Best Practices

1. **Start Small**: Begin with one platform, expand gradually
2. **Monitor Performance**: Check analytics regularly
3. **Adjust Strategy**: Let the system optimize automatically
4. **Quality Over Quantity**: Better to post less with higher quality
5. **Engage Authentically**: Even AI influencers need genuine connection

---

**Made with ❤️ by the Autonomous Systems Team**

For more information, visit our [documentation](docs/) or [website](https://example.com).
