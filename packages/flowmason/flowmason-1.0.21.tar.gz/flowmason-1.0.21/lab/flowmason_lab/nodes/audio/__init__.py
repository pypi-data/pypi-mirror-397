"""
FlowMason Audio Nodes

Provides audio processing nodes for speech-to-text (STT) and
text-to-speech (TTS) operations.

Built-in Nodes:
- transcriber: Convert speech audio to text
- synthesizer: Convert text to speech audio

Usage:
    # Transcribe audio to text
    {
        "id": "transcribe-call",
        "component": "transcriber",
        "inputs": {
            "audio": "{{input.audio_file}}",
            "timestamps": true,
            "language": "en"
        }
    }

    # Generate speech from text
    {
        "id": "generate-response",
        "component": "synthesizer",
        "inputs": {
            "text": "{{upstream.generate-text.result}}",
            "voice": "nova",
            "format": "mp3"
        }
    }
"""

from .transcriber import TranscriberNode
from .synthesizer import SynthesizerNode

__all__ = [
    "TranscriberNode",
    "SynthesizerNode",
]
