# Free, commercial-license candidate narration — Quaddis Shorts

**Status: source and local integration tested; real Kokoro generation on the user's Mac still pending.** This does **not** claim that the final monetizable Short is ready.

## Reason for switching

The previously narrated 47.75s ATS review contains **HeyGen Free-plan** voice output. HeyGen's [Terms](https://www.heygen.com/terms) restrict Free-plan user output to personal, non-commercial and internal evaluation; it may **not** be monetized. Do not publish that review video as an ad or monetized YouTube Short.

A local candidate is [hexgrad/Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) (model weights licensed Apache-2.0) using [thewh1teagle/kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx) (runtime MIT license). Check the actual downloaded model and voice-pack license and provenance. This is not a voice clone and does not require a paid SaaS API or additional recurring subscription. Local ONNX generation is intended to run on Mac M1 8GB with Python 3.10–3.13; the model must be downloaded first (~326 MB FP32 + ~28 MB voices).

## Prepared private handoff

A **new separate downloadable ZIP** is supplied in the user conversation: `Quaddis_ATS_Zero_Cost_Commercial_Voice_Starter.zip` (about 1.3 MB, 20 files). It contains:
- 8 original ATS motion-graphic MP4 clips; all local, not pushed here.
- `local_commercial_voice.py`: produces one female synthetic narrator (default `af_sarah`) in 15 exact script phrases, dynamic **phrase** captions from generated segment lengths, eight exact scene boundaries, 720×1280 H.264/AAC review with the previous overlay text removed. Never uses HeyGen MP3.
- `setup_kokoro_mac.sh`: creates venv; installs `kokoro-onnx==0.6.1`; downloads official model files from upstream; creates new review-only audio + video. It does **not** publish.
- `SETUP_KOKORO_MAC.md`, `README_MALAYALAM_KOKORO.txt`, `BRAND_VERIFICATION.md`, private scene pack and unit tests.
- Private installer `install_into_youtube_agy.py` changed to copy **visual assets only** and intentionally NOT copy the non-commercial HeyGen audio into the repo.

**One command after extracting ZIP on Mac** (install FFmpeg/Python 3.12 once if missing):

```bash
bash setup_kokoro_mac.sh
```

The generated candidate video will be placed in `local_assets/commercial_voice_candidate/quaddis_ats_kokoro_review.mp4`. This is **not** a finished full talking-avatar video. The presenter remains a static, consented PIP photo until real lipsync video for the exact narrator voice is available. The 15 captions are timed to newly generated phrase durations, not word-level forced alignment. Sentence-by-sentence synthesis may sound less natural than a continuous narration; listen before approving.

## What was verified in this session

- Reused source images and motion scenes to produce `quaddis_ats_brand_corrected_internal_review.mp4` (47.752s, 720×1280 H.264/AAC). It still includes the HeyGen Free audio and remains internal review only.
- Measured audio activity-envelope correlation 0.99939 to the original voice, and FFmpeg decoded the entire video without errors.
- The incorrect artificial Q-logo symbol in the previous preview was masked and replaced with plain editorial text. Dynamic captions are in the lower safe zone; old provider overlays masked.
- 14 local unit tests passed (8 existing bundle checks + 6 new voice generator checks). A true 11.4-second **test-fixture** FFmpeg render verified the voice-relative scene assembly path. No actual Kokoro model or human-sounding Kokoro audio could be downloaded/rendered in this ChatGPT container. Do not misrepresent this as a full end-to-end Mac test.
- Brand guide inspected in existing Canva design `DAHYGeeg96I`, **Quaddis Brand Guidelines v2.0**. The original preview's improvised Q icon is **not** the approved master logo. Guide's sampled provisional colors: `#F34B89` pink; `#112347` navy; exact vector master swatches and SVG/transparent brand mark still needed.

## Publication blockers

1. Run the ZIP's Kokoro script on the user's Mac with the official model files. Review the new recording's English accent, continuity, phrasing, and narration speed. Do not use the HeyGen Free MP3 commercially.
2. Review newly synthesized timed captions (and adjust exact wording), verify the brand logo master and Free CV Audit destination URL.
3. Realistic lip-synced on-camera avatar remains unavailable for the new voice; this solution deliberately uses a still PIP rather than faking lip movements. An approved real presenter shot or legitimate lip-sync render is needed for a speaking head.
4. Confirm rights to any voice, clips, brand assets and image likeness, and check current YouTube altered/synthetic content disclosure rules. No automatic upload and no guaranteed YouTube monetization.
5. The Docker/Antigravity/Google Flow MCP and fully autonomous one-prompt generation are NOT connected by this ZIP.

**No private voice, personal image, credential or model weights were committed to GitHub.** Keep Draft PR #3 unmerged until approved.
