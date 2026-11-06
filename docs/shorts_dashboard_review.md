# Quaddis Shorts — Desktop Review Mode

This feature was added on branch `fix/shorts-quality-2026-11` / Draft PR #3. It is not a one-prompt cloud video generator. It is a safe one-click **render and review** button for already approved narration + scene assets.

## On your Mac (no new subscription)
1. Open the project folder (`Skp693/YouTube-agy`). Update to the reviewed branch only if you intend to test the unmerged changes.
2. Confirm FFmpeg is installed: `ffmpeg -version`. If needed on macOS with Homebrew, install with `brew install ffmpeg`.
3. Copy `docs/narration_first_manifest.example.json` to `docs/narration_first_manifest.json`.
4. Store the **approved** single English narrator recording and all scene visuals under `local_assets/` (this folder is ignored by Git). Set the manifest's actual file paths. Scene start/end timestamps must cover the entire narration with no gaps, 8–60 seconds total.
5. Use `presenter_native` only where that exact source video is speaking at that exact audio timestamp. For other scenes use silent media `broll` or still-picture presenter `pip_still`. Add captions only from the actual verified words and timestamps.
6. Launch the app: `python3 desktop_server.py 8501` (from repository root; existing project dependencies may need installing).
7. Open `http://127.0.0.1:8501/`. Find **Shorts Review — Approved Media** in the Studio dashboard. Confirm manifest name `narration_first_manifest.json`, press **Create Shorts Review MP4**, and watch progress.
8. On success, the vertical 720 × 1280 preview plays inside the dashboard; download it if the browser viewer has playback issues. Output is saved to `videos/shorts_<id>_final.mp4` on the Mac. The server exposes it locally at `/media/video/shorts_<id>`.
9. Play all scenes and manually verify voice naturalness, audio content, lip-sync of visible presenter, source rights, captions, branding and factual correctness before ever publishing.

## Faster setup: prepare scene timing automatically (new)

You can create a review manifest without editing JSON manually. This works **only with existing narration and visuals**. It does not create or verify a new natural voice, and it does not know which exact words occur at each time.

From the repository root on your Mac, after placing approved clips/portraits in `local_assets/`:

```bash
python3 scripts/prepare_shorts_manifest.py \
  --topic "How ATS Works — 3 Resume Tips" \
  --narration "local_assets/approved_presenter_45s.mp4" \
  --asset "local_assets/resume_layout.png::Keep formatting readable::broll" \
  --asset "local_assets/presenter_portrait.jpg::Match skills truthfully::pip_still" \
  --output "docs/narration_first_manifest.json"
```

**Replace filenames with real approved recordings and graphics** before running. The tool checks that each source exists, uses FFprobe to obtain actual master-audio duration, creates exact contiguous scene boundaries, and adds the same-source presenter only at the beginning/end of a source video. If you provide an external WAV/MP3 narrator instead, no moving talking-head shots are inserted. It NEVER infers spoken text, captions, voice quality or word-aligned timings.

The command intentionally refuses to overwrite a previous manifest. For a different Short choose a new filename in `docs/` and enter that filename in the dashboard. Raw presenter media and prepared manifests are ignored by Git.

If you provide a moving B-roll video, use `--verified-nontalking-video` **only after** visually confirming it contains no visibly speaking faces; otherwise the tool rejects that asset. Recheck the proposed scene cuts against the actual spoken words before pressing Create Shorts Review MP4. For accuracy, create topic-relevant visuals and exact caption cues separately.

## Built-in boundaries
- Accepts only ordinary .json filename in this repo's `docs/` directory — no arbitrary path from the dashboard request, directory traversal, or linked manifest.
- The render endpoint runs only from a localhost browser origin, and refuses concurrent Shorts jobs.
- Uses a random job ID; does not overwrite existing review MP4s.
- Runs the existing narration-first safety, stream, duration and audio continuity checks. Rejects audio missing from the master or scene mismatch.
- Never calls Google Flow, spends generation credits, requests account cookies, invokes YouTube upload, or claims perfect lips or monetization.
- Rendering is limited to the Mac's actual CPU, RAM and available files. A 45s video may take longer than a minute, and a healthy output does not prove editorial quality.

## Common issues
- **422 missing manifest:** Make a copy of the example file and fill real file paths. Do not select an example JSON.
- **Render stopped — missing media:** check the file path and source recording are locally accessible.
- **Talking presenter mismatch:** use the approved original video/audio timecodes, or replace it with a still portrait until an exactly lip-synced shot is available.
- **No natural voice available:** stop the production. Do not insert oscillator tones or copy a voice into unrelated talking-head footage.
- **No preview in browser:** use the MP4 link in dashboard, then open with QuickTime/Files; confirm FFprobe output is H.264/AAC and 720x1280.

## What is NOT yet done
- Automatically generating new Google Flow clips from a single prompt via official APIs/MCP.
- Obtaining and verifying a consented, full-length, realistic voice performance for the 45-second ATS script.
- Transcribing and forced-aligning caption words to actual voice recording with manual verification.
- Automatically building topic-specific original B-roll and confirmed Quaddis brand kit for all tracks.
- Sending a new Short to YouTube, Instagram, Facebook or Postiz.

Do not call the existing long-video generator button the Shorts pipeline. The old and new workflows remain separate until their assets and tests are verified.
