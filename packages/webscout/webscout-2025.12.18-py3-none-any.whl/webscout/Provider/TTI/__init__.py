# This file marks the directory as a Python package.
# Static imports for all TTI (Text-to-Image) provider modules

# Base classes
from webscout.Provider.TTI.base import (
    TTICompatibleProvider,
    BaseImages,
)

# Utility classes
from webscout.Provider.TTI.utils import (
    ImageData,
    ImageResponse,
)

# Provider implementations
from webscout.Provider.TTI.aiarta import AIArta
from webscout.Provider.TTI.bing import BingImageAI
from webscout.Provider.TTI.claudeonline import ClaudeOnlineTTI
from webscout.Provider.TTI.gpt1image import GPT1Image
from webscout.Provider.TTI.imagen import ImagenAI
from webscout.Provider.TTI.infip import InfipAI
from webscout.Provider.TTI.magicstudio import MagicStudioAI
from webscout.Provider.TTI.monochat import MonoChatAI
from webscout.Provider.TTI.piclumen import PiclumenAI
from webscout.Provider.TTI.pixelmuse import PixelMuse
from webscout.Provider.TTI.pollinations import PollinationsAI
from webscout.Provider.TTI.together import TogetherImage
from webscout.Provider.TTI.venice import VeniceAI

# List of all exported names
__all__ = [
    # Base classes
    "TTICompatibleProvider",
    "BaseImages",
    # Utilities
    "ImageData",
    "ImageResponse",
    # Providers
    "AIArta",
    "BingImageAI",
    "ClaudeOnlineTTI",
    "GPT1Image",
    "ImagenAI",
    "InfipAI",
    "MagicStudioAI",
    "MonoChatAI",
    "PiclumenAI",
    "PixelMuse",
    "PollinationsAI",
    "TogetherImage",
    "VeniceAI",
]
