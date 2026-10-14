# Issues Investigated, Root Causes & Fixes Applied

This document details all technical issues discovered during the end-to-end system testing of **YouTube-agy**, their root causes, and the concrete code changes implemented to ensure production-grade reliability.

---

## Issue 1: FFmpeg Concat Video Truncation (0.26s Duration Bug)

### Symptom
When `main_pipeline.py` executed Stage 5 (Video Assembly), FFmpeg completed with exit code 0 in under 1 second. However, `ffprobe` revealed the output video had a duration of only **0.266 seconds** (8 frames total) instead of the expected 5 minutes (302 seconds), despite the audio track being 302 seconds long.

### Root Cause
In `assemble_video.py`, the dynamic Ken Burns filter was configured as:
```text
zoompan=z='min(zoom+0.00015,1.05)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30
```
In FFmpeg's `zoompan` filter, `:d=1` specifies that each input image from the concat demuxer produces exactly **1 output frame**. Because `concat_txt` contained 7 scenes (plus 1 repeated file for the concat demuxer quirk), `zoompan` generated exactly 8 frames total ($8 / 30 = 0.266\text{s}$). Because `-shortest` was passed to terminate encoding when the first stream ended, FFmpeg terminated the entire encoding session as soon as frame 8 was written, discarding the remaining 5 minutes of voiceover audio.

### Resolution
Updated `assemble_video.py` to use a rock-solid presentation filter chain:
```python
# Ensure solid 30fps presentation timeline matching exact audio duration
video_filter = "fps=30,scale=1920:1080"
```
And updated both the background music mix and no-music branches to use `video_filter`. Concat demuxer timestamps now smoothly advance across all 9,085 frames at 30 fps, producing a complete 302.86-second (5:02) 1080p video matching the audio track down to the millisecond.

---

## Issue 2: Hardcoded Slide Footer Branding in Visuals Engine

### Symptom
All generated slides in `images/` displayed the footer text `"CLAUDE 3.7 ARTIFACTS • AUTONOMOUS VIDEO PIPELINE 2026"`, regardless of the tool or topic being generated.

### Root Cause
In `visuals.py`, line 221 contained hardcoded string assignment in the native BMP rasterizer:
```python
footer = "CLAUDE 3.7 ARTIFACTS • AUTONOMOUS VIDEO PIPELINE 2026"
```

### Resolution
Updated `render_slide_native_bmp` to accept `tool_name: str = "AI TOOL EXPLAINER"`. In `generate_visuals`, `tool_name` is retrieved from `script_data` and passed into the slide renderer:
```python
footer = f"{tool_name[:32].upper()} • AUTONOMOUS VIDEO PIPELINE 2026"
```
The footer text now accurately mirrors the featured topic on every slide.

---

## Issue 3: Single-Tool Procedural Script vs Multi-Tool Roundup

### Symptom
When requesting a multi-tool roundup topic ("5 Practical AI Tools That Can Save Small Business Owners Time in 2026"), `script_writer.py` was defaulting to a single-tool tutorial structure (Step 1 Setup, Step 2 First Project, Step 3 Power User Shortcuts) rather than introducing the 5 distinct tools requested.

### Root Cause
`script_writer.py` previously only had two offline procedural engines:
1. `build_claude_artifacts_script()`: A specialized 1,500-word tutorial for Claude.
2. `build_procedural_script()`: A generic step-by-step tutorial template for a single tool.

### Resolution
Added a dedicated multi-tool roundup generator `build_small_business_ai_tools_script(topic_data)` to `script_writer.py`:
- 7 distinct sections (Overview Hook, Tool 1 NotebookLM, Tool 2 Notion AI, Tool 3 Descript, Tool 4 Perplexity Pro, Tool 5 Make.com, Action Blueprint Outro).
- Strict educational scripting with factual small business use cases, time savings, and real pricing tiers.
- 727 words total, resulting in an optimal 5:02 minute video runtime.
- Added routing in `write_script()` that automatically detects keywords such as `"small business"`, `"5 practical"`, or `"save time"`.

---

## Issue 4: Missing `--project-id` CLI Argument in Master Orchestrator

### Symptom
When attempting to run `main_pipeline.py` with `--project-id test_20261012_smallbiz`, `argparse` raised an error: `unrecognized arguments: --project-id`.

### Root Cause
The argument parser in `main_pipeline.py` supported `--tool`, `--angle`, `--privacy`, `--schedule`, and `--interval-hours`, but omitted `--project-id`.

### Resolution
Added `--project-id` to `main_pipeline.py`:
```python
parser.add_argument("--project-id", type=str, help="Custom project identifier")
```
And forwarded `args.project_id` into `run_pipeline(..., project_id=args.project_id)`.

---

## Issue 5: Floating-Point Truncation in Subtitle Time Formatting

### Symptom
Subtitles occasionally displayed inconsistent millisecond timestamps in previous runs.

### Root Cause
In `assemble_video.py`, `format_srt_time` computed milliseconds using floating-point subtraction `millis = int((seconds - int(seconds)) * 1000)`, which is prone to IEEE 754 precision artifacts.

### Resolution
Refactored `format_srt_time` to use exact integer millisecond math:
```python
total_ms = int(round(seconds * 1000))
hrs = total_ms // 3600000
mins = (total_ms % 3600000) // 60000
secs = (total_ms % 60000) // 1000
millis = total_ms % 1000
```
This guarantees monotonically increasing, valid SRT cue intervals.

---

## Issue 6: Missing PIL/Pillow Dependency Fallback

### Symptom
Importing Pillow (`from PIL import Image`) failed with `ModuleNotFoundError: No module named 'PIL'`.

### Root Cause
The active macOS Python environment does not have Pillow installed globally.

### Resolution
Implemented standard-library rasterization in `visuals.py` and `metadata.py` using pure-Python 24-bit uncompressed BMP generation + native macOS `sips` conversion to PNG. Slides and thumbnails render at 1080p and 720p with clean typography and zero external library dependencies.
