"""
Avatar Generator - Creates life-like avatars using AI
"""

import os
import requests
from pathlib import Path
from typing import Dict, Optional
import json

from core.logger import setup_logger
from core.config import Config

logger = setup_logger(__name__)

class AvatarGenerator:
    """Generates and manages life-like avatars"""
    
    def __init__(self, config: Config):
        self.config = config
        self.avatar_data = {}
        self.avatar_dir = Path("data/avatars")
        self.avatar_dir.mkdir(parents=True, exist_ok=True)
    
    async def create_avatar(self, config: Dict) -> Optional[Dict]:
        """Create a life-like avatar based on configuration"""
        logger.info(f"🎨 Creating avatar with config: {config}")
        
        # Try multiple methods
        avatar_data = None
        
        # Method 1: OpenAI DALL-E (if available)
        if self.config.get("api_keys.openai"):
            avatar_data = await self._create_with_openai(config)
        
        # Method 2: Stability AI (if available)
        if not avatar_data and self.config.get("api_keys.stability"):
            avatar_data = await self._create_with_stability(config)
        
        # Method 3: Fallback to local generation or placeholder
        if not avatar_data:
            avatar_data = await self._create_placeholder(config)
        
        if avatar_data:
            self.avatar_data = avatar_data
            await self._save_avatar_data(avatar_data)
            logger.info("✅ Avatar created successfully")
        
        return avatar_data
    
    async def _create_with_openai(self, config: Dict) -> Optional[Dict]:
        """Create avatar using OpenAI DALL-E"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.config.get("api_keys.openai"))
            
            prompt = self._build_avatar_prompt(config)
            
            logger.info("🖼️ Generating avatar with DALL-E...")
            
            response = client.images.generate(
                prompt=prompt,
                n=1,
                size="1024x1024",
                model="dall-e-3"
            )
            
            image_url = response.data[0].url
            
            # Download image
            image_path = await self._download_image(image_url, "avatar_main.png")
            
            return {
                "id": "avatar_001",
                "image_path": str(image_path),
                "image_url": image_url,
                "prompt": prompt,
                "config": config,
                "created_at": str(Path().cwd())
            }
            
        except Exception as e:
            logger.warning(f"OpenAI avatar generation failed: {e}")
            return None
    
    async def _create_with_stability(self, config: Dict) -> Optional[Dict]:
        """Create avatar using Stability AI"""
        try:
            api_key = self.config.get("api_keys.stability")
            prompt = self._build_avatar_prompt(config)
            
            logger.info("🖼️ Generating avatar with Stability AI...")
            
            response = requests.post(
                "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "text_prompts": [{"text": prompt, "weight": 1}],
                    "cfg_scale": 7,
                    "height": 1024,
                    "width": 1024,
                    "samples": 1,
                    "steps": 30
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                image_base64 = result["artifacts"][0]["base64"]
                
                # Save image
                image_path = await self._save_base64_image(image_base64, "avatar_main.png")
                
                return {
                    "id": "avatar_001",
                    "image_path": str(image_path),
                    "prompt": prompt,
                    "config": config,
                    "created_at": str(Path().cwd())
                }
            else:
                logger.warning(f"Stability AI request failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.warning(f"Stability AI avatar generation failed: {e}")
            return None
    
    async def _create_placeholder(self, config: Dict) -> Dict:
        """Create placeholder avatar data"""
        logger.info("📝 Creating placeholder avatar data...")
        
        return {
            "id": "avatar_001",
            "image_path": None,
            "prompt": self._build_avatar_prompt(config),
            "config": config,
            "placeholder": True,
            "created_at": str(Path().cwd())
        }
    
    def _build_avatar_prompt(self, config: Dict) -> str:
        """Build prompt for avatar generation"""
        style = config.get("style", "realistic")
        age = config.get("age_range", "25-35")
        personality = config.get("personality", "friendly, professional")
        
        prompt = f"A {style} portrait photo of a {age} year old person, {personality} personality, "
        prompt += "professional headshot quality, studio lighting, high resolution, "
        prompt += "photorealistic, detailed facial features, natural expression, "
        prompt += "suitable for social media profile, modern style"
        
        return prompt
    
    async def _download_image(self, url: str, filename: str) -> Path:
        """Download image from URL"""
        response = requests.get(url)
        image_path = self.avatar_dir / filename
        image_path.write_bytes(response.content)
        return image_path
    
    async def _save_base64_image(self, base64_data: str, filename: str) -> Path:
        """Save base64 image to file"""
        import base64
        
        image_data = base64.b64decode(base64_data)
        image_path = self.avatar_dir / filename
        image_path.write_bytes(image_data)
        return image_path
    
    async def _save_avatar_data(self, avatar_data: Dict):
        """Save avatar metadata"""
        metadata_path = self.avatar_dir / "avatar_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(avatar_data, f, indent=2)
    
    def get_avatar_data(self) -> Dict:
        """Get current avatar data"""
        return self.avatar_data
    
    async def generate_variations(self, count: int = 5) -> list:
        """Generate variations of the avatar for different content"""
        variations = []
        
        for i in range(count):
            variation_config = {
                **self.avatar_data.get("config", {}),
                "expression": ["smiling", "serious", "confident", "friendly", "professional"][i % 5],
                "background": ["studio", "outdoor", "office", "lifestyle", "abstract"][i % 5]
            }
            
            variation = await self.create_avatar(variation_config)
            if variation:
                variations.append(variation)
        
        return variations
