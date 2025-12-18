"""
FlowMason Audio Providers

Provides audio processing providers for text-to-speech (TTS) and
speech-to-text (STT) operations.

Built-in Providers:
- OpenAIAudioProvider: Whisper (STT) + TTS
- ElevenLabsProvider: Premium TTS with voice cloning

Usage:
    from flowmason_core.providers.audio import (
        OpenAIAudioProvider,
        ElevenLabsProvider,
        AudioFormat,
    )

    # Transcribe audio (STT)
    provider = OpenAIAudioProvider()
    result = await provider.transcribe("audio.mp3", timestamps=True)
    print(result.text)

    # Synthesize speech (TTS)
    result = await provider.synthesize(
        "Hello, world!",
        voice="nova",
        format=AudioFormat.MP3
    )
    with open("output.mp3", "wb") as f:
        f.write(result.audio_data)

    # Premium TTS with ElevenLabs
    eleven = ElevenLabsProvider()
    result = await eleven.synthesize(
        "Hello, world!",
        voice="Rachel",
        stability=0.7
    )
"""

from .base import (
    AudioFormat,
    AudioProvider,
    AudioProviderConfig,
    SynthesisResult,
    TranscriptionResult,
    TranscriptionSegment,
    VoiceInfo,
    create_audio_provider,
    get_audio_provider,
    list_audio_providers,
    register_audio_provider,
)

# Import built-in providers to register them
from .openai import OpenAIAudioProvider
from .elevenlabs import ElevenLabsProvider

__all__ = [
    # Base classes
    "AudioProvider",
    "AudioFormat",
    "TranscriptionResult",
    "TranscriptionSegment",
    "SynthesisResult",
    "VoiceInfo",
    "AudioProviderConfig",
    # Registry functions
    "register_audio_provider",
    "get_audio_provider",
    "list_audio_providers",
    "create_audio_provider",
    # Built-in providers
    "OpenAIAudioProvider",
    "ElevenLabsProvider",
]
