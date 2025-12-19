"""
ElevenLabs Audio Provider

Provides premium text-to-speech with voice cloning capabilities.
"""

import os
from typing import BinaryIO, Dict, List, Optional, Union

from .base import (
    AudioFormat,
    AudioProvider,
    SynthesisResult,
    TranscriptionResult,
    VoiceInfo,
    register_audio_provider,
)


@register_audio_provider
class ElevenLabsProvider(AudioProvider):
    """
    Audio provider for ElevenLabs TTS API.

    ElevenLabs offers high-quality, natural-sounding voices with:
    - Multiple voice models (eleven_multilingual_v2, eleven_turbo_v2, etc.)
    - Voice cloning from audio samples
    - Voice design with custom settings
    - Multiple output formats

    Pricing varies by tier:
    - Free: 10K chars/month
    - Starter: $5/30K chars
    - Creator: $22/100K chars
    - Pro: $99/500K chars

    Note: This provider is TTS-only. Does not support speech-to-text.
    """

    DEFAULT_PRICING = {
        "transcription_per_minute": 0.0,  # Not supported
        "synthesis_per_1k_chars": 0.30,  # Approximate
    }

    # Default voices (these are pre-made voices, user voices will be loaded dynamically)
    DEFAULT_VOICES = [
        VoiceInfo(
            id="21m00Tcm4TlvDq8ikWAM",
            name="Rachel",
            description="American female, calm",
            gender="female",
            language="en",
            accent="American",
        ),
        VoiceInfo(
            id="AZnzlk1XvdvUeBnXmlld",
            name="Domi",
            description="American female, confident",
            gender="female",
            language="en",
            accent="American",
        ),
        VoiceInfo(
            id="EXAVITQu4vr4xnSDxMaL",
            name="Bella",
            description="American female, soft",
            gender="female",
            language="en",
            accent="American",
        ),
        VoiceInfo(
            id="ErXwobaYiN019PkySvjV",
            name="Antoni",
            description="American male, well-rounded",
            gender="male",
            language="en",
            accent="American",
        ),
        VoiceInfo(
            id="MF3mGyEYCl7XYWbV9V6O",
            name="Elli",
            description="American female, emotional",
            gender="female",
            language="en",
            accent="American",
        ),
        VoiceInfo(
            id="TxGEqnHWrfWFTfGW9XjX",
            name="Josh",
            description="American male, young",
            gender="male",
            language="en",
            accent="American",
        ),
        VoiceInfo(
            id="VR6AewLTigWG4xSOukaG",
            name="Arnold",
            description="American male, crisp",
            gender="male",
            language="en",
            accent="American",
        ),
        VoiceInfo(
            id="pNInz6obpgDQGcFmaJgB",
            name="Adam",
            description="American male, deep",
            gender="male",
            language="en",
            accent="American",
        ),
        VoiceInfo(
            id="yoZ06aMxZJJ28mfd3POQ",
            name="Sam",
            description="American male, raspy",
            gender="male",
            language="en",
            accent="American",
        ),
    ]

    # Available models
    MODELS = {
        "eleven_multilingual_v2": "Multi-lingual, highest quality",
        "eleven_turbo_v2": "Low latency, English optimized",
        "eleven_monolingual_v1": "English only, legacy",
        "eleven_multilingual_v1": "Multi-lingual, legacy",
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
        api_key = api_key or os.environ.get("ELEVENLABS_API_KEY")
        if not api_key:
            raise ValueError(
                "ElevenLabs API key required. Set ELEVENLABS_API_KEY env var or pass api_key."
            )

        super().__init__(
            api_key=api_key,
            default_voice=default_voice or "21m00Tcm4TlvDq8ikWAM",  # Rachel
            default_model=default_model or "eleven_multilingual_v2",
            timeout=timeout,
            max_retries=max_retries,
            pricing=pricing or self.DEFAULT_PRICING,
            **kwargs
        )
        self._client = None
        self._voices_cache = None

    @property
    def client(self):
        """Lazy-load the ElevenLabs client."""
        if self._client is None:
            try:
                from elevenlabs.client import ElevenLabs
                self._client = ElevenLabs(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "elevenlabs package required. Install with: pip install elevenlabs"
                )
        return self._client

    @property
    def name(self) -> str:
        return "elevenlabs"

    @property
    def capabilities(self) -> List[str]:
        return ["text_to_speech", "voice_cloning"]

    @property
    def available_voices(self) -> List[VoiceInfo]:
        """Get available voices (includes user's cloned voices)."""
        if self._voices_cache is None:
            self._voices_cache = self._fetch_voices()
        return self._voices_cache

    def _fetch_voices(self) -> List[VoiceInfo]:
        """Fetch voices from ElevenLabs API."""
        try:
            response = self.client.voices.get_all()
            voices = []

            for voice in response.voices:
                voices.append(VoiceInfo(
                    id=voice.voice_id,
                    name=voice.name,
                    description=voice.description,
                    gender=voice.labels.get("gender") if voice.labels else None,
                    accent=voice.labels.get("accent") if voice.labels else None,
                    labels=dict(voice.labels) if voice.labels else {},
                    preview_url=voice.preview_url,
                ))

            return voices if voices else self.DEFAULT_VOICES
        except Exception:
            return self.DEFAULT_VOICES

    def refresh_voices(self) -> List[VoiceInfo]:
        """Force refresh of voices cache."""
        self._voices_cache = None
        return self.available_voices

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
        ElevenLabs does not support speech-to-text.

        This method raises NotImplementedError.
        Use OpenAIAudioProvider for transcription.
        """
        return TranscriptionResult(
            text="",
            success=False,
            error="ElevenLabs does not support speech-to-text. Use OpenAI Whisper instead.",
        )

    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        format: AudioFormat = AudioFormat.MP3,
        speed: float = 1.0,
        model: Optional[str] = None,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True,
        **kwargs
    ) -> SynthesisResult:
        """
        Synthesize text to speech using ElevenLabs.

        Args:
            text: Text to synthesize
            voice: Voice ID
            format: Output audio format
            speed: Not directly supported, use style instead
            model: Model ID
            stability: Voice stability (0-1, higher = more consistent)
            similarity_boost: Voice clarity (0-1, higher = clearer)
            style: Style exaggeration (0-1, higher = more expressive)
            use_speaker_boost: Boost speaker similarity
            **kwargs: Additional options

        Returns:
            SynthesisResult with audio data
        """
        import time
        model = model or self.default_model
        voice = voice or self.default_voice

        # Map format to ElevenLabs format
        format_map = {
            AudioFormat.MP3: "mp3_44100_128",
            AudioFormat.WAV: "pcm_44100",
            AudioFormat.OGG: "mp3_44100_128",  # Fallback
            AudioFormat.FLAC: "pcm_44100",
            AudioFormat.PCM: "pcm_44100",
        }
        output_format = format_map.get(format, "mp3_44100_128")

        try:
            start = time.perf_counter()

            # Generate audio
            audio_generator = self.client.generate(
                text=text,
                voice=voice,
                model=model,
                output_format=output_format,
                voice_settings={
                    "stability": stability,
                    "similarity_boost": similarity_boost,
                    "style": style,
                    "use_speaker_boost": use_speaker_boost,
                }
            )

            # Collect audio chunks
            audio_data = b"".join(chunk for chunk in audio_generator)

            duration_ms = int((time.perf_counter() - start) * 1000)

            # Estimate duration
            word_count = len(text.split())
            estimated_duration = (word_count / 150) * 60

            return SynthesisResult(
                audio_data=audio_data,
                format=format,
                duration_seconds=estimated_duration,
                sample_rate=44100,
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

    async def synthesize_stream(
        self,
        text: str,
        voice: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ):
        """
        Stream synthesized audio chunks.

        Yields audio chunks as they are generated.
        Useful for real-time applications.

        Args:
            text: Text to synthesize
            voice: Voice ID
            model: Model ID
            **kwargs: Additional options

        Yields:
            bytes: Audio chunks
        """
        model = model or self.default_model
        voice = voice or self.default_voice

        try:
            audio_stream = self.client.generate(
                text=text,
                voice=voice,
                model=model,
                stream=True,
            )

            for chunk in audio_stream:
                yield chunk

        except Exception as e:
            raise RuntimeError(f"Streaming synthesis failed: {e}")

    async def clone_voice(
        self,
        name: str,
        audio_files: List[Union[BinaryIO, bytes, str]],
        description: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
    ) -> VoiceInfo:
        """
        Clone a voice from audio samples.

        Args:
            name: Name for the cloned voice
            audio_files: Audio samples (1-25 samples recommended)
            description: Voice description
            labels: Labels for categorization

        Returns:
            VoiceInfo for the new voice
        """
        try:
            # Prepare files
            files = []
            for i, audio in enumerate(audio_files):
                audio_data = self._load_audio(audio)
                files.append((f"sample_{i}.mp3", audio_data))

            # Create voice clone
            response = self.client.clone(
                name=name,
                description=description or f"Cloned voice: {name}",
                files=files,
                labels=labels,
            )

            # Refresh cache
            self._voices_cache = None

            return VoiceInfo(
                id=response.voice_id,
                name=name,
                description=description,
                labels=labels or {},
            )

        except Exception as e:
            raise RuntimeError(f"Voice cloning failed: {e}")

    async def delete_voice(self, voice_id: str) -> bool:
        """
        Delete a cloned voice.

        Args:
            voice_id: ID of voice to delete

        Returns:
            True if deleted successfully
        """
        try:
            self.client.voices.delete(voice_id)
            self._voices_cache = None  # Refresh cache
            return True
        except Exception as e:
            raise RuntimeError(f"Voice deletion failed: {e}")

    async def get_voice_settings(self, voice_id: str) -> Dict[str, float]:
        """Get voice settings for a specific voice."""
        try:
            settings = self.client.voices.get_settings(voice_id)
            return {
                "stability": settings.stability,
                "similarity_boost": settings.similarity_boost,
                "style": getattr(settings, "style", 0.0),
                "use_speaker_boost": getattr(settings, "use_speaker_boost", True),
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get voice settings: {e}")
