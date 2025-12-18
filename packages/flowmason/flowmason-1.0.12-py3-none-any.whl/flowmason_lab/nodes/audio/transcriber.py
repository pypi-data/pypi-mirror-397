"""
Transcriber Node - Audio Component.

Converts speech audio to text using speech-to-text providers.
"""

from typing import Any, Dict, List, Optional

from flowmason_core.core.decorators import node
from flowmason_core.core.types import Field, NodeInput, NodeOutput


@node(
    name="transcriber",
    category="audio",
    description="Transcribe speech audio to text with optional timestamps",
    icon="mic",
    color="#F59E0B",  # Amber for audio
    version="1.0.0",
    author="FlowMason",
    tags=["audio", "speech-to-text", "stt", "transcription", "voice"],
    recommended_providers={
        "openai": {
            "model": "whisper-1",
        },
    },
    default_provider="openai",
    required_capabilities=["speech_to_text"],
)
class TranscriberNode:
    """
    Transcribe audio to text using speech-to-text providers.

    The Transcriber converts spoken audio into text using
    state-of-the-art speech recognition models.

    Features:
    - Multi-language support (auto-detection or specified)
    - Word-level and segment timestamps
    - Speaker diarization (where supported)
    - Audio translation to English

    Use cases:
    - Meeting transcription
    - Voice command processing
    - Podcast/video captioning
    - Voice message processing
    - Call center analytics
    - Accessibility features

    Supported Providers:
    - OpenAI Whisper (recommended)
    """

    class Input(NodeInput):
        audio: str = Field(
            description="Audio source: file path, URL, or base64-encoded audio",
            examples=[
                "/path/to/audio.mp3",
                "https://example.com/audio.wav",
            ],
        )
        language: Optional[str] = Field(
            default=None,
            description="Language code (ISO 639-1). Auto-detected if not specified.",
            examples=["en", "es", "fr", "de", "ja"],
        )
        timestamps: bool = Field(
            default=False,
            description="Include segment-level timestamps",
        )
        word_timestamps: bool = Field(
            default=False,
            description="Include word-level timestamps (more detailed)",
        )
        translate: bool = Field(
            default=False,
            description="Translate to English (for non-English audio)",
        )
        prompt: Optional[str] = Field(
            default=None,
            description="Optional prompt to guide transcription (e.g., spelling, context)",
            examples=[
                "This is a technical discussion about Kubernetes.",
                "Names: John Smith, Jane Doe",
            ],
        )
        response_format: str = Field(
            default="text",
            description="Output format: text, json, srt, vtt",
        )

    class Output(NodeOutput):
        text: str = Field(description="Transcribed text content")
        segments: List[Dict[str, Any]] = Field(
            default_factory=list,
            description="Timestamped segments (if timestamps enabled)",
        )
        words: List[Dict[str, Any]] = Field(
            default_factory=list,
            description="Word-level timestamps (if word_timestamps enabled)",
        )
        language: str = Field(
            default="",
            description="Detected or specified language",
        )
        duration_seconds: float = Field(
            default=0.0,
            description="Audio duration in seconds",
        )
        model: str = Field(default="", description="Model used for transcription")
        confidence: float = Field(
            default=1.0,
            ge=0.0,
            le=1.0,
            description="Overall transcription confidence",
        )

    class Config:
        requires_llm: bool = False  # Uses audio provider, not LLM
        timeout_seconds: int = 300  # Audio processing can be slow

    async def execute(self, input: Input, context) -> Output:
        """
        Execute transcription using the audio provider.

        Args:
            input: The validated Input model
            context: Execution context with providers

        Returns:
            Output with transcribed text and metadata
        """
        # Get audio provider from context
        audio_provider = getattr(context, "audio", None)

        if not audio_provider:
            # Fallback for testing
            return self.Output(
                text=f"[Mock transcription of: {input.audio}]",
                language=input.language or "en",
                model="mock",
            )

        # Perform transcription
        if input.translate:
            # Use translate method if available
            if hasattr(audio_provider, "translate"):
                result = await audio_provider.translate(
                    audio=input.audio,
                    prompt=input.prompt,
                )
            else:
                result = await audio_provider.transcribe(
                    audio=input.audio,
                    language=input.language,
                    prompt=input.prompt,
                    timestamps=input.timestamps,
                    word_timestamps=input.word_timestamps,
                )
        else:
            result = await audio_provider.transcribe(
                audio=input.audio,
                language=input.language,
                prompt=input.prompt,
                timestamps=input.timestamps,
                word_timestamps=input.word_timestamps,
            )

        # Handle error case
        if not result.success:
            raise ValueError(result.error or "Transcription failed")

        # Format segments if available
        segments = []
        if result.segments:
            for seg in result.segments:
                segments.append({
                    "text": seg.text,
                    "start": seg.start,
                    "end": seg.end,
                    "confidence": seg.confidence if hasattr(seg, "confidence") else 1.0,
                })

        # Format words if available
        words = []
        if result.words:
            for word in result.words:
                words.append({
                    "word": word.word,
                    "start": word.start,
                    "end": word.end,
                    "confidence": word.confidence if hasattr(word, "confidence") else 1.0,
                })

        return self.Output(
            text=result.text,
            segments=segments,
            words=words,
            language=result.language or input.language or "",
            duration_seconds=result.duration_seconds or 0.0,
            model=result.model or audio_provider.name,
            confidence=1.0,  # Whisper doesn't provide overall confidence
        )
