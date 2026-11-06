# Quaddis Flow → YouTube-agy Shorts: safe first integration

This is a **review-only** bridge from **already-exported Google Flow MP4s** to an editable, vertical Short. It does not log in to Flow, call Google's models, require an unofficial MCP, spend credits, or upload to YouTube.

## First use (Mac M1)
1. Install Python 3 and FFmpeg with FFprobe (for example: `brew install ffmpeg`).
2. Use Google Flow to create/export 3–12 clips you have rights and consent to use. For an existing presenter, choose the same character reference, voice, clothing and studio setup; reuse saved character assets where supported.
3. Store MP4s in `local_assets/` (do not commit these personal media files). Copy `docs/flow_shorts_manifest.example.json` to `docs/flow_shorts_manifest.json` and update its paths.
4. Run:
   ```bash
   python3 scripts/flow_shorts_review.py docs/flow_shorts_manifest.json --output videos/quaddis_review_1080p.mp4 --mobile-output videos/quaddis_review_iphone.mp4
   ```
5. Play the output all the way through. Check narration meaning, speech naturalness, lip sync, lighting, cuts, timing, PIP, facts, and licensing. The automatic QA only checks file/stream/duration/resolution; it cannot judge human voice quality.
6. **Do not publish until human review.**

Output: full HD 1080 × 1920 and optional phone-friendly 720 × 1280, H.264 + AAC MP4, full-screen and picture-in-picture clips, **topic-specific scene cards**, text overlays, CTA. Supply a `topic` in the JSON manifest; for every `mode: pip` scene provide 1–3 short `cards` strings. The review tool rejects generic fallback cards, missing topics and a timeline exceeding 60 seconds. Source narration audio is preserved; separate scene audio may differ in timbre or script and **must** be reviewed. Input footage resolution below 1080p is upscaled, not magically made sharper.

## What was fixed on this branch
- `voiceover.py` now refuses to silently invent synthetic tone audio if narration generation fails.
- `assemble_video.py` now refuses to write fake MP4 headers if FFmpeg is missing.
- `youtube_uploader.py` now uses FFprobe to reject non-playable media **even on dry run** and sends `status.containsSyntheticMedia` when uploading applicable AI content.
- `tests/test_shorts_regressions.py` captures those failures.

## Automation blueprint (proposed, not connected to Google account)
**Antigravity controller → topic research → approved script + precise scene list → Flow creation/approved exported clips → this local FFmpeg adapter → automatic technical QA → human review → optional upload.**

Google's official Flow web UI supports Omni Flash 1.2 extending short clips for AI Pro subscribers; video-to-video generation, characters, audio consistency, and duration remain subject to model restrictions, credits and availability. The Google AI Pro Flow credits do **not** grant general free video API calls.

**Do not trust a third-party Flow MCP / Chrome extension with your Google session cookies.** An extension can automate clicking the Flow UI but cannot remove credits, guarantee identical avatars, make speech flawless, or bypass account restrictions. Only add integrations after source review, permission audit and throwaway-account testing; prefer an official supported API or explicit export-handoff.

## Example prompt for Antigravity
```text
In my existing Skp693/YouTube-agy repo, build a 45-second Quaddis ATS Short
from 4 human-approved Google Flow MP4 clips saved in local_assets/.
Use docs/flow_shorts_manifest.json and scripts/flow_shorts_review.py; each PIP scene must have relevant cards and the manifest must have a topic.
Maintain one presenter, 1080x1920, the QUADDIS identity, readable labels
and a picture-in-picture presenter where appropriate. Do not synthesize
fake voice, scrape cookies, use a paid API, spend credits, or publish.
Run the renderer and FFprobe. Only report technical success if a real
playable MP4 exists. Give me the preview and an honest quality checklist.
```

## Production TODO
- Add true topic-linked script-to-scene matching, consistent *single* narrator voice, forced alignment of actual audio to captions, and synchronized PIP presenter lip movements.
- Add original B-roll/screen recordings for each topic, rather than only relying on Flow character talking-head clips.
- Wire the actual dashboard's Shorts mode to the manifest/renderer and quality check after acceptance.
- Validate voice and lip-sync with a human **before** enabling automation across a full 60-second video.
- Audit third-party license terms, synthetic-media labeling, social-platform policies, and any Google quota changes.

This starter is not a one-prompt Flow generation system. Flow creation is deliberately manual until safe, supported account authorization exists.
