"""
Audio Provider Base Classes

Provides the base infrastructure for audio providers handling
text-to-speech (TTS) and speech-to-text (STT) operations.
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, BinaryIO, Dict, List, Optional, Union


class AudioFormat(str, Enum):
    """Supported audio formats."""
    MP3 = "mp3"
    WAV = "wav"
    OGG = "ogg"
    FLAC = "flac"
    M4A = "m4a"
    OPUS = "opus"
    WEBM = "webm"
    AAC = "aac"
    PCM = "pcm"


@dataclass
class TranscriptionSegment:
    """A segment of transcribed audio with timing information."""
    start: float  # Start time in seconds
    end: float  # End time in seconds
    text: str
    confidence: Optional[float] = None
    speaker: Optional[str] = None  # For speaker diarization

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start": self.start,
            "end": self.end,
            "text": self.text,
            "confidence": self.confidence,
            "speaker": self.speaker,
        }


@dataclass
class TranscriptionResult:
    """Result of a speech-to-text operation."""
    text: str
    language: Optional[str] = None
    duration_seconds: float = 0.0
    segments: Optional[List[TranscriptionSegment]] = None
    confidence: Optional[float] = None
    words: Optional[List[Dict[str, Any]]] = None  # Word-level timing
    model: str = ""
    duration_ms: int = 0  # Processing time
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "language": self.language,
            "duration_seconds": self.duration_seconds,
            "segments": [s.to_dict() for s in self.segments] if self.segments else None,
            "confidence": self.confidence,
            "words": self.words,
            "model": self.model,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error": self.error,
        }


@dataclass
class SynthesisResult:
    """Result of a text-to-speech operation."""
    audio_data: bytes
    format: AudioFormat
    duration_seconds: float = 0.0
    sample_rate: int = 24000
    voice_id: str = ""
    model: str = ""
    characters: int = 0  # Characters synthesized
    duration_ms: int = 0  # Processing time
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "format": self.format.value,
            "duration_seconds": self.duration_seconds,
            "sample_rate": self.sample_rate,
            "voice_id": self.voice_id,
            "model": self.model,
            "characters": self.characters,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error": self.error,
            # Note: audio_data not included in dict (binary)
        }


@dataclass
class VoiceInfo:
    """Information about an available voice."""
    id: str
    name: str
    description: Optional[str] = None
    gender: Optional[str] = None  # male, female, neutral
    language: Optional[str] = None
    accent: Optional[str] = None
    preview_url: Optional[str] = None
    labels: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "gender": self.gender,
            "language": self.language,
            "accent": self.accent,
            "preview_url": self.preview_url,
            "labels": self.labels,
        }


@dataclass
class AudioProviderConfig:
    """Configuration for an audio provider instance."""
    provider_type: str
    api_key_env: str
    default_voice: Optional[str] = None
    default_model: Optional[str] = None
    timeout: int = 120
    max_retries: int = 3
    extra_config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider_type": self.provider_type,
            "api_key_env": self.api_key_env,
            "default_voice": self.default_voice,
            "default_model": self.default_model,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "extra_config": self.extra_config,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AudioProviderConfig":
        return cls(**data)


class AudioProvider(ABC):
    """
    Abstract base class for audio providers (TTS/STT).

    Providers must implement:
    - name: Provider identifier
    - transcribe(): Speech-to-text (if supported)
    - synthesize(): Text-to-speech (if supported)
    - available_voices: List of available voices (for TTS)
    - capabilities: List of supported capabilities

    Example implementation:

        class MyAudioProvider(AudioProvider):
            @property
            def name(self) -> str:
                return "my_audio"

            @property
            def capabilities(self) -> List[str]:
                return ["speech_to_text", "text_to_speech"]

            @property
            def available_voices(self) -> List[VoiceInfo]:
                return [VoiceInfo(id="voice1", name="Voice 1")]

            async def transcribe(self, audio, language=None, ...) -> TranscriptionResult:
                # Implement STT
                pass

            async def synthesize(self, text, voice=None, ...) -> SynthesisResult:
                # Implement TTS
                pass
    """

    # Default pricing (override in subclasses)
    # STT: per minute, TTS: per 1K characters
    DEFAULT_PRICING = {
        "transcription_per_minute": 0.0,
        "synthesis_per_1k_chars": 0.0,
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_voice: Optional[str] = None,
        default_model: Optional[str] = None,
        timeout: int = 120,
        max_retries: int = 3,
        pricing: Optional[Dict[str, float]] = None,
        **kwargs
    ):
        """
        Initialize the audio provider.

        Args:
            api_key: API key for the provider
            default_voice: Default voice for TTS
            default_model: Default model to use
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            pricing: Custom pricing overrides
            **kwargs: Provider-specific configuration
        """
        self.api_key = api_key
        self.default_voice = default_voice
        self.default_model = default_model
        self.timeout = timeout
        self.max_retries = max_retries
        self.pricing = pricing or self.DEFAULT_PRICING
        self.extra_config = kwargs

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name identifier."""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """
        List of capabilities this provider supports.

        Values: "speech_to_text", "text_to_speech", "voice_cloning"
        """
        pass

    @property
    @abstractmethod
    def available_voices(self) -> List[VoiceInfo]:
        """List of available voices for TTS."""
        pass

    def supports_stt(self) -> bool:
        """Check if provider supports speech-to-text."""
        return "speech_to_text" in self.capabilities

    def supports_tts(self) -> bool:
        """Check if provider supports text-to-speech."""
        return "text_to_speech" in self.capabilities

    def supports_cloning(self) -> bool:
        """Check if provider supports voice cloning."""
        return "voice_cloning" in self.capabilities

    @abstractmethod
    async def transcribe(
        self,
        audio: Union[BinaryIO, bytes, str],
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        timestamps: bool = False,
        word_timestamps: bool = False,
        model: Optional[str] = None,
        **kwargs
    ) -> TranscriptionResult:
        """
        Transcribe audio to text.

        Args:
            audio: Audio data (file-like, bytes, or file path)
            language: Language code (ISO 639-1, e.g., "en", "es")
            prompt: Context hint for better transcription
            timestamps: Include segment-level timestamps
            word_timestamps: Include word-level timestamps
            model: Override default model
            **kwargs: Provider-specific options

        Returns:
            TranscriptionResult with transcribed text
        """
        pass

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        format: AudioFormat = AudioFormat.MP3,
        speed: float = 1.0,
        model: Optional[str] = None,
        **kwargs
    ) -> SynthesisResult:
        """
        Synthesize text to speech.

        Args:
            text: Text to synthesize
            voice: Voice ID to use
            format: Output audio format
            speed: Speech speed multiplier (0.25 to 4.0 typically)
            model: Override default model
            **kwargs: Provider-specific options

        Returns:
            SynthesisResult with audio data
        """
        pass

    async def synthesize_to_file(
        self,
        text: str,
        output_path: str,
        voice: Optional[str] = None,
        format: Optional[AudioFormat] = None,
        speed: float = 1.0,
        **kwargs
    ) -> SynthesisResult:
        """
        Synthesize text and save to file.

        Args:
            text: Text to synthesize
            output_path: Path to save audio file
            voice: Voice ID to use
            format: Output format (detected from path if not specified)
            speed: Speech speed multiplier
            **kwargs: Additional options

        Returns:
            SynthesisResult (audio_data will be empty)
        """
        # Detect format from path if not specified
        if format is None:
            ext = output_path.rsplit(".", 1)[-1].lower()
            try:
                format = AudioFormat(ext)
            except ValueError:
                format = AudioFormat.MP3

        result = await self.synthesize(
            text=text,
            voice=voice,
            format=format,
            speed=speed,
            **kwargs
        )

        if result.success:
            with open(output_path, "wb") as f:
                f.write(result.audio_data)

        return result

    def get_voice(self, voice_id: str) -> Optional[VoiceInfo]:
        """Get voice info by ID."""
        for voice in self.available_voices:
            if voice.id == voice_id:
                return voice
        return None

    def calculate_transcription_cost(self, duration_seconds: float) -> float:
        """Calculate cost for transcription."""
        minutes = duration_seconds / 60
        return minutes * self.pricing.get("transcription_per_minute", 0)

    def calculate_synthesis_cost(self, characters: int) -> float:
        """Calculate cost for synthesis."""
        return (characters / 1000) * self.pricing.get("synthesis_per_1k_chars", 0)

    def _time_call(self, func, *args, **kwargs) -> tuple:
        """Time a function call."""
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration_ms = int((time.perf_counter() - start) * 1000)
        return result, duration_ms

    async def _time_call_async(self, coro) -> tuple:
        """Time an async coroutine."""
        start = time.perf_counter()
        result = await coro
        duration_ms = int((time.perf_counter() - start) * 1000)
        return result, duration_ms

    def _load_audio(self, audio: Union[BinaryIO, bytes, str]) -> bytes:
        """Load audio from various input types."""
        if isinstance(audio, bytes):
            return audio
        elif isinstance(audio, str):
            with open(audio, "rb") as f:
                return f.read()
        else:
            return audio.read()

    def get_config(self) -> AudioProviderConfig:
        """Get the configuration for this provider instance."""
        return AudioProviderConfig(
            provider_type=self.name,
            api_key_env=f"{self.name.upper()}_API_KEY",
            default_voice=self.default_voice,
            default_model=self.default_model,
            timeout=self.timeout,
            max_retries=self.max_retries,
            extra_config=self.extra_config,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(voice={self.default_voice})"


# Audio Provider Registry
_AUDIO_REGISTRY: Dict[str, type] = {}


def register_audio_provider(provider_class: type) -> type:
    """
    Register an audio provider class.

    Can be used as a decorator:

        @register_audio_provider
        class MyAudioProvider(AudioProvider):
            ...
    """
    if not issubclass(provider_class, AudioProvider):
        raise ValueError(f"{provider_class.__name__} must extend AudioProvider")

    try:
        temp = object.__new__(provider_class)
        temp.api_key = "temp"
        temp.default_voice = None
        temp.default_model = None
        temp.timeout = 120
        temp.max_retries = 3
        temp.pricing = provider_class.DEFAULT_PRICING
        temp.extra_config = {}
        name = temp.name
    except Exception:
        name = provider_class.__name__.lower().replace("provider", "").replace("audio", "")

    _AUDIO_REGISTRY[name] = provider_class
    return provider_class


def get_audio_provider(name: str) -> Optional[type]:
    """Get an audio provider class by name."""
    return _AUDIO_REGISTRY.get(name)


def list_audio_providers() -> List[str]:
    """List all registered audio provider names."""
    return list(_AUDIO_REGISTRY.keys())


def create_audio_provider(config: AudioProviderConfig) -> AudioProvider:
    """Create an audio provider instance from configuration."""
    import os

    provider_class = get_audio_provider(config.provider_type)
    if not provider_class:
        raise ValueError(f"Unknown audio provider type: {config.provider_type}")

    api_key = os.environ.get(config.api_key_env)

    provider: AudioProvider = provider_class(
        api_key=api_key,
        default_voice=config.default_voice,
        default_model=config.default_model,
        timeout=config.timeout,
        max_retries=config.max_retries,
        **config.extra_config
    )
    return provider
