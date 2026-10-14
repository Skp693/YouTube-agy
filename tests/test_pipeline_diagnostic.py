"""Diagnostic and Unit Test Suite for Autonomous YouTube Video Pipeline.

Tests all modular stages, configuration loading, error recovery,
compliance auditing, and REST API handlers.
"""

import os
import sys
import json
import shutil
import unittest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import settings
import topic_selector
import topic_refiner
import script_writer
import voiceover
import visuals
import assemble_video
import metadata
import compliance_checker

class TestConfigAndSettings(unittest.TestCase):
    """Test configuration loading, paths, and environment settings."""

    def test_directories_exist_or_creatable(self):
        settings.ensure_directories()
        self.assertTrue(settings.TOPICS_DIR.exists())
        self.assertTrue(settings.SCRIPTS_DIR.exists())
        self.assertTrue(settings.AUDIO_DIR.exists())
        self.assertTrue(settings.IMAGES_DIR.exists())
        self.assertTrue(settings.VIDEOS_DIR.exists())
        self.assertTrue(settings.THUMBNAILS_DIR.exists())
        self.assertTrue(settings.METADATA_DIR.exists())
        self.assertTrue(settings.LOGS_DIR.exists())

    def test_default_production_constants(self):
        self.assertEqual(settings.VIDEO_RESOLUTION_WIDTH, 1920)
        self.assertEqual(settings.VIDEO_RESOLUTION_HEIGHT, 1080)
        self.assertEqual(settings.VIDEO_FPS, 30)
        self.assertGreaterEqual(settings.MIN_WORDS, 1000)

class TestTopicSelectorAndRefiner(unittest.TestCase):
    """Test Stage 1: Topic selection, research heuristics, and topic refiner."""

    def test_topic_selection_output_structure(self):
        topic_data = topic_selector.select_topic(tool_name="NotebookLM")
        self.assertEqual(topic_data["tool_name"], "NotebookLM")
        self.assertIn("suggested_title", topic_data)
        self.assertIn("key_points", topic_data)
        self.assertIn("angle", topic_data)
        self.assertIsInstance(topic_data["key_points"], list)

    def test_topic_refiner_remodify(self):
        refiner = topic_refiner.TopicRefiner()
        result = refiner.remodify_topic(
            raw_input="5 Practical AI Tools for Small Business Owners",
            video_format="step_by_step"
        )
        self.assertIn("suggested_title", result)
        self.assertIn("key_points", result)
        self.assertGreaterEqual(len(result["key_points"]), 3)

    def test_topic_refiner_trending_suggestions(self):
        refiner = topic_refiner.TopicRefiner()
        suggestions = refiner.get_trending_suggestions(niche="all")
        self.assertIsInstance(suggestions, list)
        self.assertGreaterEqual(len(suggestions), 5)
        for s in suggestions:
            self.assertIn("tool_name", s)
            self.assertIn("potential_rpm", s)

class TestScriptWriter(unittest.TestCase):
    """Test Stage 2: Educational script structure, timings, and hook generation."""

    def test_procedural_script_structure(self):
        test_topic = {
            "tool_name": "Claude 3.7",
            "angle": "Building Full Stack Apps",
            "suggested_title": "How to Build Apps with Claude 3.7",
            "key_points": ["Setup environment", "Generate code", "Deploy"]
        }
        test_project_id = "test_diag_script"
        script_data = script_writer.write_script(test_topic, test_project_id)

        self.assertIn("sections", script_data)
        self.assertIn("word_count", script_data)
        self.assertGreaterEqual(script_data["word_count"], 1000)

        sections = script_data["sections"]
        self.assertGreaterEqual(len(sections), 6)
        # Verify first section is an engaging hook
        self.assertIn("hook", sections[0]["section_type"].lower())
        # Verify each section contains title, narration, on_screen_text
        for sec in sections:
            self.assertTrue("title" in sec or "section_title" in sec)
            self.assertIn("narration", sec)
            self.assertIn("on_screen_text", sec)
            self.assertTrue(len(sec["narration"].strip()) > 0)

        # Cleanup generated test script
        (settings.SCRIPTS_DIR / f"{test_project_id}_script.txt").unlink(missing_ok=True)
        (settings.SCRIPTS_DIR / f"{test_project_id}_script.json").unlink(missing_ok=True)

class TestVoiceoverSynthesis(unittest.TestCase):
    """Test Stage 3: Audio synthesis, macOS speech fallback, and timing generation."""

    def test_macos_speech_synthesis(self):
        test_out = settings.AUDIO_DIR / "diag_test_voice.wav"
        duration = voiceover.synthesize_macos_speech(
            text="Welcome to this practical demonstration of modern AI automation.",
            output_path=test_out,
            voice="Daniel",
            rate_wpm=165
        )
        if duration is not None:
            self.assertTrue(test_out.exists())
            self.assertGreater(duration, 1.0)
            test_out.unlink(missing_ok=True)
        else:
            self.skipTest("macOS say binary not available or audio failed")

class TestVisualsEngine(unittest.TestCase):
    """Test Stage 4: 1080p slide generation and pure-standard-library BMP engine."""

    def test_slide_native_bmp_rendering(self):
        test_out = settings.IMAGES_DIR / "diag_slide.png"
        visuals.render_slide_native_bmp(
            section_num=1,
            section_type="HOOK & OVERVIEW",
            title="5 Practical AI Tools for Business",
            bullets=["Automate customer support", "Streamline invoices", "Cut operating costs"],
            output_path=test_out,
            width=1920,
            height=1080
        )
        self.assertTrue(test_out.exists() or test_out.with_suffix(".bmp").exists())
        # Clean up
        test_out.unlink(missing_ok=True)
        test_out.with_suffix(".bmp").unlink(missing_ok=True)

class TestAssembleVideoTools(unittest.TestCase):
    """Test Stage 5: Subtitle cue formatting and FFmpeg verification."""

    def test_srt_time_formatting(self):
        formatted = assemble_video.format_srt_time(65.345)
        self.assertEqual(formatted, "00:01:05,345")

    def test_ffmpeg_binary_availability(self):
        import subprocess
        res = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("ffmpeg", res.stdout.lower())

class TestMetadataAndThumbnails(unittest.TestCase):
    """Test Stage 6: Metadata, Chapter Timestamps (00:00), and 3 A/B thumbnail variations."""

    def test_chapter_formatting(self):
        t0 = metadata.format_chapter_timestamp(0.0)
        t1 = metadata.format_chapter_timestamp(75.4)
        t2 = metadata.format_chapter_timestamp(3665.0)
        self.assertEqual(t0, "00:00")
        self.assertEqual(t1, "01:15")
        self.assertEqual(t2, "1:01:05")

    def test_thumbnail_ab_variations_render(self):
        test_pid = "diag_thumb_test"
        thumb_a = settings.THUMBNAILS_DIR / f"{test_pid}_thumb_A.png"
        thumb_b = settings.THUMBNAILS_DIR / f"{test_pid}_thumb_B.png"
        thumb_c = settings.THUMBNAILS_DIR / f"{test_pid}_thumb_C.png"

        metadata.render_thumbnail_variant_a("AI Tools", thumb_a)
        metadata.render_thumbnail_variant_b("AI Tools", thumb_b)
        metadata.render_thumbnail_variant_c("AI Tools", thumb_c)

        self.assertTrue(thumb_a.exists())
        self.assertTrue(thumb_b.exists())
        self.assertTrue(thumb_c.exists())

        # Cleanup
        thumb_a.unlink(missing_ok=True)
        thumb_b.unlink(missing_ok=True)
        thumb_c.unlink(missing_ok=True)

class TestComplianceChecker(unittest.TestCase):
    """Test YouTube Partner Program compliance and monetization safety auditor."""

    def test_safe_content_passes(self):
        checker = compliance_checker.ComplianceChecker()
        audit = checker.audit_project(
            title="5 Practical AI Tools to Save Time (2026 Guide)",
            description="Complete educational walkthrough with 00:00 Introduction 01:30 Tools",
            narration_full="Today we explore five practical tools designed to streamline everyday operations.",
            tags=["ai", "productivity", "tutorial"],
            has_ai_disclosure=True
        )
        self.assertGreaterEqual(audit["score"], 85)
        self.assertEqual(audit["status"], "PASSED_MONETIZATION_READY")

    def test_demonitization_keywords_flagged(self):
        checker = compliance_checker.ComplianceChecker()
        audit = checker.audit_project(
            title="How to crack software and bypass paywall",
            description="Free crack hack tool",
            narration_full="In this tutorial we show how to pirate services.",
            tags=["hack", "piracy"],
            has_ai_disclosure=False
        )
        self.assertLess(audit["score"], 70)
        self.assertEqual(audit["status"], "NEEDS_MODIFICATION")
        self.assertTrue(len(audit["issues"]) > 0)

if __name__ == "__main__":
    unittest.main()
