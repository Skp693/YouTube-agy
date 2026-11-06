# Quaddis audio-first Shorts: one narrator, matching scenes

Goal: create 8–60-second review videos without switching among unrelated Flow voices or placing a moving mouth over unrelated audio.

## Supported sources

1. A single approved presenter recording (narration_source_video) with a full narration. Scenes marked presenter_native may use ONLY that exact source file, with media_seek equal to the corresponding master narration start. One audio track continues through talking-head and visual-insert scenes.
2. A separate approved recorded narration (narration_audio, WAV or MP3). In this mode, moving-mouth presenter scenes are prohibited until separately lip-synced clips exist. Still portrait (pip_still) and topic-specific graphics or B-roll can be used.

The system cannot certify voice identity, natural speaking style or lip sync simply by finding an audio stream.

## Steps (Mac M1, no new subscriptions)

1. Install FFmpeg: brew install ffmpeg
2. Save authorized sources and your avatar reference in local_assets/ (excluded from Git).
3. Copy docs/narration_first_manifest.example.json to docs/narration_first_manifest.json. Point it to your actual footage and single narration master.
4. Make all scene start/end time ranges contiguous, from 0 to the audio duration. For moving B-roll video use no_visible_speaking_faces=true only after checking the footage truly has no talking faces.
5. Add captions with real, verified timestamps from a transcript of this exact audio. No captions are invented. Example: {"start":0.25,"end":1.45,"text":"Your resume is scanned."}
6. Render review MP4:
   python3 scripts/narration_first_shorts.py docs/narration_first_manifest.json --output videos/audio_first_review.mp4 --width 720
   Use --width 1080 for full HD 1080x1920.
7. Watch end-to-end and separately approve factual accuracy, natural speech, exact words, lip-sync, graphics, caption timing, music/licensing and branding. No public upload before review.

Automatic checks: topic exists, real audio stream, duration 8–60 seconds, scene coverage and chronological order, source media existence, matching native-presenter source and timecodes, overlapping captions blocked, MP4 streams and output dimensions checked.

Caveats: No Google Flow generation, MCP login, Chrome cookie access, paid API call, voice cloning, perfect lip-sync guarantee or automatic YouTube publishing. This is an offline assembly and validation module.

## Antigravity starter instruction

Use my existing Skp693/YouTube-agy repository. Given one approved 45-second narration track and exported Flow media, generate a safe narration-first manifest with correct scene timecodes and verified transcript timing. Never mix separate Flow scene audio or show an unrelated moving talking face. Use scripts/narration_first_shorts.py to create a vertical H.264/AAC review MP4. Run quality checks, return the actual preview, and wait for my approval. Do not spend credits, publish, or access my Google session cookies.

## Next dependencies

- One consented full-length natural narration in the desired voice, plus its exact transcript.
- Matching actor lip-sync content when on screen (or native recording as above).
- Fact-checked topic-specific motion visuals.
- Real reviewed captions with accurate timing.
- Optional approval-gated private upload after the MP4 passes human review.
