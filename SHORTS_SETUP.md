# Shorts Studio — safe first integration for YouTube-agy

**Status: tested local scene composer, not an autonomous script/avatar generator.** The existing long-form pipeline and desktop dashboard are unchanged. This adds a new, optional local 9:16 workflow.

## What this solves
- Assembles a **45-second example** (configurable, up to 60 seconds) in 1080 × 1920, H.264 MP4, 30 fps.
- Has three scene modes: `presenter_full`, `presenter_pip` (a real speaking clip over B-roll), and `broll` (video plus approved narration recording).
- **Presenter audio comes from the actual avatar video**, never a separately dubbed recording pretending to be lip-synced. If presenter video is muted, it fails.
- **No artificial sine-wave or silent fallback**. If narration recording is missing/too short, it fails instead of exporting a bogus Short.
- Preserves existing files and **never uploads** to YouTube, calls paid video APIs, handles account credentials, or changes existing long-form code.

## Prepare media (no password or API secrets)
1. Download your 10-second video from Google Flow as MP4: Google Flow > project > hover asset > More > Download. Save to `shorts_assets/flow_presenter_intro.mp4`. Do not remove visible or invisible watermarks.
2. Provide B-roll (your own screen recording) and separately high-quality, approved narration WAV for the non-avatar scene(s). Example names: `shorts_assets/ats_screen_recording.mp4`, `shorts_assets/ats_demo.mp4` and `shorts_assets/approved_narration.wav`.
3. Use only media you are permitted to use. The same voice/accent across the Flow presenter and separate narration must be **checked by ear**; the composer does not generate speech or measure similarity.

## Mac installation and render
```bash
cd ~/YouTube-agy
# FFmpeg and FFprobe must be installed. If missing: brew install ffmpeg
cp examples/shorts_manifest.example.json examples/shorts_manifest.json
# Edit asset filenames and durations in examples/shorts_manifest.json
python3 shorts_pipeline.py --manifest examples/shorts_manifest.json
```

Output for the example: `videos/quaddis_ats_short.mp4`, only after the referenced source files exist.

Optional captions: add `"captions": "../shorts_assets/approved_captions.srt"` to the root of JSON; FFmpeg must include the `subtitles` filter. Only use manually verified, correctly timed SRT; the caption burner has not been tested on the user's Mac.

## Quality checks and reproducible tests
- Fails if any scene file, original presenter audio, or narration is missing or too short.
- 60-second preset cap, FFprobe validation, 1080x1920 output check, audio stream required.
- Tests are checked in: `python3 -m unittest discover -s tests -v`.
- A synthetic FFmpeg render is included in **tests only**. Production code does not create artificial voice.
- Human review still required: naturalness, actual lip-sync, captions, pacing, privacy, rights, and brand consistency. Audio-track presence alone cannot prove a natural human voice.

## Google Flow / Flow MCP
- **Recommended:** Create the avatar in Google Flow, download the MP4 and import it. This avoids credentials in YouTube-agy and incurs no extra software charge beyond existing subscription credits.
- Community `google-flow-mcp` projects do exist. They use browser automation, are unofficial, and can break when Flow changes. Do not automatically install them or expose a signed-in browser to unreviewed code.
- Google AI Pro Flow credits do not create a free unlimited Gemini API.
- Preserve Google Flow's SynthID marks. No secret keys or browser session cookies belong in the public repository.

## Exact current limitation
This milestone is a **working local assembly adapter**, not one-prompt AI direction. It cannot yet generate 45 seconds of human-like narration from topic text, add new lip-synced speech to a 10-second clip, guarantee consistent voices, or automatically fetch Flow clips. Actual integration should be calibrated against the user's own clip *before* connecting to the existing dashboard or enabling automatic jobs. No YouTube publishing is performed.
