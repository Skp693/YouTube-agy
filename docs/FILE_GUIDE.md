# Tracked-file guide

Source snapshot: [`db87567ac469`](https://github.com/Skp693/YouTube-agy/tree/db87567ac4698e7f229ff4d09ee24c83d8f3a143).

This inventory lists every tracked file in the reviewed default-branch snapshot. It includes inherited scaffolding, generated output, binary assets, and tooling symlinks. Runtime and setup claims were checked separately in the verification record; the inventory is not a line-by-line security audit.

| Path | Type | Purpose |
| --- | --- | --- |
| [`.env.example`](../.env.example) | text | Environment-variable template; replace placeholders locally and keep actual secrets out of Git. |
| [`.gitignore`](../.gitignore) | text | Tracked project file or directory placeholder. |
| [`README.md`](../README.md) | text | Existing package overview and usage guide (root README replaced by this documentation change). |
| [`assemble_video.py`](../assemble_video.py) | text | Source module for assemble video; feature-level responsibilities are explained in the README. |
| [`assets/demo.mp4`](../assets/demo.mp4) | binary | Existing artwork, screenshot, or demonstration media. |
| [`assets/library_screenshot.png`](../assets/library_screenshot.png) | binary | Existing artwork, screenshot, or demonstration media. |
| [`assets/screenshot.png`](../assets/screenshot.png) | binary | Existing artwork, screenshot, or demonstration media. |
| [`audio/.gitkeep`](../audio/.gitkeep) | text | Saved production/demo artifact, timeline, or metadata. |
| [`audio/20261011_144800/full_voiceover.wav`](../audio/20261011_144800/full_voiceover.wav) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`audio/20261011_144800/section_01.wav`](../audio/20261011_144800/section_01.wav) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`audio/20261011_144800/section_02.wav`](../audio/20261011_144800/section_02.wav) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`audio/20261011_144800/section_03.wav`](../audio/20261011_144800/section_03.wav) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`audio/20261011_144800/section_04.wav`](../audio/20261011_144800/section_04.wav) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`audio/20261011_144800/section_05.wav`](../audio/20261011_144800/section_05.wav) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`audio/20261011_144800/section_06.wav`](../audio/20261011_144800/section_06.wav) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`audio/20261011_144800/section_07.wav`](../audio/20261011_144800/section_07.wav) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`audio/20261011_144800/section_08.wav`](../audio/20261011_144800/section_08.wav) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`audio/20261011_144800/section_09.wav`](../audio/20261011_144800/section_09.wav) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`audio/20261011_144800/timing.json`](../audio/20261011_144800/timing.json) | text | Saved production/demo artifact, timeline, or metadata. |
| [`compliance_checker.py`](../compliance_checker.py) | text | Source module for compliance checker; feature-level responsibilities are explained in the README. |
| [`config/.gitkeep`](../config/.gitkeep) | text | Tracked project file or directory placeholder. |
| [`config/logging_config.py`](../config/logging_config.py) | text | Source module for logging config; feature-level responsibilities are explained in the README. |
| [`config/settings.py`](../config/settings.py) | text | Source module for settings; feature-level responsibilities are explained in the README. |
| [`desktop_server.py`](../desktop_server.py) | text | HTTP server and API entry point; see README for routes and runtime behavior. |
| [`images/.gitkeep`](../images/.gitkeep) | text | Saved production/demo artifact, timeline, or metadata. |
| [`images/20261011_144800/scene_01.bmp`](../images/20261011_144800/scene_01.bmp) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`images/20261011_144800/scene_01.png`](../images/20261011_144800/scene_01.png) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`images/20261011_144800/scene_02.bmp`](../images/20261011_144800/scene_02.bmp) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`images/20261011_144800/scene_02.png`](../images/20261011_144800/scene_02.png) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`images/20261011_144800/scene_03.bmp`](../images/20261011_144800/scene_03.bmp) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`images/20261011_144800/scene_03.png`](../images/20261011_144800/scene_03.png) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`images/20261011_144800/scene_04.bmp`](../images/20261011_144800/scene_04.bmp) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`images/20261011_144800/scene_04.png`](../images/20261011_144800/scene_04.png) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`images/20261011_144800/scene_05.bmp`](../images/20261011_144800/scene_05.bmp) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`images/20261011_144800/scene_05.png`](../images/20261011_144800/scene_05.png) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`images/20261011_144800/scene_06.bmp`](../images/20261011_144800/scene_06.bmp) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`images/20261011_144800/scene_06.png`](../images/20261011_144800/scene_06.png) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`images/20261011_144800/scene_07.bmp`](../images/20261011_144800/scene_07.bmp) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`images/20261011_144800/scene_07.png`](../images/20261011_144800/scene_07.png) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`images/20261011_144800/scene_08.bmp`](../images/20261011_144800/scene_08.bmp) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`images/20261011_144800/scene_08.png`](../images/20261011_144800/scene_08.png) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`images/20261011_144800/scene_09.bmp`](../images/20261011_144800/scene_09.bmp) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`images/20261011_144800/scene_09.png`](../images/20261011_144800/scene_09.png) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`images/20261011_144800/scenes_timeline.json`](../images/20261011_144800/scenes_timeline.json) | text | Saved production/demo artifact, timeline, or metadata. |
| [`launch_app.command`](../launch_app.command) | text | Tracked project file or directory placeholder. |
| [`logs/.gitkeep`](../logs/.gitkeep) | text | Existing local operational output; may contain personal information. Contents are not reproduced here. |
| [`main.py`](../main.py) | text | Source module for main; feature-level responsibilities are explained in the README. |
| [`main_pipeline.py`](../main_pipeline.py) | text | Source module for main pipeline; feature-level responsibilities are explained in the README. |
| [`metadata.py`](../metadata.py) | text | Source module for metadata; feature-level responsibilities are explained in the README. |
| [`metadata/.gitkeep`](../metadata/.gitkeep) | text | Saved production/demo artifact, timeline, or metadata. |
| [`metadata/20261011_144800_metadata.json`](../metadata/20261011_144800_metadata.json) | text | Saved production/demo artifact, timeline, or metadata. |
| [`model_advisor.py`](../model_advisor.py) | text | Source module for model advisor; feature-level responsibilities are explained in the README. |
| [`music/.gitkeep`](../music/.gitkeep) | text | Tracked project file or directory placeholder. |
| [`music/ambient_sample.wav`](../music/ambient_sample.wav) | binary | Tracked project file or directory placeholder. |
| [`music/generate_ambient.py`](../music/generate_ambient.py) | text | Source module for generate ambient; feature-level responsibilities are explained in the README. |
| [`requirements.txt`](../requirements.txt) | text | Tracked project file or directory placeholder. |
| [`run_desktop.sh`](../run_desktop.sh) | text | Tracked project file or directory placeholder. |
| [`script_writer.py`](../script_writer.py) | text | Source module for script writer; feature-level responsibilities are explained in the README. |
| [`scripts/.gitkeep`](../scripts/.gitkeep) | text | Tracked project file or directory placeholder. |
| [`scripts/20261011_144800_captions.srt`](../scripts/20261011_144800_captions.srt) | text | Generated narration, captions, or script metadata. |
| [`scripts/20261011_144800_script.json`](../scripts/20261011_144800_script.json) | text | Generated narration, captions, or script metadata. |
| [`scripts/20261011_144800_script.txt`](../scripts/20261011_144800_script.txt) | text | Generated narration, captions, or script metadata. |
| [`src/__init__.py`](../src/__init__.py) | text | Source module for   init  ; feature-level responsibilities are explained in the README. |
| [`src/models.py`](../src/models.py) | text | Source module for models; feature-level responsibilities are explained in the README. |
| [`src/scheduler.py`](../src/scheduler.py) | text | Source module for scheduler; feature-level responsibilities are explained in the README. |
| [`src/stages/__init__.py`](../src/stages/__init__.py) | text | Source module for   init  ; feature-level responsibilities are explained in the README. |
| [`src/stages/base.py`](../src/stages/base.py) | text | Source module for base; feature-level responsibilities are explained in the README. |
| [`src/stages/stage_1_topic.py`](../src/stages/stage_1_topic.py) | text | Source module for stage 1 topic; feature-level responsibilities are explained in the README. |
| [`src/stages/stage_2_script.py`](../src/stages/stage_2_script.py) | text | Source module for stage 2 script; feature-level responsibilities are explained in the README. |
| [`src/stages/stage_3_voiceover.py`](../src/stages/stage_3_voiceover.py) | text | Source module for stage 3 voiceover; feature-level responsibilities are explained in the README. |
| [`src/stages/stage_4_visuals.py`](../src/stages/stage_4_visuals.py) | text | Source module for stage 4 visuals; feature-level responsibilities are explained in the README. |
| [`src/stages/stage_5_assembly.py`](../src/stages/stage_5_assembly.py) | text | Source module for stage 5 assembly; feature-level responsibilities are explained in the README. |
| [`src/stages/stage_6_metadata.py`](../src/stages/stage_6_metadata.py) | text | Source module for stage 6 metadata; feature-level responsibilities are explained in the README. |
| [`src/stages/stage_7_uploader.py`](../src/stages/stage_7_uploader.py) | text | Source module for stage 7 uploader; feature-level responsibilities are explained in the README. |
| [`src/utils/__init__.py`](../src/utils/__init__.py) | text | Source module for   init  ; feature-level responsibilities are explained in the README. |
| [`src/utils/bitmap_font.py`](../src/utils/bitmap_font.py) | text | Source module for bitmap font; feature-level responsibilities are explained in the README. |
| [`src/utils/browser_recorder.py`](../src/utils/browser_recorder.py) | text | Source module for browser recorder; feature-level responsibilities are explained in the README. |
| [`src/utils/file_manager.py`](../src/utils/file_manager.py) | text | Source module for file manager; feature-level responsibilities are explained in the README. |
| [`static/app.js`](../static/app.js) | text | Source module for app; feature-level responsibilities are explained in the README. |
| [`static/index.html`](../static/index.html) | text | Application composition, browser/document entry point, or router entry point. |
| [`static/style.css`](../static/style.css) | text | Stylesheet, vector/image asset, or reference document. |
| [`test_results_20261012/final_script.md`](../test_results_20261012/final_script.md) | text | Generated or historical output; not evidence of a current successful production run. |
| [`test_results_20261012/final_test_video.mp4`](../test_results_20261012/final_test_video.mp4) | binary | Generated or historical output; not evidence of a current successful production run. |
| [`test_results_20261012/issues_and_fixes.md`](../test_results_20261012/issues_and_fixes.md) | text | Generated or historical output; not evidence of a current successful production run. |
| [`test_results_20261012/metadata.json`](../test_results_20261012/metadata.json) | text | Generated or historical output; not evidence of a current successful production run. |
| [`test_results_20261012/pipeline_logs.txt`](../test_results_20261012/pipeline_logs.txt) | text | Generated or historical output; not evidence of a current successful production run. |
| [`test_results_20261012/research_sources.md`](../test_results_20261012/research_sources.md) | text | Generated or historical output; not evidence of a current successful production run. |
| [`test_results_20261012/subtitles.srt`](../test_results_20261012/subtitles.srt) | text | Generated or historical output; not evidence of a current successful production run. |
| [`test_results_20261012/test_report.md`](../test_results_20261012/test_report.md) | text | Generated or historical output; not evidence of a current successful production run. |
| [`test_results_20261012/thumbnail.png`](../test_results_20261012/thumbnail.png) | binary | Generated or historical output; not evidence of a current successful production run. |
| [`tests/test_pipeline_diagnostic.py`](../tests/test_pipeline_diagnostic.py) | text | Existing automated checks for the named module or workflow. |
| [`thumbnails/.gitkeep`](../thumbnails/.gitkeep) | text | Saved production/demo artifact, timeline, or metadata. |
| [`thumbnails/20261011_144800_thumb_A.png`](../thumbnails/20261011_144800_thumb_A.png) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`thumbnails/20261011_144800_thumb_B.png`](../thumbnails/20261011_144800_thumb_B.png) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`thumbnails/20261011_144800_thumb_C.png`](../thumbnails/20261011_144800_thumb_C.png) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`thumbnails/20261011_144800_thumbnail.png`](../thumbnails/20261011_144800_thumbnail.png) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`topic_refiner.py`](../topic_refiner.py) | text | Source module for topic refiner; feature-level responsibilities are explained in the README. |
| [`topic_selector.py`](../topic_selector.py) | text | Source module for topic selector; feature-level responsibilities are explained in the README. |
| [`topics/.gitkeep`](../topics/.gitkeep) | text | Saved production/demo artifact, timeline, or metadata. |
| [`topics/20261011_144800_topic.json`](../topics/20261011_144800_topic.json) | text | Saved production/demo artifact, timeline, or metadata. |
| [`videos/.gitkeep`](../videos/.gitkeep) | text | Saved production/demo artifact, timeline, or metadata. |
| [`videos/20261011_144800_concat.txt`](../videos/20261011_144800_concat.txt) | text | Saved production/demo artifact, timeline, or metadata. |
| [`videos/20261011_144800_final.mp4`](../videos/20261011_144800_final.mp4) | binary | Saved production/demo artifact, timeline, or metadata. |
| [`videos/20261011_144800_render.sh`](../videos/20261011_144800_render.sh) | text | Saved production/demo artifact, timeline, or metadata. |
| [`visuals.py`](../visuals.py) | text | Source module for visuals; feature-level responsibilities are explained in the README. |
| [`voiceover.py`](../voiceover.py) | text | Source module for voiceover; feature-level responsibilities are explained in the README. |
| [`youtube_uploader.py`](../youtube_uploader.py) | text | Source module for youtube uploader; feature-level responsibilities are explained in the README. |

New documentation files and media added by this change are described in `VERIFICATION.md`; they are not counted in the original source inventory.
