# QUADDIS — How ATS Works (45-second production pack)

**Stage:** Proposed English script + scene design. NOT recorded, rendered, approved, or published. No new paid credits used.

**Production specification:** 9:16, 1080 × 1920 master, 30fps, estimated 45s at ~150 WPM; same consented presenter, one natural narration source and one Quaddis brand kit. Save master voice, transcript and images outside public Git.

## Narration script (~112 words / ~45s at 150 WPM)

> Ever wondered why a good résumé gets ignored? Applicant tracking systems, or ATS tools, help employers collect and search applications. They may extract details like your experience, skills, and job titles. Here’s how to make your résumé easier to read. First, use clear headings like Work Experience, Education, and Skills. Second, match the job description truthfully. Use the terms that describe skills you actually have. Third, keep the layout simple; complicated columns and text boxes can sometimes confuse parsing. Remember, an ATS isn’t one universal robot that automatically rejects everyone. Recruiters still make decisions. Want a second pair of eyes? Quaddis can help you review your résumé. Request a free CV audit.

**Editorial caution:** Different ATS products behave differently. No universal ATS score or guaranteed keyword-based rejection. Check current claims against vendor documentation, and don't promise a job or screening result.

## Approximate scene plan — NOT approved exact timestamps

| Estimate | Camera / motion | On-screen text | Audio |
|---|---|---|---|
| 00–07 | Presenter on camera, natural gestures. Only native synced footage from the exact master speech. | Why good resumes get missed | Single approved narration |
| 07–15 | Original animated job application inbox / resume PDF parsing illustration. Do NOT imply proprietary ATS screenshots are real. | ATS helps organize applications | Same master narration |
| 15–23 | Presenter reference portrait in PIP (still) beside animated resume headings, no moving mouth. | Work Experience / Education / Skills | Same master narration |
| 23–31 | Animated job description highlighting verified skills. | Match skills truthfully | Same master narration |
| 31–39 | Simple side-by-side one-column layout vs complex text-box layout; avoid universal bans. | Keep formatting readable | Same master narration |
| 39–45 | Consent-approved presenter synchronized to the exact audio if available; otherwise brand CTA motion graphic. | Get a Free CV Audit | Same master narration |

**Beats are estimates.** After recording, time each sentence from actual words. Align scene boundaries to audio; never force 45s into independently spoken 8s clips.

## Google Flow prompts (only if using available credits and proper rights)

**Global reusable character reference:** Use the consent-approved Quaddis presenter portrait or saved Flow character. Keep her face, skin tone, hair, coral patterned headscarf, clothing, studio lights and framing consistent. Only use specific lip movements that are independently verified to the exact narration; don't invent different spoken words across scenes.

**Scene 2:** "Vertical 9:16 premium educational motion-graphics animation: anonymous resume PDF enters a modern recruitment inbox, fields like Work Experience, Education, Skills are extracted and displayed clearly. Tasteful camera moves, minimal dark studio palette, no real company product UI, no people speaking, no text hallucinations; leave clear negative space for verified captions."

**Scene 3:** "Vertical 9:16 original graphic: clean simple single-column resume with legible headings, sequential highlight of Work Experience, Education, Skills. Small static presenter portrait in PIP overlay composited later; do not render a synthetic speaking face. Natural clean motion and spacious areas for subtitles."

**Scene 4:** "Vertical 9:16 motion explainer: a generic job description on the left, truthful matching skill terms on the right; subtle highlighted keywords, no automated-rejection or guaranteed-score claim, no talking faces."

**Scene 5:** "Vertical 9:16 side-by-side educational visual: simple readable resume structure vs very dense layout with overlapping text boxes. Show that readability can be affected; do not falsely claim all ATS products reject columns."

**Scene 6:** "Vertical 9:16 Quaddis branded end frame, single clean CTA: Get a Free CV Audit. Simple elegant transitions. Logo and accurate website address should be supplied as verified original assets. Do not invent URLs."

## Antigravity single prompt (safe review run, not silent Google Flow login)

"Use my existing Skp693/YouTube-agy project and this production pack. Use one approved ~45s natural English narration that speaks the exact script, then calculate actual timing from the narration. Render 1080×1920 original motion graphics, clean Quaddis CTA, a consented presenter only where speech is truly synchronized, PIP still portrait where useful, and verified timed captions. Use exported Google Flow clips if I provide them; otherwise local FFmpeg original motion graphics are acceptable. Never synthesize a fake robotic voice, invent a transcript, claim ATS has universal rejection scoring, use hidden browser sessions, spend credits or publish. Run audio-preflight, master-audio continuity, frame/codec QA and all regression tests. Export review-only MP4 and ask for my approval. If natural narration/verified brand assets are unavailable, stop with a clear blocker report rather than fabricating completion."

## Required input before a true final Short

1. One **approved** 45s narration recording or authorized realistic speech result and its exact text.
2. One confirmed presenter source clip with lip sync to that recording (if talking on camera is essential) or still portrait PIP.
3. Approved Quaddis primary logo and official URL/CTA destination (never infer from sample media).
4. Fact-check the script and confirm permission to reuse external videos, fonts, music, and images.
5. Run: `python3 scripts/narration_first_shorts.py docs/narration_first_manifest.json --output videos/quaddis_ats_review.mp4 --width 1080`. No automated publishing.

**No new subscription required for assembly** (FFmpeg + Python), but Google Flow generation and realistic avatar synthesis can be limited by credits and supported interfaces. This document is a production-ready *plan*, not a finished natural-voice video.
