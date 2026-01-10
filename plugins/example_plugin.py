"""
Example Plugin for Suite Orchestrator
Demonstrates how to create custom plugins
"""

from plugin_system import PluginBase, PluginInfo

class ExamplePlugin(PluginBase):
    """Example plugin that logs all service events"""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="example_plugin",
            version="1.0.0",
            description="Example plugin that logs service events",
            author="Your Name",
            hooks=["service_start", "service_stop", "service_error"]
        )
    
    def on_service_start(self, service_name: str, pid: int) -> None:
        """Log when a service starts"""
        print(f"📝 [ExamplePlugin] Service '{service_name}' started with PID {pid}")
    
    def on_service_stop(self, service_name: str, pid: int) -> None:
        """Log when a service stops"""
        print(f"📝 [ExamplePlugin] Service '{service_name}' stopped (was PID {pid})")
    
    def on_service_error(self, service_name: str, error: Exception) -> None:
        """Log service errors"""
        print(f"❌ [ExamplePlugin] Service '{service_name}' error: {error}")
