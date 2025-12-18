
__version__ = "0.0.3"

from .fara_agent import FaraAgent
from .browser.playwright_controller import PlaywrightController

__all__ = ["FaraAgent", "PlaywrightController"]
