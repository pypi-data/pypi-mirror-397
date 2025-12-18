"""
OpenAI Audio Provider

Provides speech-to-text via Whisper and text-to-speech via OpenAI's TTS API.
"""

import io
import os
from typing import BinaryIO, Dict, List, Optional, Union

from .base import (
    AudioFormat,
    AudioProvider,
    SynthesisResult,
    TranscriptionResult,
    TranscriptionSegment,
    VoiceInfo,
    register_audio_provider,
)


@register_audio_provider
class OpenAIAudioProvider(AudioProvider):
    """
    Audio provider for OpenAI's Whisper (STT) and TTS APIs.

    Speech-to-Text (Whisper):
    - whisper-1: Multi-lingual transcription
    - Supports 98+ languages
    - Word and segment timestamps
    - Translation to English

    Text-to-Speech:
    - tts-1: Standard quality, lower latency
    - tts-1-hd: High-definition quality
    - 6 built-in voices

    Pricing (as of Dec 2024):
    - Whisper: $0.006 per minute
    - TTS: $0.015 per 1K characters (tts-1), $0.030 per 1K (tts-1-hd)
    """

    DEFAULT_PRICING = {
        "transcription_per_minute": 0.006,
        "synthesis_per_1k_chars": 0.015,  # tts-1
    }

    # OpenAI TTS voices
    VOICES = [
        VoiceInfo(id="alloy", name="Alloy", description="Neutral, balanced", gender="neutral"),
        VoiceInfo(id="echo", name="Echo", description="Warm, conversational", gender="male"),
        VoiceInfo(id="fable", name="Fable", description="Expressive, storytelling", gender="male"),
        VoiceInfo(id="onyx", name="Onyx", description="Deep, authoritative", gender="male"),
        VoiceInfo(id="nova", name="Nova", description="Friendly, upbeat", gender="female"),
        VoiceInfo(id="shimmer", name="Shimmer", description="Clear, professional", gender="female"),
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_voice: Optional[str] = None,
        default_model: Optional[str] = None,
        timeout: int = 120,
        max_retries: int = 3,
        pricing: Optional[Dict[str, float]] = None,
        base_url: Optional[str] = None,
        **kwargs
    ):
        api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key."
            )

        super().__init__(
            api_key=api_key,
            default_voice=default_voice or "nova",
            default_model=default_model,
            timeout=timeout,
            max_retries=max_retries,
            pricing=pricing or self.DEFAULT_PRICING,
            **kwargs
        )
        self.base_url = base_url
        self._client = None
        self._async_client = None

    @property
    def client(self):
        """Lazy-load the OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.api_key,
                    timeout=self.timeout,
                    max_retries=self.max_retries,
                    base_url=self.base_url,
                )
            except ImportError:
                raise ImportError("openai package required. Install with: pip install openai")
        return self._client

    @property
    def async_client(self):
        """Lazy-load the async OpenAI client."""
        if self._async_client is None:
            try:
                from openai import AsyncOpenAI
                self._async_client = AsyncOpenAI(
                    api_key=self.api_key,
                    timeout=self.timeout,
                    max_retries=self.max_retries,
                    base_url=self.base_url,
                )
            except ImportError:
                raise ImportError("openai package required. Install with: pip install openai")
        return self._async_client

    @property
    def name(self) -> str:
        return "openai_audio"

    @property
    def capabilities(self) -> List[str]:
        return ["speech_to_text", "text_to_speech"]

    @property
    def available_voices(self) -> List[VoiceInfo]:
        return self.VOICES

    async def transcribe(
        self,
        audio: Union[BinaryIO, bytes, str],
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        timestamps: bool = False,
        word_timestamps: bool = False,
        model: Optional[str] = None,
        response_format: str = "verbose_json",
        **kwargs
    ) -> TranscriptionResult:
        """
        Transcribe audio using OpenAI Whisper.

        Args:
            audio: Audio data (file-like, bytes, or file path)
            language: Language code (ISO 639-1)
            prompt: Context hint for better transcription
            timestamps: Include segment timestamps
            word_timestamps: Include word-level timestamps
            model: Model to use (default: whisper-1)
            response_format: Output format
            **kwargs: Additional options

        Returns:
            TranscriptionResult with transcribed text
        """
        import time
        model = model or self.default_model or "whisper-1"

        try:
            # Load audio data
            audio_data = self._load_audio(audio)

            # Determine response format based on timestamp needs
            if timestamps or word_timestamps:
                response_format = "verbose_json"

            # Build parameters
            params = {
                "model": model,
                "file": ("audio.mp3", io.BytesIO(audio_data), "audio/mpeg"),
                "response_format": response_format,
            }

            if language:
                params["language"] = language
            if prompt:
                params["prompt"] = prompt
            if word_timestamps:
                params["timestamp_granularities"] = ["word", "segment"]
            elif timestamps:
                params["timestamp_granularities"] = ["segment"]

            start = time.perf_counter()
            response = await self.async_client.audio.transcriptions.create(**params)
            duration_ms = int((time.perf_counter() - start) * 1000)

            # Parse response based on format
            if response_format == "verbose_json":
                text = response.text
                language_detected = getattr(response, "language", language)
                duration_seconds = getattr(response, "duration", 0.0)

                # Parse segments
                segments = None
                if timestamps and hasattr(response, "segments"):
                    segments = [
                        TranscriptionSegment(
                            start=seg.get("start", 0),
                            end=seg.get("end", 0),
                            text=seg.get("text", ""),
                        )
                        for seg in response.segments
                    ]

                # Parse words
                words = None
                if word_timestamps and hasattr(response, "words"):
                    words = [
                        {"word": w.get("word"), "start": w.get("start"), "end": w.get("end")}
                        for w in response.words
                    ]
            else:
                text = response if isinstance(response, str) else str(response)
                language_detected = language
                duration_seconds = 0.0
                segments = None
                words = None

            return TranscriptionResult(
                text=text,
                language=language_detected,
                duration_seconds=duration_seconds,
                segments=segments,
                words=words,
                model=model,
                duration_ms=duration_ms,
                success=True,
            )

        except Exception as e:
            return TranscriptionResult(
                text="",
                model=model,
                success=False,
                error=str(e),
            )

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
        Synthesize text to speech using OpenAI TTS.

        Args:
            text: Text to synthesize (max 4096 chars)
            voice: Voice ID (alloy, echo, fable, onyx, nova, shimmer)
            format: Output audio format
            speed: Speed multiplier (0.25 to 4.0)
            model: TTS model (tts-1 or tts-1-hd)
            **kwargs: Additional options

        Returns:
            SynthesisResult with audio data
        """
        import time
        model = model or self.default_model or "tts-1"
        voice = voice or self.default_voice or "nova"

        # Clamp speed to valid range
        speed = max(0.25, min(4.0, speed))

        # Map format to OpenAI format names
        format_map = {
            AudioFormat.MP3: "mp3",
            AudioFormat.WAV: "wav",
            AudioFormat.OGG: "opus",  # OpenAI uses opus for ogg
            AudioFormat.OPUS: "opus",
            AudioFormat.FLAC: "flac",
            AudioFormat.AAC: "aac",
            AudioFormat.PCM: "pcm",
        }
        output_format = format_map.get(format, "mp3")

        try:
            start = time.perf_counter()
            response = await self.async_client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
                response_format=output_format,
                speed=speed,
            )
            duration_ms = int((time.perf_counter() - start) * 1000)

            # Get audio bytes
            audio_data = response.content

            # Estimate duration (rough estimate: ~150 words per minute at speed 1.0)
            word_count = len(text.split())
            estimated_duration = (word_count / 150) * 60 / speed

            return SynthesisResult(
                audio_data=audio_data,
                format=format,
                duration_seconds=estimated_duration,
                sample_rate=24000,  # OpenAI TTS sample rate
                voice_id=voice,
                model=model,
                characters=len(text),
                duration_ms=duration_ms,
                success=True,
            )

        except Exception as e:
            return SynthesisResult(
                audio_data=b"",
                format=format,
                voice_id=voice,
                model=model,
                success=False,
                error=str(e),
            )

    async def translate(
        self,
        audio: Union[BinaryIO, bytes, str],
        prompt: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> TranscriptionResult:
        """
        Translate audio to English text.

        This uses Whisper's translation capability to transcribe and
        translate non-English audio to English.

        Args:
            audio: Audio data
            prompt: Context hint
            model: Model to use

        Returns:
            TranscriptionResult with English text
        """
        import time
        model = model or self.default_model or "whisper-1"

        try:
            audio_data = self._load_audio(audio)

            params = {
                "model": model,
                "file": ("audio.mp3", io.BytesIO(audio_data), "audio/mpeg"),
                "response_format": "verbose_json",
            }

            if prompt:
                params["prompt"] = prompt

            start = time.perf_counter()
            response = await self.async_client.audio.translations.create(**params)
            duration_ms = int((time.perf_counter() - start) * 1000)

            return TranscriptionResult(
                text=response.text,
                language="en",  # Translation always outputs English
                duration_seconds=getattr(response, "duration", 0.0),
                model=model,
                duration_ms=duration_ms,
                success=True,
            )

        except Exception as e:
            return TranscriptionResult(
                text="",
                model=model,
                success=False,
                error=str(e),
            )
