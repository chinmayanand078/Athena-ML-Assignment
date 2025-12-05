"""CLI entry point for the Shark Tank pitch analyzer."""

import argparse
import json
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from sharktank_pipeline.pipeline import TRANSCRIPTION_WARNING, run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Shark Tank pitch analyzer")
    parser.add_argument("--audio", required=True, help="Path to the audio file (wav/mp3)")
    parser.add_argument("--transcript", required=False, help="Optional transcript to skip ASR")
    parser.add_argument("--output", required=False, help="Optional JSON output path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not Path(args.audio).exists():
        raise FileNotFoundError(f"Audio file not found: {args.audio}")

    try:
        response = run_pipeline(args.audio, transcript=args.transcript)
    except RuntimeError as exc:  # whisper not installed
        raise SystemExit(f"{TRANSCRIPTION_WARNING} Original error: {exc}")

    serialized = {
        "delivery": response.delivery.__dict__,
        "content": response.content.__dict__,
        "feedback": [item.__dict__ for item in response.feedback],
        "final_recommendation": response.final_recommendation,
    }

    pretty = json.dumps(serialized, indent=2)
    print(pretty)

    if args.output:
        Path(args.output).write_text(pretty, encoding="utf-8")


if __name__ == "__main__":
    main()

