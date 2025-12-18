"""
Tests for audio nodes.

Tests cover:
- TranscriberNode
- SynthesizerNode
"""

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock

from flowmason_lab.nodes.audio import TranscriberNode, SynthesizerNode


class TestTranscriberNode:
    """Tests for TranscriberNode."""

    def test_node_metadata(self):
        """Test node has correct metadata."""
        assert hasattr(TranscriberNode, "_flowmason_metadata")
        meta = TranscriberNode._flowmason_metadata
        assert meta["name"] == "transcriber"
        assert meta["category"] == "audio"
        assert "speech-to-text" in meta["tags"]

    def test_input_schema(self):
        """Test input schema fields."""
        input_schema = TranscriberNode.Input.model_json_schema()
        props = input_schema["properties"]
        assert "audio" in props
        assert "language" in props
        assert "timestamps" in props
        assert "word_timestamps" in props
        assert "translate" in props

    def test_output_schema(self):
        """Test output schema fields."""
        output_schema = TranscriberNode.Output.model_json_schema()
        props = output_schema["properties"]
        assert "text" in props
        assert "segments" in props
        assert "words" in props
        assert "language" in props
        assert "duration_seconds" in props

    def test_input_validation(self):
        """Test input validation."""
        input_obj = TranscriberNode.Input(
            audio="/path/to/audio.mp3",
            language="en",
            timestamps=True,
        )
        assert input_obj.audio == "/path/to/audio.mp3"
        assert input_obj.timestamps is True

    @pytest.mark.asyncio
    async def test_execute_without_provider(self):
        """Test execution without provider returns mock."""
        node = TranscriberNode()
        input_obj = TranscriberNode.Input(audio="test.mp3")
        context = Mock()
        context.audio = None

        result = await node.execute(input_obj, context)

        assert "Mock transcription" in result.text
        assert result.model == "mock"

    @pytest.mark.asyncio
    async def test_execute_with_mocked_provider(self):
        """Test execution with mocked provider."""
        node = TranscriberNode()
        input_obj = TranscriberNode.Input(
            audio="meeting.mp3",
            language="en",
            timestamps=True,
        )

        # Mock audio provider
        mock_segment = MagicMock()
        mock_segment.text = "Hello everyone"
        mock_segment.start = 0.0
        mock_segment.end = 1.5

        mock_result = MagicMock()
        mock_result.text = "Hello everyone, welcome to the meeting."
        mock_result.language = "en"
        mock_result.duration_seconds = 5.0
        mock_result.segments = [mock_segment]
        mock_result.words = []
        mock_result.model = "whisper-1"
        mock_result.success = True

        mock_audio = MagicMock()
        mock_audio.transcribe = AsyncMock(return_value=mock_result)
        mock_audio.name = "openai"

        context = Mock()
        context.audio = mock_audio

        result = await node.execute(input_obj, context)

        assert result.text == "Hello everyone, welcome to the meeting."
        assert result.language == "en"
        assert result.duration_seconds == 5.0
        assert len(result.segments) == 1

    @pytest.mark.asyncio
    async def test_execute_with_translate(self):
        """Test execution with translation."""
        node = TranscriberNode()
        input_obj = TranscriberNode.Input(
            audio="spanish.mp3",
            translate=True,
        )

        mock_result = MagicMock()
        mock_result.text = "Translated text in English"
        mock_result.language = "es"
        mock_result.segments = []
        mock_result.words = []
        mock_result.model = "whisper-1"
        mock_result.success = True
        mock_result.duration_seconds = None

        mock_audio = MagicMock()
        mock_audio.translate = AsyncMock(return_value=mock_result)
        mock_audio.name = "openai"

        context = Mock()
        context.audio = mock_audio

        result = await node.execute(input_obj, context)

        assert "Translated" in result.text


class TestSynthesizerNode:
    """Tests for SynthesizerNode."""

    def test_node_metadata(self):
        """Test node has correct metadata."""
        assert hasattr(SynthesizerNode, "_flowmason_metadata")
        meta = SynthesizerNode._flowmason_metadata
        assert meta["name"] == "synthesizer"
        assert meta["category"] == "audio"
        assert "text-to-speech" in meta["tags"]

    def test_input_schema(self):
        """Test input schema fields."""
        input_schema = SynthesizerNode.Input.model_json_schema()
        props = input_schema["properties"]
        assert "text" in props
        assert "voice" in props
        assert "speed" in props
        assert "format" in props
        assert "output_path" in props

    def test_output_schema(self):
        """Test output schema fields."""
        output_schema = SynthesizerNode.Output.model_json_schema()
        props = output_schema["properties"]
        assert "audio_data" in props
        assert "audio_base64" in props
        assert "file_path" in props
        assert "duration_seconds" in props
        assert "voice" in props

    def test_input_validation(self):
        """Test input validation."""
        input_obj = SynthesizerNode.Input(
            text="Hello world",
            voice="nova",
            speed=1.0,
        )
        assert input_obj.text == "Hello world"
        assert input_obj.voice == "nova"

        # Test speed constraints
        with pytest.raises(Exception):
            SynthesizerNode.Input(text="test", speed=5.0)  # Max is 4.0

    @pytest.mark.asyncio
    async def test_execute_without_provider(self):
        """Test execution without provider returns mock."""
        node = SynthesizerNode()
        input_obj = SynthesizerNode.Input(text="Hello world")
        context = Mock()
        context.audio = None

        result = await node.execute(input_obj, context)

        assert result.audio_data == b"mock_audio_data"
        assert result.model == "mock"

    @pytest.mark.asyncio
    async def test_execute_with_mocked_provider(self):
        """Test execution with mocked provider."""
        node = SynthesizerNode()
        input_obj = SynthesizerNode.Input(
            text="Welcome to FlowMason",
            voice="nova",
            format="mp3",
        )

        # Mock audio provider
        mock_result = MagicMock()
        mock_result.audio_data = b"audio_bytes_here"
        mock_result.format = "mp3"
        mock_result.duration_seconds = 2.5
        mock_result.voice_id = "nova"
        mock_result.model = "tts-1"
        mock_result.characters = 20
        mock_result.success = True

        mock_audio = MagicMock()
        mock_audio.synthesize = AsyncMock(return_value=mock_result)
        mock_audio.name = "openai"

        context = Mock()
        context.audio = mock_audio

        result = await node.execute(input_obj, context)

        assert result.audio_data == b"audio_bytes_here"
        assert result.voice == "nova"
        assert result.duration_seconds == 2.5
        assert len(result.audio_base64) > 0

    @pytest.mark.asyncio
    async def test_execute_saves_to_file(self, tmp_path):
        """Test execution saves audio to file."""
        node = SynthesizerNode()
        output_file = tmp_path / "output.mp3"
        input_obj = SynthesizerNode.Input(
            text="Save this audio",
            output_path=str(output_file),
        )

        mock_result = MagicMock()
        mock_result.audio_data = b"audio_content"
        mock_result.format = "mp3"
        mock_result.duration_seconds = 1.0
        mock_result.voice_id = "default"
        mock_result.model = "tts-1"
        mock_result.characters = 15
        mock_result.success = True

        mock_audio = MagicMock()
        mock_audio.synthesize = AsyncMock(return_value=mock_result)
        mock_audio.name = "test"

        context = Mock()
        context.audio = mock_audio

        result = await node.execute(input_obj, context)

        assert result.file_path == str(output_file)
        assert output_file.exists()
        assert output_file.read_bytes() == b"audio_content"
