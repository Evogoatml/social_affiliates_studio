#!/usr/bin/env python3
"""
Interactive Setup Wizard for Autonomous Influencer System
"""

import os
import sys
from pathlib import Path
import json
from typing import Dict

def print_header():
    """Print welcome header"""
    print("\n" + "="*60)
    print("  🤖 AUTONOMOUS INFLUENCER SYSTEM - SETUP WIZARD")
    print("="*60 + "\n")

def print_section(title: str):
    """Print section header"""
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}\n")

def get_input(prompt: str, default: str = "", required: bool = False) -> str:
    """Get user input with optional default"""
    if default:
        prompt_text = f"{prompt} [{default}]: "
    else:
        prompt_text = f"{prompt}: "
    
    while True:
        value = input(prompt_text).strip()
        if not value and default:
            return default
        if not value and required:
            print("❌ This field is required. Please provide a value.")
            continue
        return value

def get_yes_no(prompt: str, default: bool = True) -> bool:
    """Get yes/no input"""
    default_str = "Y/n" if default else "y/N"
    while True:
        response = input(f"{prompt} [{default_str}]: ").strip().lower()
        if not response:
            return default
        if response in ['y', 'yes']:
            return True
        if response in ['n', 'no']:
            return False
        print("❌ Please answer 'yes' or 'no'")

def setup_api_keys() -> Dict[str, str]:
    """Setup API keys"""
    print_section("🔑 API KEYS CONFIGURATION")
    
    print("The system supports multiple AI services for content generation.")
    print("You can configure them now or add them later to the .env file.\n")
    
    api_keys = {}
    
    # OpenAI
    if get_yes_no("Configure OpenAI API? (Recommended for best quality)"):
        key = get_input("OpenAI API Key", required=True)
        api_keys["OPENAI_API_KEY"] = key
        print("✅ OpenAI configured\n")
    
    # Stability AI
    if get_yes_no("Configure Stability AI? (For image generation alternative)"):
        key = get_input("Stability AI API Key")
        if key:
            api_keys["STABILITY_API_KEY"] = key
            print("✅ Stability AI configured\n")
    
    return api_keys

def setup_social_platforms() -> Dict[str, str]:
    """Setup social media platforms"""
    print_section("📱 SOCIAL MEDIA PLATFORMS")
    
    print("Configure access tokens for automated posting.")
    print("You can skip this and run in simulation mode initially.\n")
    
    platforms = {}
    
    # Instagram
    if get_yes_no("Configure Instagram?"):
        print("\nℹ️  Get your Instagram Access Token from:")
        print("   https://developers.facebook.com/docs/instagram-api/")
        token = get_input("Instagram Access Token")
        if token:
            platforms["INSTAGRAM_ACCESS_TOKEN"] = token
            print("✅ Instagram configured\n")
    
    # Twitter
    if get_yes_no("Configure Twitter/X?"):
        print("\nℹ️  Get your Twitter API credentials from:")
        print("   https://developer.twitter.com/")
        token = get_input("Twitter Bearer Token")
        if token:
            platforms["TWITTER_BEARER_TOKEN"] = token
            print("✅ Twitter configured\n")
    
    # TikTok
    if get_yes_no("Configure TikTok?"):
        print("\nℹ️  Get your TikTok API credentials from:")
        print("   https://developers.tiktok.com/")
        token = get_input("TikTok Access Token")
        if token:
            platforms["TIKTOK_ACCESS_TOKEN"] = token
            print("✅ TikTok configured\n")
    
    return platforms

def setup_avatar_preferences() -> Dict[str, str]:
    """Setup avatar preferences"""
    print_section("🎨 AVATAR CONFIGURATION")
    
    print("Configure your AI influencer avatar appearance and personality.\n")
    
    preferences = {
        "AVATAR_PERSONALITY": get_input(
            "Personality traits",
            default="friendly, professional, engaging"
        ),
        "AVATAR_AGE_RANGE": get_input(
            "Age range",
            default="25-35"
        ),
        "AVATAR_GENDER": get_input(
            "Gender",
            default="neutral"
        ),
        "AVATAR_ETHNICITY": get_input(
            "Ethnicity",
            default="diverse"
        ),
        "AVATAR_STYLE": get_input(
            "Visual style",
            default="realistic"
        )
    }
    
    print("✅ Avatar preferences saved\n")
    return preferences

def setup_marketing_strategy() -> Dict[str, str]:
    """Setup marketing strategy"""
    print_section("📊 MARKETING STRATEGY")
    
    print("Define your influencer's niche and target audience.\n")
    
    strategy = {
        "MARKETING_NICHE": get_input(
            "Primary niche (e.g., lifestyle, fitness, tech)",
            default="lifestyle",
            required=True
        ),
        "TARGET_AUDIENCE": get_input(
            "Target audience",
            default="18-35 professionals",
            required=True
        ),
        "CONTENT_THEMES": get_input(
            "Content themes (comma-separated)",
            default="motivation,lifestyle,tips,behind-the-scenes"
        ),
        "POSTING_FREQUENCY": get_input(
            "Posting frequency",
            default="daily"
        )
    }
    
    print("✅ Marketing strategy configured\n")
    return strategy

def setup_content_preferences() -> Dict[str, str]:
    """Setup content generation preferences"""
    print_section("📝 CONTENT PREFERENCES")
    
    print("Configure content generation preferences.\n")
    
    preferences = {
        "VIDEO_RATIO": get_input(
            "Video content ratio (0.0-1.0)",
            default="0.3"
        ),
        "CAROUSEL_RATIO": get_input(
            "Carousel content ratio (0.0-1.0)",
            default="0.4"
        ),
        "AUTO_RESPOND_COMMENTS": "true" if get_yes_no(
            "Auto-respond to comments?",
            default=True
        ) else "false"
    }
    
    print("✅ Content preferences configured\n")
    return preferences

def create_env_file(config: Dict[str, str]):
    """Create .env file with configuration"""
    env_file = Path(".env")
    
    if env_file.exists():
        if not get_yes_no("⚠️  .env file already exists. Overwrite?", default=False):
            print("ℹ️  Skipping .env file creation")
            return
    
    with open(env_file, "w") as f:
        f.write("# Autonomous Influencer System Configuration\n")
        f.write(f"# Generated on {Path.cwd()}\n\n")
        
        # API Keys
        f.write("# ===== API KEYS =====\n")
        for key, value in config.items():
            if "API_KEY" in key or "TOKEN" in key:
                f.write(f"{key}={value}\n")
        
        f.write("\n# ===== AVATAR CONFIGURATION =====\n")
        for key, value in config.items():
            if key.startswith("AVATAR_"):
                f.write(f"{key}={value}\n")
        
        f.write("\n# ===== MARKETING STRATEGY =====\n")
        for key, value in config.items():
            if key.startswith("MARKETING_") or key.startswith("TARGET_") or key.startswith("CONTENT_"):
                f.write(f"{key}={value}\n")
        
        f.write("\n# ===== CONTENT PREFERENCES =====\n")
        for key, value in config.items():
            if key.endswith("_RATIO") or key.startswith("AUTO_"):
                f.write(f"{key}={value}\n")
        
        f.write("\n# ===== POSTING SCHEDULE =====\n")
        for key, value in config.items():
            if key.startswith("POSTING_"):
                f.write(f"{key}={value}\n")
    
    print(f"✅ Configuration saved to {env_file}\n")

def create_config_json():
    """Create default config.json"""
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / "config.json"
    
    if config_file.exists():
        if not get_yes_no("⚠️  config/config.json already exists. Overwrite?", default=False):
            return
    
    default_config = {
        "avatar": {
            "personality": "friendly, professional, engaging",
            "age_range": "25-35",
            "gender": "neutral",
            "ethnicity": "diverse",
            "style": "realistic"
        },
        "marketing": {
            "goals": ["grow followers", "increase engagement", "build brand"],
            "niche": "lifestyle",
            "target_audience": "18-35 professionals",
            "content_themes": ["motivation", "lifestyle", "tips", "behind-the-scenes"]
        },
        "social": {
            "platforms": ["instagram", "twitter", "tiktok"],
            "posting_times": {
                "instagram": ["09:00", "18:00"],
                "twitter": ["08:00", "12:00", "20:00"],
                "tiktok": ["19:00"]
            },
            "auto_respond": True,
            "engagement_rate_target": 0.05
        },
        "content": {
            "post_frequency": "daily",
            "video_ratio": 0.3,
            "carousel_ratio": 0.4,
            "single_image_ratio": 0.3,
            "hashtag_count": {
                "instagram": 20,
                "twitter": 5,
                "tiktok": 10
            }
        },
        "analytics": {
            "track_engagement": True,
            "track_growth": True,
            "optimization_frequency": "daily"
        }
    }
    
    with open(config_file, "w") as f:
        json.dump(default_config, f, indent=2)
    
    print(f"✅ Default configuration saved to {config_file}\n")

def check_dependencies():
    """Check and install dependencies"""
    print_section("📦 DEPENDENCIES CHECK")
    
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return
    
    if get_yes_no("Install Python dependencies now?", default=True):
        print("\nInstalling dependencies...")
        os.system(f"{sys.executable} -m pip install -r requirements.txt")
        print("✅ Dependencies installed\n")
    else:
        print(f"\nℹ️  You can install dependencies later with:")
        print(f"   pip install -r requirements.txt\n")

def create_directories():
    """Create necessary directories"""
    print_section("📁 DIRECTORY SETUP")
    
    directories = [
        "data/avatars",
        "data/content",
        "data/media/images",
        "data/media/videos",
        "data/media/thumbnails",
        "data/posts",
        "data/analytics",
        "data/strategies",
        "logs",
        "config"
    ]
    
    print("Creating directory structure...")
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directory structure created\n")

def print_next_steps():
    """Print next steps"""
    print_section("🚀 SETUP COMPLETE!")
    
    print("Your autonomous influencer system is ready to start!")
    print("\nNext steps:")
    print("  1. Review your configuration in .env and config/config.json")
    print("  2. Add any missing API keys to .env")
    print("  3. Run the system:")
    print("     python app.py")
    print("\nFor simulation mode (no actual posting):")
    print("  - The system will generate content and simulate posts")
    print("  - Add API credentials later for real posting")
    print("\nDocumentation:")
    print("  - Check README.md for detailed information")
    print("  - Visit docs/ for advanced configuration")
    print("\n" + "="*60 + "\n")

def main():
    """Main setup wizard"""
    print_header()
    
    print("This wizard will help you configure your autonomous influencer system.")
    print("You can always change these settings later in .env and config/config.json")
    print()
    
    if not get_yes_no("Continue with setup?", default=True):
        print("\nSetup cancelled. You can run this wizard again anytime.")
        return
    
    # Collect all configuration
    config = {}
    
    # Create directories first
    create_directories()
    
    # API Keys
    config.update(setup_api_keys())
    
    # Social Platforms
    config.update(setup_social_platforms())
    
    # Avatar
    config.update(setup_avatar_preferences())
    
    # Marketing Strategy
    config.update(setup_marketing_strategy())
    
    # Content Preferences
    config.update(setup_content_preferences())
    
    # Create configuration files
    create_env_file(config)
    create_config_json()
    
    # Dependencies
    check_dependencies()
    
    # Final steps
    print_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted. You can run this wizard again anytime.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        sys.exit(1)
