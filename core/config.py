"""
Configuration management for the autonomous influencer system
"""

import os
from pathlib import Path
from typing import Any, Dict
import json

class Config:
    """Configuration manager"""
    
    def __init__(self, config_file: str = "config/config.json"):
        self.config_file = Path(config_file)
        self.config_data = {}
        self._load_config()
        self._load_env()
    
    def _load_config(self):
        """Load configuration from JSON file"""
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                self.config_data = json.load(f)
        else:
            # Default configuration
            self.config_data = self._get_default_config()
            self._save_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
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
    
    def _load_env(self):
        """Load environment variables and override config"""
        # API Keys
        self.config_data["api_keys"] = {
            "openai": os.getenv("OPENAI_API_KEY", ""),
            "stability": os.getenv("STABILITY_API_KEY", ""),
            "instagram": os.getenv("INSTAGRAM_ACCESS_TOKEN", ""),
            "twitter": os.getenv("TWITTER_BEARER_TOKEN", ""),
            "tiktok": os.getenv("TIKTOK_ACCESS_TOKEN", "")
        }
    
    def _save_config(self):
        """Save configuration to file"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump(self.config_data, f, indent=2)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key_path.split(".")
        value = self.config_data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key_path.split(".")
        config = self.config_data
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
        self._save_config()
