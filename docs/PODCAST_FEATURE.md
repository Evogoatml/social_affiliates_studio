# 🎙️ AI Podcast Feature - Daily Viral Trends Show

## Overview

Your AI influencer now hosts a **daily podcast** that runs for 1-2 hours every night, discussing:
- Today's viral content analysis
- Trending topics and hashtags
- Trendsetting strategies and techniques
- Platform-specific insights
- How to become a trendsetter, not just a follower

---

## 🎯 Features

### Automated Daily Episodes
- **Generated Every Night**: Default 9 PM (configurable)
- **Duration**: 60-120 minutes (1-2 hours)
- **AI-Powered**: Uses GPT-4 for script generation
- **High-Quality Audio**: OpenAI TTS with HD voice
- **Data-Driven**: Based on real viral content scraped daily

### Content Structure

Each episode includes **7 segments**:

1. **Intro & Welcome** (5 min)
   - Welcoming greeting
   - Overview of today's topics
   - What to expect

2. **Today's Viral Breakdown** (20-30 min)
   - Analysis of top viral posts
   - Why they went viral
   - Engagement patterns
   - Platform-specific strategies

3. **Trending Hashtags & Topics** (15-20 min)
   - Current trending hashtags
   - Topic analysis
   - How to leverage trends

4. **Trendsetting Strategies** (25-30 min)
   - How to create trends, not follow them
   - Innovation techniques
   - Standing out strategies
   - Real examples from data

5. **Platform Deep Dive** (15-20 min)
   - Instagram-specific insights
   - TikTok strategies
   - Twitter/X tactics
   - Cross-platform approach

6. **Listener Q&A & Rapid-Fire Tips** (7-10 min)
   - Common questions answered
   - Quick actionable tips
   - Pro strategies

7. **Wrap-Up & Daily Challenge** (3-5 min)
   - Episode summary
   - Tomorrow's trendsetting challenge
   - Call-to-action

---

## 🚀 Quick Start

### 1. Enable Podcast Generation

Add to your `.env` file:
```bash
# Podcast Configuration
PODCAST_ENABLED=true
PODCAST_DURATION=90
PODCAST_SCHEDULE_TIME=21:00  # 9 PM
PODCAST_VOICE=nova  # Options: nova, alloy, echo, fable, onyx, shimmer
```

### 2. Configure in config.json

```json
{
  "podcast": {
    "enabled": true,
    "duration_minutes": 90,
    "scheduled_time": "21:00",
    "voice": "nova",
    "platforms": ["spotify", "apple_podcasts", "youtube", "soundcloud"],
    "auto_publish": false
  }
}
```

### 3. Generate Your First Episode

```python
# Test podcast generation manually
python -c "
import asyncio
from content.podcast_generator import PodcastGenerator
from core.config import Config
from core.database import Database

async def test():
    config = Config()
    database = Database()
    generator = PodcastGenerator(config, database, None)
    
    result = await generator.generate_daily_podcast(
        duration_minutes=90,
        topic_focus='How to become a viral content creator'
    )
    
    print(result)

asyncio.run(test())
"
```

### 4. Automatic Generation

Once enabled, the system will automatically:
- Generate a new episode every day at 9 PM
- Analyze the day's viral content
- Create a structured script
- Generate high-quality audio
- Save everything to `data/podcasts/`

---

## 📂 File Structure

```
data/podcasts/
├── scripts/           # JSON scripts for each episode
│   └── 20240208_210000.json
├── audio/             # MP3 audio segments
│   ├── 20240208_210000_segment_1.mp3
│   ├── 20240208_210000_segment_2.mp3
│   └── ...
└── metadata/          # Episode metadata
    └── 20240208_210000.json
```

---

## 🎤 Voice Options

Choose from OpenAI's TTS voices:

| Voice | Description | Best For |
|-------|-------------|----------|
| **nova** | Female, friendly, clear | ✅ Recommended |
| **alloy** | Neutral, professional | Corporate content |
| **echo** | Male, deep, authoritative | Educational content |
| **fable** | Warm, storytelling | Narrative podcasts |
| **onyx** | Male, strong, confident | Motivational content |
| **shimmer** | Female, energetic | Upbeat content |

Change in `.env`:
```bash
PODCAST_VOICE=nova  # or alloy, echo, fable, onyx, shimmer
```

---

## 📊 Episode Metadata

Each episode includes:

```json
{
  "episode_id": "20240208_210000",
  "title": "Viral Trends Daily - February 8, 2024",
  "subtitle": "Analyzing today's viral content and trendsetting strategies",
  "description": "Full show notes...",
  "duration_minutes": 90,
  "segment_count": 7,
  "audio_files_count": 7,
  "created_at": "2024-02-08T21:00:00",
  "status": "generated",
  "platforms": ["spotify", "apple_podcasts", "youtube"],
  "tags": ["viral trends", "social media", "trendsetting"]
}
```

---

## 🎬 Integration with System

### Automatic Workflow

```
1. 9:00 PM - Podcast generation trigger
   ↓
2. Gather viral data from database
   ↓
3. Generate script with GPT-4 (7 segments)
   ↓
4. Generate audio with OpenAI TTS-HD
   ↓
5. Save script, audio, metadata
   ↓
6. (Optional) Auto-publish to platforms
   ↓
7. (Optional) Post announcement on social media
```

### Manual Control

```python
from content.podcast_generator import PodcastGenerator

# Initialize
generator = PodcastGenerator(config, database, viral_intelligence)

# Generate specific episode
result = await generator.generate_daily_podcast(
    duration_minutes=120,  # 2 hours
    topic_focus="TikTok viral strategies"
)

# Check if it's time to generate
if generator.should_generate_now():
    await generator.generate_daily_podcast()
```

---

## 🔄 Publishing Workflow

### Option 1: Manual Upload

1. Episode generated in `data/podcasts/audio/`
2. Combine segments (if needed):
   ```bash
   # Use ffmpeg to combine segments
   ffmpeg -i "concat:segment_1.mp3|segment_2.mp3|..." -acodec copy episode.mp3
   ```
3. Upload to podcast platforms manually
4. Add show notes from `metadata/`

### Option 2: Automated Publishing (Coming Soon)

Future features:
- ✅ Spotify API integration
- ✅ Apple Podcasts API
- ✅ YouTube API upload
- ✅ RSS feed generation
- ✅ Auto social media announcements

---

## 🎯 Customization

### Custom Script Prompts

Edit the script generation in `content/podcast_generator.py`:

```python
def _create_script_prompt(self, context, duration_minutes, topic_focus):
    # Customize the prompt structure
    # Add your own segments
    # Change tone and style
    pass
```

### Custom Segments

Modify segment structure:

```python
"segments": [
    {
        "title": "Your Custom Segment",
        "duration_minutes": 15,
        "content": "Your content template...",
        "voice_notes": "enthusiastic, engaging"
    }
]
```

### Custom Voice Style

Adjust TTS parameters:

```python
response = self.client.audio.speech.create(
    model="tts-1-hd",
    voice="nova",
    input=content,
    speed=1.1  # Slightly faster (1.0 = normal, 0.5-2.0 range)
)
```

---

## 📈 Analytics & Insights

Track podcast performance:

```python
# Get viral data used in episode
viral_data = generator._gather_viral_trends()

# Track which topics were covered
topics_covered = [seg['title'] for seg in script['segments']]

# Monitor which episodes get most engagement
# (requires platform API integration)
```

---

## 🎓 Best Practices

### Content Quality

1. **Data-Driven**: Uses real viral content data
2. **Timely**: Generated daily with latest trends
3. **Structured**: 7-segment format keeps listeners engaged
4. **Actionable**: Provides specific strategies and tips
5. **Conversational**: Natural podcast tone, not robotic

### Scheduling

- **Default 9 PM**: Good for evening listeners
- **Consistent**: Same time every day builds audience
- **Duration**: 60-90 minutes is optimal (1-2 hours max)
- **Buffer**: Generated at night, published morning

### Engagement

- **Show Notes**: Include timestamps and resources
- **Challenges**: Daily trendsetting challenge
- **Q&A**: Address common questions
- **Examples**: Reference specific viral content

---

## 🐛 Troubleshooting

### Issue: "OpenAI API not available"
```bash
# Check API key
echo $OPENAI_API_KEY

# Set in .env
OPENAI_API_KEY=sk-...
```

### Issue: "Audio generation failed"
```python
# Check TTS limits
# OpenAI TTS: 4096 characters per request
# Solution: Script is auto-split into segments
```

### Issue: "No viral data found"
```bash
# Ensure viral scraper ran
python -c "from analytics.viral_scraper import ViralContentScraper; ..."

# Check database
sqlite3 data/influencer.db "SELECT COUNT(*) FROM viral_content;"
```

### Issue: "Podcast not generating at scheduled time"
```python
# Check orchestrator is running
ps aux | grep app.py

# Verify schedule in config
cat config/config.json | grep podcast
```

---

## 💰 Cost Estimates

### Per Episode (90 minutes):

**Script Generation**:
- GPT-4: ~8,000 tokens
- Cost: ~$0.24 (at $0.03/1K tokens)

**Audio Generation**:
- 7 segments @ ~10 min each
- TTS-HD: ~$0.70 (at $0.030/1K characters)

**Total per Episode**: ~$1.00
**Monthly (30 episodes)**: ~$30.00

**Tips to Reduce Costs**:
- Use GPT-3.5 for scripts (~$0.01 per episode)
- Use standard TTS model (~$0.35 per episode)
- Reduce duration to 60 minutes

---

## 🚀 Next Steps

### Immediate:
1. ✅ Enable podcast in config
2. ✅ Test generation manually
3. ✅ Review first episode
4. ✅ Adjust settings as needed

### Short Term:
5. Set up RSS feed
6. Upload to podcast platforms
7. Announce on social media
8. Build listener base

### Long Term:
9. Automate publishing workflow
10. Add listener analytics
11. Integrate feedback loops
12. Expand to multiple shows

---

## 📚 Resources

### Documentation
- Script Generator: `content/podcast_generator.py`
- Orchestrator Integration: `core/orchestrator.py`
- Configuration: `config/config.json`

### APIs Used
- **OpenAI GPT-4**: Script generation
- **OpenAI TTS-HD**: Audio generation
- **Database**: Viral content storage

### External Links
- [OpenAI TTS Docs](https://platform.openai.com/docs/guides/text-to-speech)
- [Podcast Distribution Guide](https://podcasters.spotify.com/)
- [RSS Feed Spec](https://www.rssboard.org/rss-specification)

---

## 🎊 Example Output

**Episode**: "Viral Trends Daily - February 8, 2024"

**Segments Generated**:
1. ✅ Intro & Welcome (5 min)
2. ✅ Today's Viral Breakdown (25 min)
3. ✅ Trending Hashtags (15 min)
4. ✅ Trendsetting Strategies (30 min)
5. ✅ Platform Deep Dive (10 min)
6. ✅ Quick Tips (5 min)
7. ✅ Wrap-Up & Challenge (3 min)

**Total Duration**: 93 minutes
**Audio Files**: 7 MP3 segments
**Script**: Structured JSON
**Cost**: ~$1.00

---

## ✅ Quick Checklist

```
□ Add OPENAI_API_KEY to .env
□ Enable podcast in config
□ Test manual generation
□ Verify audio quality
□ Review episode structure
□ Adjust voice/duration settings
□ Set up automated schedule
□ Plan publishing workflow
□ Create RSS feed
□ Upload to platforms
□ Announce first episode
□ Monitor engagement
```

---

**Your AI influencer is now a podcast host! 🎙️**

Every night, it will analyze the day's viral trends and create an engaging, insightful episode for your audience. Turn it on and watch your podcast library grow!
