# Premium-first video workflow (no new recurring subscriptions)

Status: implementation roadmap. Creative services are *not yet automatically connected* to this Python project. Real access/credit balance must be confirmed before calling a paid API.

## What is in the code today

- The desktop app runs `main_pipeline.py` with top-level `topic_selector.py`, `script_writer.py`, `voiceover.py`, `visuals.py`, `assemble_video.py`, `metadata.py` and `youtube_uploader.py`.
- There is a second implementation under `src/stages`. Do not maintain two independent production paths. Consolidate after verified regression coverage.
- `script_writer.py` can call the Gemini API only with a **separately authorized** API key. `config/settings.py` currently defaults to the older `gemini-1.5-pro` model. Check available models and free-tier quota before selecting a replacement.
- Google AI Pro, Google Flow, Canva subscriptions and Adobe Firefly creative credits are not equivalent to unrestricted programmatic API usage.
- This PR prevents the active pipeline from treating test-tone audio or a fake MP4 marker as a successful export.

## Preferred creative production flow

1. **Brief and fact-check:** Gemini/Google AI Pro for topic, research, script, visual plan; verify factual claims and attribution before approving a scene.
2. **Storyboard:** Save a structured scene manifest with narration, on-screen claim, duration, clip source, rights/license, and whether disclosure may be necessary. Favor real software screen recordings for tutorials over fabricated UI.
3. **Motion clips:** Generate limited, targeted cinematic cutaways in Google Flow using available AI credits. Export MP4 via the product UI. Do not automatically retry chargeable operations.
4. **Brand assets:** Reuse Canva Quaddis design **DAHYbplVzFg** ("Quaddis ATS — Editable 7-Scene Video Master") and brand guideline **DAHYGeeg96I**. Editable design sources remain in Canva; export approved media as production input.
5. **Finishing:** Use Adobe Express for transition polish, subtitles, layout and platform-specific edits. Firefly only for specific stills/limited generative assets; reserve credits for scenes with visual value. Preserve official Quaddis logos and correct brand colors.
6. **Audio:** Use a real, auditioned English voice. Native macOS speech is a no-additional-fee fallback, **not** evidence of premium speech quality. Never export synthetic test tones as narration.
7. **Local editing/render:** Mac M1 8 GB, FFmpeg 1080p H.264/AAC. Short test clips first, then 45–60 s Shorts, then 8–10 min exports.
8. **Human approval gate:** Verify audio quality, visuals, factual accuracy, rights, source links, caption timing, privacy, and any required YouTube synthetic-content disclosure. Keep YouTube upload disabled until explicit approval of the individual deliverable.

## Integration boundaries (do not spend without confirmation)

- **Google AI Pro:** Google Flow/Antigravity/Gemini app benefits depend on the account and remaining AI credits. A Gemini **API** key has its own billing and rate limits. Never treat a paid consumer subscription as API credit.
- **Adobe Firefly:** The user's stated **250 credits** are a planning limit, **not a live-verified remaining balance**. Premium image/video actions can deduct different numbers of credits. Prefer saving a clear prompt and generating once after approval.
- **Canva:** Existing user designs are accessible through the connected Canva workspace, but that does not yet provide an authenticated unattended media-export API in this repository.
- **Adobe Marketing Agent:** Adobe enterprise marketing/audience analytics, not the core video renderer. Add only if an eligible organization and data view are actually configured.
- **Plugin Creator / automation apps:** Optional orchestration layer, not a substitute for verified media generation, licensing, or secure credential storage.

## Engineering backlog (priority order)

1. **Safety: done in PR:** fail when speech unavailable or FFmpeg missing; regression tests and CI, no generated fake artifacts.
2. **Next:** validate MP4 with ffprobe (video + audio streams, duration, output size); reject an invalid file before YouTube dry run or upload. Remove fake DRY_RUN YouTube URLs.
3. **Next:** implement a **local, user-controlled premium media import**: a scene manifest accepting exported Canva/Adobe PNGs and Google Flow MP4s with per-scene timestamps, license metadata, and strict path validation. Preserve duration and aspect ratio. Never silently replace video with static slides.
4. **Next:** proper word-aligned captions and audio loudness validation; current section-level timing is not true word alignment.
5. **Next:** provide 9:16 Shorts profile and 16:9 long-form profile, brand-aware graphics, scene pacing/retention checks, transition tests.
6. **Next:** consolidate `src/stages` and top-level code, pin tested dependencies, update models, run the full suite on macOS Apple Silicon, and add end-to-end output validation.
7. **Later:** per-video, separately confirmed YouTube upload; multi-platform posting only after reliability and permission verification.

## First 45-second pilot

Topic: "Three resume formatting mistakes that confuse ATS systems".
- 0–5s: hook — Canva branded intro.
- 5–17s: mistake 1 — side-by-side examples of complicated layouts; show a clear document.
- 17–29s: mistake 2 — important experience hidden in text boxes; demo visually.
- 29–40s: mistake 3 — generic keywords rather than accurate, job-relevant language.
- 40–45s: Quaddis CTA: "Get a Free CV Audit".
Use the existing seven-scene Canva master as the starting point. No new Firefly or Flow credits are required for this pilot.

## Relevant vendor documentation

- Gemini API billing: https://ai.google.dev/gemini-api/docs/billing/
- Google Flow credits: https://support.google.com/flow/answer/16526234
- Adobe generative credits: https://helpx.adobe.com/creative-cloud/apps/generative-ai/generative-credits-faq.html
- Canva REST API: https://www.canva.dev/docs/apps/rest-apis/reference/
