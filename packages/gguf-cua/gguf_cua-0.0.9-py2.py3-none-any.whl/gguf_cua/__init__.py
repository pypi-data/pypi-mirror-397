
__version__ = "0.0.9"

from .gguf_agent import FaraAgent
from .browser.playwright_controller import PlaywrightController

__all__ = ["FaraAgent", "PlaywrightController"]
