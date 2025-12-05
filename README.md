# Shark Tank Pitch Analyzer

This repository contains a reference implementation for a **multimodal Shark Tank pitch analyzer**. The system separates audio-based delivery analysis from content evaluation, then generates narrative feedback from a panel of virtual investor personas.

## Features
- **Pipeline 1 – Voice & Tone Analysis**: Extracts vocal features (pitch, pace, volume, pauses), detects emotional tone, flags filler words/hesitation, and produces a delivery score.
- **Pipeline 2 – Content & Business Logic**: Transcribes speech (or ingests a provided transcript) and grades problem clarity, differentiation, business model, market, revenue logic, and competition awareness. Detects pitch structure (Hook → Problem → Solution → Ask) and computes a business viability score.
- **Virtual Shark Panel**: Configurable investor personas use analysis outputs to produce personalized feedback and an investment verdict.

## Project Layout
```
src/
  sharktank_pipeline/
    audio_processor.py   # Audio feature extraction and delivery scoring
    content_analyzer.py  # Transcript-driven business scoring
    models.py            # Data structures shared across the pipeline
    shark_panel.py       # Persona definitions and feedback synthesis
    pipeline.py          # Orchestrates both pipelines and merges results
main.py                  # CLI entry point for running the analyzer
requirements.txt         # Recommended dependencies
```

## Quickstart
1. **Install dependencies** (Python 3.10+ recommended):
   ```bash
   pip install -r requirements.txt
   ```
   The audio pipeline depends on `librosa`; the optional Whisper ASR path depends on `openai-whisper`.

2. **Run the analyzer** on an audio file (provide a transcript to skip ASR):
   ```bash
   python main.py --audio path/to/pitch.wav --transcript "Your prepared transcript"
   ```

3. **Outputs**
   - Delivery metrics and score (0–100)
   - Business content scores (0–100)
   - Persona-specific feedback and final recommendation

## Notes
- The ASR stage is optional; you can supply a transcript directly when testing.
- Scoring heuristics are transparent and adjustable in the code to match rubric changes.
- Persona prompts are lightweight templates designed to be extended with LLM calls if desired.
- See `STATUS.md` for a candid checklist of what is implemented versus what remains from the assignment brief.
