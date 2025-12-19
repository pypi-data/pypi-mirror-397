# This file marks the directory as a Python package.
# Static imports for all TTS (Text-to-Speech) provider modules

# Base classes
from webscout.Provider.TTS.base import (
    BaseTTSProvider,
    AsyncBaseTTSProvider,
)

# Utility classes
from webscout.Provider.TTS.utils import SentenceTokenizer

# Provider implementations
from webscout.Provider.TTS.deepgram import DeepgramTTS
from webscout.Provider.TTS.elevenlabs import ElevenlabsTTS
from webscout.Provider.TTS.freetts import FreeTTS
from webscout.Provider.TTS.gesserit import GesseritTTS
from webscout.Provider.TTS.murfai import MurfAITTS
from webscout.Provider.TTS.openai_fm import OpenAIFMTTS
from webscout.Provider.TTS.parler import ParlerTTS
from webscout.Provider.TTS.speechma import SpeechMaTTS
from webscout.Provider.TTS.streamElements import StreamElements

# List of all exported names
__all__ = [
    # Base classes
    "BaseTTSProvider",
    "AsyncBaseTTSProvider",
    # Utilities
    "SentenceTokenizer",
    # Providers
    "DeepgramTTS",
    "ElevenlabsTTS",
    "FreeTTS",
    "GesseritTTS",
    "MurfAITTS",
    "OpenAIFMTTS",
    "ParlerTTS",
    "SpeechMaTTS",
    "StreamElements",
]
