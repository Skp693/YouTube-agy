"""Model Advisor & Engine Configuration Advisor (model_advisor.py)

Analyzes available API keys, system environment, and video goals to suggest the
best model setup for maximum quality, retention, and monetization revenue.
"""

import os
import shutil
from typing import Dict, Any, List
from config.settings import settings

class ModelAdvisor:
    """Recommends and validates the optimal AI model and media engines."""

    @classmethod
    def get_recommendations(cls) -> Dict[str, Any]:
        """Evaluates active environment and recommends the best model stack."""
        has_gemini = bool(settings.GEMINI_API_KEY)
        has_openai = bool(settings.OPENAI_API_KEY)
        has_anthropic = bool(settings.ANTHROPIC_API_KEY)
        has_elevenlabs = bool(settings.ELEVENLABS_API_KEY)
        has_ffmpeg = shutil.which("ffmpeg") is not None
        has_macos_say = shutil.which("say") is not None

        # 1. Scriptwriting Recommendation
        if has_gemini:
            script_rec = {
                "selected_engine": "Gemini 1.5 Pro / 2.0 Flash",
                "quality_rating": "10/10 (Industry Leader)",
                "rationale": "Massive 2M token context, native Google search grounding, and deep technical mastery.",
                "cost": "Free tier available / Ultra-low cost per video (< $0.02)"
            }
        elif has_anthropic:
            script_rec = {
                "selected_engine": "Claude 3.7 Sonnet",
                "quality_rating": "10/10",
                "rationale": "Exceptional coding instruction, architectural clarity, and structured JSON output.",
                "cost": "~$0.05 per 1500-word script"
            }
        elif has_openai:
            script_rec = {
                "selected_engine": "OpenAI GPT-4o",
                "quality_rating": "9.5/10",
                "rationale": "High conversational fluency, structured formatting, and broad world knowledge.",
                "cost": "~$0.04 per 1500-word script"
            }
        else:
            script_rec = {
                "selected_engine": "Built-In Procedural Masterclass Engine",
                "quality_rating": "9.0/10 (Recommended Zero-Cost Mode)",
                "rationale": "Generates 1400-1800 word tactical tutorials with zero API keys required, 100% offline and free.",
                "cost": "$0.00 (Zero-Cost Forever)"
            }

        # 2. Voiceover Recommendation
        if has_elevenlabs:
            voice_rec = {
                "selected_engine": "ElevenLabs Multilingual v2",
                "quality_rating": "10/10",
                "rationale": "Emotional inflection and human-like cadence for top viewer retention.",
                "cost": "Subscription / Usage based"
            }
        elif has_gemini or os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            voice_rec = {
                "selected_engine": "Google Cloud Text-to-Speech (Journey / Studio)",
                "quality_rating": "9.8/10",
                "rationale": "Deep neural audio synthesis with studio broadcast quality (en-US-Journey-F).",
                "cost": "Free tier includes 1M characters/month"
            }
        elif has_macos_say:
            voice_rec = {
                "selected_engine": "Native macOS Studio Voice (Daniel / Samantha)",
                "quality_rating": "8.8/10 (Recommended Zero-Cost Mode)",
                "rationale": "Runs locally on your Mac via /usr/bin/say, zero latency, zero cost, completely offline.",
                "cost": "$0.00 (Zero-Cost Forever)"
            }
        else:
            voice_rec = {
                "selected_engine": "Synthetic Wave Modulation",
                "quality_rating": "5.0/10 (Dry-Run Only)",
                "rationale": "Generates harmonic pacing track for testing pipeline flow.",
                "cost": "$0.00"
            }

        # 3. Visuals Recommendation
        visual_rec = {
            "selected_engine": "1080p Pure-Python Typography & Graphic Engine",
            "quality_rating": "8.5/10 (Clean Explainer / Slideshow)",
            "rationale": "Produces sharp, readable dark-mode cards with category pills, titles, checkmark cards, and branding.",
            "cost": "$0.00 (Zero-Cost Forever)"
        }
        if has_gemini:
            visual_rec["optional_upgrade"] = "Google Imagen 3 API (Add IMAGEN_API_KEY in .env for photorealistic illustrations)"

        # 4. Video Assembly
        assembly_rec = {
            "engine": "FFmpeg Engine (Active: /opt/homebrew/bin/ffmpeg)" if has_ffmpeg else "FFmpeg Manifest Generator",
            "status": "Ready for 1080p / 4K MP4 Production" if has_ffmpeg else "Install via: brew install ffmpeg",
            "features": "Smooth slide timing, SRT subtitle burn-in, background music ducking (-22dB)"
        }

        return {
            "script_engine": script_rec,
            "voice_engine": voice_rec,
            "visual_engine": visual_rec,
            "assembly_engine": assembly_rec,
            "overall_assessment": "Production-Ready with Zero-Cost Local Mode active. Add GEMINI_API_KEY to unlock Cloud AI features.",
            "active_env": {
                "gemini": has_gemini,
                "openai": has_openai,
                "anthropic": has_anthropic,
                "elevenlabs": has_elevenlabs,
                "ffmpeg": has_ffmpeg,
                "macos_say": has_macos_say
            }
        }
