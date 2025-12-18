
__version__ = "0.0.6"

from .gguf_agent import FaraAgent
from .browser.playwright_controller import PlaywrightController

__all__ = ["FaraAgent", "PlaywrightController"]
