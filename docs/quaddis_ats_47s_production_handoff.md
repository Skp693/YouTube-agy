# Quaddis ATS Short — 47.75-second production asset handoff (2026-11-06)

**Status: PRIVATE REVIEW ASSETS READY, not monetization-ready and not published.**

A separate downloadable private production ZIP has been provided in the conversation. It includes eight original topic-specific motion-graphics scene MP4s, 720x1280 iPhone-compatible **silent-preview** H.264/AAC MP4, source narration script, provider-timed captions and SRT, scene-timing JSON, reference portrait (provided with consent), original Python renderer, audio mux script, an installer for this existing repository, a sample review manifest, social content drafts and tests.

**The private ZIP / photo / audio-host URL have intentionally NOT been pushed to this public GitHub repository.** The user may download the ZIP in their conversation and place it on their own Mac.

## What has actually been generated
- HeyGen voice *Joanna — Warm & Conversational*, 47.7518-second narration recording, separate playable provider resource. The exact audio bytes were **not** downloaded into the rendering environment, so do not call the silent preview a finished voiceover video.
- Eight original animation sequences with captions timed to provider word timestamps; non-speaking, static presenter picture-in-picture in relevant scenes. No talking-face lip sync was generated or claimed.
- A private local installer `install_into_youtube_agy.py` copies clips into `local_assets/quaddis_ats_47s/scenes/` and creates ignored `docs/quaddis_ats_prepared_manifest.json`. The 47.75s master narration must also exist locally for final MP4 assembly; failed/missing narration is a blocker.
- 8/8 local ZIP package tests passed including missing audio, silence, oscillator detection, exact scene boundaries and safe local installation. These tests are local to the private pack, not yet part of this repo's 49-test CI suite.
- Final integration should run through `scripts/narration_first_shorts.py` or the included local `finalize_short.py` for a **review-only** MP4, after a legally usable narration file has been provided.

## IMPORTANT HeyGen license limitation
The connected HeyGen account reported **Free** plan. According to https://www.heygen.com/terms (Free-plan User Output license), that Free output is **personal, non-commercial/internal evaluation only**; it cannot be monetized, advertised, used for client work or revenue-generating projects. Hence the generated Joanna voice is **for private workflow evaluation ONLY**. Do not use it for monetized YouTube content.

For commercial publishing without new software subscriptions, obtain a consented original human narration or a separate speech engine/voice model with verifiable commercial-use rights. When the narrator changes, **regenerate/realign the captions and edit scene boundaries against the new actual recording**. A voice file of approximately equal duration does not make transcript/lip-sync accurate.

## Factual claims
ATS products can parse resumes and may have trouble with complex formatting, but no universal "ATS rejection score" exists across all systems.
- https://support.greenhouse.io/hc/en-us/articles/200989175-Unsuccessful-resume-parse
- https://help.lever.co/s/article/Understanding-Resume-Parsing

## Before marking production ready
- Import a lawfully usable narration master and review its naturalness and words.
- Validate/realign captions to THAT exact recording.
- Replace provisional Quaddis text mark with verified official brand logo, CTA website/link.
- Review actual presenter lip-sync if a moving, speaking face is required (this pack intentionally uses a still portrait to avoid false mouth sync).
- Verify 1080x1920 output, licenses, AI-generated content disclosures and factual claims.
- Run code/FFmpeg tests on the user's Mac; only then consider publishing after explicit review.

**No Google Flow MCP cookie scraping, extra Google Flow credits, paid generation purchases, or YouTube publication occurred.** Keep Draft PR #3 open until reviewed.
