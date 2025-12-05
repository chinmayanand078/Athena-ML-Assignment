"""Audio feature extraction and delivery scoring utilities."""

import importlib.util
from typing import Dict, List, Tuple

import numpy as np

from .models import DeliveryMetrics


def _require_librosa():
    if importlib.util.find_spec("librosa") is None:
        raise ImportError("librosa is required for audio processing. Install it via `pip install librosa`.")
    import librosa

    return librosa


def load_audio(path: str, target_sr: int = 16000) -> Tuple[np.ndarray, int]:
    """Load audio as a mono waveform.

    Args:
        path: Path to the audio file.
        target_sr: Target sampling rate in Hz.

    Returns:
        Tuple of waveform samples and sampling rate.
    """

    librosa = _require_librosa()
    waveform, sr = librosa.load(path, sr=target_sr, mono=True)
    return waveform, sr


def extract_features(waveform: np.ndarray, sr: int) -> Dict[str, float]:
    """Extract pitch, pace, energy, pause ratio, and monotony indicators."""

    librosa = _require_librosa()

    pitch_track, _ = librosa.pyin(waveform, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7"))
    pitch_mean = float(np.nanmean(pitch_track)) if np.nanmean(pitch_track) == np.nanmean(pitch_track) else 0.0

    tempo, _ = librosa.beat.beat_track(y=waveform, sr=sr)
    pace_wpm = float(tempo) * 2.0  # heuristic to convert beats per minute to words per minute

    rms = librosa.feature.rms(y=waveform)[0]
    volume_variance = float(np.var(rms))

    intervals = librosa.effects.split(waveform, top_db=25)
    non_silent = sum((end - start) for start, end in intervals)
    pause_ratio = float(1 - (non_silent / len(waveform)))

    monotony_score = float(1.0 - np.nanstd(pitch_track) / (np.nanmean(pitch_track) + 1e-6)) if np.nanmean(pitch_track) else 1.0

    return {
        "pitch_mean": pitch_mean,
        "pace_wpm": pace_wpm,
        "volume_variance": volume_variance,
        "pause_ratio": pause_ratio,
        "monotony_score": monotony_score,
    }


def detect_fillers(transcript: str, fillers: List[str] | None = None) -> int:
    """Count filler words within the transcript."""

    if fillers is None:
        fillers = ["um", "uh", "like", "you know", "er", "ah"]

    transcript_lower = transcript.lower()
    return sum(transcript_lower.count(filler) for filler in fillers)


def derive_emotion(monotony: float, pause_ratio: float, pace_wpm: float) -> str:
    """Infer an approximate emotional tone from basic prosody features."""

    if monotony > 0.8 or pause_ratio > 0.3:
        return "Nervous"
    if pace_wpm < 110:
        return "Calm"
    if pace_wpm > 180:
        return "Energetic"
    return "Confident"


def score_delivery(features: Dict[str, float], filler_count: int) -> float:
    """Combine features into a 0–100 delivery score."""

    clarity = max(0.0, 30 - (features["pause_ratio"] * 100))
    energy = min(30.0, max(0.0, features["volume_variance"] * 5))
    confidence_penalty = min(20.0, features["monotony_score"] * 20)
    filler_penalty = min(20.0, filler_count * 1.5)

    base = clarity + energy + (30 - confidence_penalty) + (20 - filler_penalty)
    return float(max(0.0, min(100.0, base)))


def analyze_delivery(audio_path: str, transcript: str = "") -> DeliveryMetrics:
    """Run the voice and tone pipeline for a given audio file.

    Args:
        audio_path: Location of the audio file to analyze.
        transcript: Optional transcript used for filler detection.

    Returns:
        DeliveryMetrics populated with extracted features and scores.
    """

    waveform, sr = load_audio(audio_path)
    features = extract_features(waveform, sr)
    filler_count = detect_fillers(transcript) if transcript else 0
    emotion = derive_emotion(features["monotony_score"], features["pause_ratio"], features["pace_wpm"])
    score = score_delivery(features, filler_count)

    return DeliveryMetrics(
        pitch_mean=features["pitch_mean"],
        pace_wpm=features["pace_wpm"],
        volume_variance=features["volume_variance"],
        pause_ratio=features["pause_ratio"],
        filler_count=filler_count,
        monotony_score=features["monotony_score"],
        emotion=emotion,
        delivery_score=score,
    )

