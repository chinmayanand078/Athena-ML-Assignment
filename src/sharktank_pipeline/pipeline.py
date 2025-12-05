"""End-to-end orchestration of the Shark Tank pitch analyzer."""

import importlib.util
from pathlib import Path
from typing import Optional

from .audio_processor import analyze_delivery
from .content_analyzer import analyze_content
from .models import PanelResponse
from .shark_panel import run_panel


TRANSCRIPTION_WARNING = "No ASR backend detected. Provide a transcript with --transcript to skip ASR."


def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio using Whisper when available.

    This function deliberately uses importlib to avoid hard dependencies at runtime.
    """

    if importlib.util.find_spec("whisper") is None:
        raise RuntimeError(TRANSCRIPTION_WARNING)

    import whisper

    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result.get("text", "").strip()


def run_pipeline(audio_path: str, transcript: Optional[str] = None) -> PanelResponse:
    """Execute both pipelines and return the aggregated panel response."""

    audio_exists = Path(audio_path)
    if not audio_exists.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    if not transcript:
        transcript = transcribe_audio(audio_path)

    delivery = analyze_delivery(audio_path, transcript)
    content = analyze_content(transcript)
    return run_panel(delivery, content)

