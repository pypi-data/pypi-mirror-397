"""
Synthesizer Node - Audio Component.

Converts text to speech using text-to-speech providers.
"""

from typing import Any, Dict, List, Optional

from flowmason_core.core.decorators import node
from flowmason_core.core.types import Field, NodeInput, NodeOutput


@node(
    name="synthesizer",
    category="audio",
    description="Convert text to natural-sounding speech with voice selection",
    icon="volume-2",
    color="#F59E0B",  # Amber for audio
    version="1.0.0",
    author="FlowMason",
    tags=["audio", "text-to-speech", "tts", "voice", "synthesis"],
    recommended_providers={
        "openai": {
            "model": "tts-1",
            "voice": "nova",
        },
        "elevenlabs": {
            "model": "eleven_multilingual_v2",
            "voice": "Rachel",
        },
    },
    default_provider="openai",
    required_capabilities=["text_to_speech"],
)
class SynthesizerNode:
    """
    Synthesize speech from text using text-to-speech providers.

    The Synthesizer converts text into natural-sounding speech
    with customizable voices and settings.

    Features:
    - Multiple voice options
    - Speed/pace control
    - Multiple audio formats (MP3, WAV, OGG, etc.)
    - High-quality and low-latency models

    Use cases:
    - Voice assistants
    - Audio content generation
    - Accessibility features
    - Notification systems
    - Interactive voice response (IVR)
    - Podcast/video narration

    Supported Providers:
    - OpenAI TTS (alloy, echo, fable, onyx, nova, shimmer)
    - ElevenLabs (premium voices + voice cloning)
    """

    class Input(NodeInput):
        text: str = Field(
            description="Text to convert to speech",
            examples=[
                "Hello, welcome to our service!",
                "Your order has been confirmed.",
            ],
        )
        voice: Optional[str] = Field(
            default=None,
            description="Voice ID or name to use",
            examples=["nova", "alloy", "Rachel", "Josh"],
        )
        model: Optional[str] = Field(
            default=None,
            description="TTS model to use (provider-specific)",
            examples=["tts-1", "tts-1-hd", "eleven_multilingual_v2"],
        )
        speed: float = Field(
            default=1.0,
            ge=0.25,
            le=4.0,
            description="Speech speed multiplier (0.25-4.0)",
        )
        format: str = Field(
            default="mp3",
            description="Output audio format",
            examples=["mp3", "wav", "ogg", "flac"],
        )
        output_path: Optional[str] = Field(
            default=None,
            description="Optional file path to save the audio",
            examples=["/tmp/output.mp3", "./audio/greeting.wav"],
        )
        # ElevenLabs-specific settings
        stability: Optional[float] = Field(
            default=None,
            ge=0.0,
            le=1.0,
            description="Voice stability (ElevenLabs: 0-1, higher = more consistent)",
        )
        similarity_boost: Optional[float] = Field(
            default=None,
            ge=0.0,
            le=1.0,
            description="Voice clarity (ElevenLabs: 0-1, higher = clearer)",
        )

    class Output(NodeOutput):
        audio_data: bytes = Field(
            default=b"",
            description="Raw audio data as bytes",
        )
        audio_base64: str = Field(
            default="",
            description="Base64-encoded audio data",
        )
        file_path: Optional[str] = Field(
            default=None,
            description="Path where audio was saved (if output_path specified)",
        )
        format: str = Field(default="mp3", description="Audio format")
        duration_seconds: float = Field(
            default=0.0,
            description="Estimated audio duration",
        )
        voice: str = Field(default="", description="Voice used")
        model: str = Field(default="", description="Model used")
        characters: int = Field(
            default=0,
            description="Number of characters synthesized",
        )

    class Config:
        requires_llm: bool = False  # Uses audio provider, not LLM
        timeout_seconds: int = 120

    async def execute(self, input: Input, context) -> Output:
        """
        Execute speech synthesis using the audio provider.

        Args:
            input: The validated Input model
            context: Execution context with providers

        Returns:
            Output with audio data and metadata
        """
        import base64

        # Get audio provider from context
        audio_provider = getattr(context, "audio", None)

        if not audio_provider:
            # Fallback for testing
            return self.Output(
                audio_data=b"mock_audio_data",
                audio_base64=base64.b64encode(b"mock_audio_data").decode(),
                format=input.format,
                voice=input.voice or "mock",
                model="mock",
                characters=len(input.text),
            )

        # Map format string to AudioFormat enum
        from flowmason_core.providers.audio.base import AudioFormat

        format_map = {
            "mp3": AudioFormat.MP3,
            "wav": AudioFormat.WAV,
            "ogg": AudioFormat.OGG,
            "flac": AudioFormat.FLAC,
            "pcm": AudioFormat.PCM,
            "aac": AudioFormat.AAC,
            "opus": AudioFormat.OPUS,
        }
        audio_format = format_map.get(input.format.lower(), AudioFormat.MP3)

        # Build provider-specific kwargs
        kwargs = {}
        if input.stability is not None:
            kwargs["stability"] = input.stability
        if input.similarity_boost is not None:
            kwargs["similarity_boost"] = input.similarity_boost

        # Perform synthesis
        result = await audio_provider.synthesize(
            text=input.text,
            voice=input.voice,
            format=audio_format,
            speed=input.speed,
            model=input.model,
            **kwargs,
        )

        # Handle error case
        if not result.success:
            raise ValueError(result.error or "Speech synthesis failed")

        # Save to file if requested
        file_path = None
        if input.output_path:
            with open(input.output_path, "wb") as f:
                f.write(result.audio_data)
            file_path = input.output_path

        # Encode audio to base64 for transport
        audio_base64 = base64.b64encode(result.audio_data).decode() if result.audio_data else ""

        return self.Output(
            audio_data=result.audio_data,
            audio_base64=audio_base64,
            file_path=file_path,
            format=input.format,
            duration_seconds=result.duration_seconds or 0.0,
            voice=result.voice_id or input.voice or "",
            model=result.model or audio_provider.name,
            characters=result.characters or len(input.text),
        )
