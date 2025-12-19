"""
Tests for audio providers.

Tests cover:
- AudioProvider base class
- TranscriptionResult and SynthesisResult dataclasses
- OpenAI audio provider
- ElevenLabs provider
- Registry functions
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock

from flowmason_core.providers.audio import (
    AudioProvider,
    AudioFormat,
    TranscriptionResult,
    TranscriptionSegment,
    SynthesisResult,
    VoiceInfo,
    AudioProviderConfig,
    OpenAIAudioProvider,
    ElevenLabsProvider,
    register_audio_provider,
    get_audio_provider,
    list_audio_providers,
)


class TestAudioFormat:
    """Tests for AudioFormat enum."""

    def test_format_values(self):
        """Test audio format values."""
        assert AudioFormat.MP3.value == "mp3"
        assert AudioFormat.WAV.value == "wav"
        assert AudioFormat.OGG.value == "ogg"
        assert AudioFormat.FLAC.value == "flac"


class TestTranscriptionResult:
    """Tests for TranscriptionResult dataclass."""

    def test_basic_result(self):
        """Test basic transcription result."""
        result = TranscriptionResult(
            text="Hello world",
            language="en",
        )
        assert result.text == "Hello world"
        assert result.language == "en"
        assert result.success is True

    def test_result_with_segments(self):
        """Test result with segments."""
        segments = [
            TranscriptionSegment(text="Hello", start=0.0, end=0.5),
            TranscriptionSegment(text="world", start=0.5, end=1.0),
        ]
        result = TranscriptionResult(
            text="Hello world",
            segments=segments,
        )
        assert len(result.segments) == 2
        assert result.segments[0].text == "Hello"

    def test_error_result(self):
        """Test error result."""
        result = TranscriptionResult(
            text="",
            success=False,
            error="Audio file not found",
        )
        assert result.success is False
        assert result.error == "Audio file not found"

    def test_to_dict(self):
        """Test serialization."""
        result = TranscriptionResult(
            text="Test",
            language="en",
            duration_seconds=5.0,
        )
        d = result.to_dict()
        assert d["text"] == "Test"
        assert d["language"] == "en"
        assert d["duration_seconds"] == 5.0


class TestSynthesisResult:
    """Tests for SynthesisResult dataclass."""

    def test_basic_result(self):
        """Test basic synthesis result."""
        result = SynthesisResult(
            audio_data=b"audio_bytes",
            format=AudioFormat.MP3,
        )
        assert result.audio_data == b"audio_bytes"
        assert result.format == AudioFormat.MP3
        assert result.success is True

    def test_result_with_metadata(self):
        """Test result with metadata."""
        result = SynthesisResult(
            audio_data=b"audio",
            format=AudioFormat.MP3,
            duration_seconds=2.5,
            voice_id="nova",
            model="tts-1",
            characters=50,
        )
        assert result.duration_seconds == 2.5
        assert result.voice_id == "nova"
        assert result.characters == 50

    def test_error_result(self):
        """Test error result."""
        result = SynthesisResult(
            audio_data=b"",
            format=AudioFormat.MP3,
            success=False,
            error="Invalid voice ID",
        )
        assert result.success is False


class TestVoiceInfo:
    """Tests for VoiceInfo dataclass."""

    def test_basic_voice(self):
        """Test basic voice info."""
        voice = VoiceInfo(
            id="nova",
            name="Nova",
        )
        assert voice.id == "nova"
        assert voice.name == "Nova"

    def test_voice_with_details(self):
        """Test voice with full details."""
        voice = VoiceInfo(
            id="nova",
            name="Nova",
            description="Warm and friendly",
            gender="female",
            language="en",
            accent="American",
        )
        assert voice.gender == "female"
        assert voice.accent == "American"


class TestAudioRegistry:
    """Tests for audio provider registry."""

    def test_list_providers(self):
        """Test listing providers."""
        providers = list_audio_providers()
        assert "openai" in providers
        assert "elevenlabs" in providers

    def test_get_provider(self):
        """Test getting provider class."""
        provider_class = get_audio_provider("openai")
        assert provider_class is not None
        assert issubclass(provider_class, AudioProvider)


class TestOpenAIAudioProvider:
    """Tests for OpenAI audio provider."""

    def test_init_requires_api_key(self):
        """Test init requires API key."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="API key required"):
                OpenAIAudioProvider()

    def test_init_with_api_key(self):
        """Test init with API key."""
        provider = OpenAIAudioProvider(api_key="test-key")
        assert provider.api_key == "test-key"
        assert provider.name == "openai"

    def test_capabilities(self):
        """Test capabilities."""
        provider = OpenAIAudioProvider(api_key="test-key")
        caps = provider.capabilities
        assert "speech_to_text" in caps
        assert "text_to_speech" in caps

    def test_available_voices(self):
        """Test available voices."""
        provider = OpenAIAudioProvider(api_key="test-key")
        voices = provider.available_voices
        voice_ids = [v.id for v in voices]
        assert "nova" in voice_ids
        assert "alloy" in voice_ids
        assert "echo" in voice_ids

    @pytest.mark.asyncio
    async def test_transcribe_mock(self):
        """Test transcription with mocked client."""
        provider = OpenAIAudioProvider(api_key="test-key")

        # Mock the client
        mock_response = MagicMock()
        mock_response.text = "Hello world"
        mock_response.language = "en"
        mock_response.duration = 2.5

        mock_client = MagicMock()
        mock_client.audio.transcriptions.create = AsyncMock(return_value=mock_response)
        provider._async_client = mock_client

        # Mock file loading
        with patch.object(provider, '_load_audio', return_value=b"audio_data"):
            result = await provider.transcribe("test.mp3")

        assert result.success is True
        assert result.text == "Hello world"

    @pytest.mark.asyncio
    async def test_synthesize_mock(self):
        """Test synthesis with mocked client."""
        provider = OpenAIAudioProvider(api_key="test-key")

        # Mock the client
        mock_response = MagicMock()
        mock_response.content = b"audio_bytes"

        mock_client = MagicMock()
        mock_client.audio.speech.create = AsyncMock(return_value=mock_response)
        provider._async_client = mock_client

        result = await provider.synthesize("Hello world", voice="nova")

        assert result.success is True
        assert result.audio_data == b"audio_bytes"


class TestElevenLabsProvider:
    """Tests for ElevenLabs provider."""

    def test_init_requires_api_key(self):
        """Test init requires API key."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="API key required"):
                ElevenLabsProvider()

    def test_init_with_api_key(self):
        """Test init with API key."""
        provider = ElevenLabsProvider(api_key="test-key")
        assert provider.api_key == "test-key"
        assert provider.name == "elevenlabs"

    def test_capabilities(self):
        """Test capabilities (TTS only)."""
        provider = ElevenLabsProvider(api_key="test-key")
        caps = provider.capabilities
        assert "text_to_speech" in caps
        assert "voice_cloning" in caps
        # ElevenLabs doesn't support STT
        assert "speech_to_text" not in caps

    def test_default_voices(self):
        """Test default voices list."""
        provider = ElevenLabsProvider(api_key="test-key")
        # Access the class constant
        assert len(provider.DEFAULT_VOICES) > 0
        voice_names = [v.name for v in provider.DEFAULT_VOICES]
        assert "Rachel" in voice_names

    @pytest.mark.asyncio
    async def test_transcribe_not_supported(self):
        """Test that transcription returns error."""
        provider = ElevenLabsProvider(api_key="test-key")
        result = await provider.transcribe("test.mp3")
        assert result.success is False
        assert "not support" in result.error.lower()

    @pytest.mark.asyncio
    async def test_synthesize_mock(self):
        """Test synthesis with mocked client."""
        provider = ElevenLabsProvider(api_key="test-key")

        # Mock the client
        mock_client = MagicMock()
        mock_client.generate.return_value = iter([b"chunk1", b"chunk2"])
        provider._client = mock_client

        result = await provider.synthesize("Hello world")

        assert result.success is True
        assert result.audio_data == b"chunk1chunk2"
