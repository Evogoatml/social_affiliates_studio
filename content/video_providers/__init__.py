"""
Video Provider Registry and Factory
"""

from typing import Dict, Type, Optional
from .base_provider import BaseVideoProvider
from .kling_provider import KlingProvider
from .pika_provider import PikaProvider
from .runway_provider import RunwayProvider
from .heygen_provider import HeyGenProvider
from core.logger import setup_logger

logger = setup_logger(__name__)


class VideoProviderRegistry:
    """Registry for managing video generation providers"""
    
    _providers: Dict[str, Type[BaseVideoProvider]] = {
        "kling": KlingProvider,
        "pika": PikaProvider,
        "runway": RunwayProvider,
        "heygen": HeyGenProvider,
    }
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseVideoProvider]):
        """Register a new provider"""
        cls._providers[name] = provider_class
        logger.info(f"✅ Registered video provider: {name}")
    
    @classmethod
    def get_provider_class(cls, name: str) -> Optional[Type[BaseVideoProvider]]:
        """Get provider class by name"""
        return cls._providers.get(name.lower())
    
    @classmethod
    def list_providers(cls) -> list:
        """List all registered provider names"""
        return list(cls._providers.keys())
    
    @classmethod
    def create_provider(
        cls, 
        name: str, 
        api_key: str, 
        config: Optional[Dict] = None
    ) -> Optional[BaseVideoProvider]:
        """
        Factory method to create a provider instance
        
        Args:
            name: Provider name (e.g., 'kling', 'pika', 'runway')
            api_key: API key for the provider
            config: Optional provider-specific configuration
        
        Returns:
            Provider instance or None if not found
        """
        provider_class = cls.get_provider_class(name)
        
        if provider_class is None:
            logger.error(f"❌ Unknown video provider: {name}")
            return None
        
        try:
            provider = provider_class(api_key=api_key, config=config or {})
            logger.info(f"✅ Created video provider: {name}")
            return provider
        except Exception as e:
            logger.exception(f"❌ Failed to create provider {name}: {e}")
            return None


__all__ = [
    "BaseVideoProvider",
    "VideoProviderRegistry",
    "KlingProvider",
    "PikaProvider",
    "RunwayProvider",
    "HeyGenProvider",
]
