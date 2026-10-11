"""Topic Refiner & Multimodal Input Expander (topic_refiner.py)

Handles user input in any format (text, reference notes, image descriptions, or video links),
provides instant AI remodification into high-CTR video blueprints, and serves curated
trending topic suggestions across high-revenue AI niches.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

TRENDING_NICHES = {
    "coding": [
        {
            "tool_name": "Claude 3.7 & Artifacts",
            "angle": "Full Interactive React Prototyping with Extended Thinking",
            "suggested_title": "How to Build Full Apps with Claude 3.7 Artifacts (2026 Masterclass)",
            "niche": "AI Coding & Prototyping",
            "potential_rpm": "$14 - $28",
            "key_points": [
                "Dual-pane interactive React and Tailwind sandbox execution",
                "Using Claude Projects with 200k tokens of design system knowledge",
                "Prompting with Hybrid Reasoning (Extended Thinking toggle)",
                "Exporting directly to GitHub, Vite, and Vercel"
            ],
            "reason": "Top trending developer workflow with massive creator audience retention."
        },
        {
            "tool_name": "Cursor AI & Composer",
            "angle": "Full Codebase Indexing & Multi-File Agent Automation",
            "suggested_title": "How to Code 10x Faster with Cursor AI (Beginner to Pro 2026)",
            "niche": "AI Coding & Prototyping",
            "potential_rpm": "$16 - $32",
            "key_points": [
                "Setting up local vector codebase indexing with .cursorrules",
                "Composer multi-file autonomous editing workflows",
                "Inline terminal command execution and instant error repair",
                "Privacy modes and enterprise security setup"
            ],
            "reason": "Extremely high search demand among engineers and founders."
        },
        {
            "tool_name": "Bolt.new vs Lovable.dev",
            "angle": "Head-to-Head Comparison: The Best Browser App Builder",
            "suggested_title": "Bolt.new vs Lovable: Which Builds Better Full-Stack Apps in 2026?",
            "niche": "AI Coding & Prototyping",
            "potential_rpm": "$15 - $30",
            "key_points": [
                "WebContainers in-browser execution vs cloud deployment",
                "Database integration speed: Supabase vs Firebase",
                "Pricing, exportability, and code ownership",
                "Final verdict for indie hackers and solo founders"
            ],
            "reason": "High-CTR comparison format driving strong viewer engagement."
        }
    ],
    "productivity": [
        {
            "tool_name": "Google NotebookLM",
            "angle": "Turn 50+ Source Documents into Podcasts & Grounded Study Guides",
            "suggested_title": "Google NotebookLM: The Ultimate AI Research Assistant (2026 Guide)",
            "niche": "AI Productivity & Knowledge",
            "potential_rpm": "$10 - $22",
            "key_points": [
                "Uploading PDFs, Google Docs, and YouTube URLs into notebooks",
                "Generating conversational Audio Overviews for passive learning",
                "Strict source citation grounding to eliminate hallucinations",
                "Best practices for legal, medical, and technical research"
            ],
            "reason": "Viral appeal across students, researchers, and knowledge workers."
        },
        {
            "tool_name": "Perplexity AI Deep Research",
            "angle": "Replacing Google with Agentic Multi-Step Web Research",
            "suggested_title": "How to Use Perplexity AI for Deep Research (Complete 2026 Guide)",
            "niche": "AI Productivity & Knowledge",
            "potential_rpm": "$12 - $25",
            "key_points": [
                "Focus modes: Academic, Writing, and Wolfram Alpha computational math",
                "Creating collaborative Collections for client projects",
                "Prompt templates for exhaustive multi-source research dossiers",
                "Exporting clean reports to Markdown and Notion"
            ],
            "reason": "Major search migration happening from traditional search engines to Perplexity."
        }
    ],
    "creative": [
        {
            "tool_name": "Midjourney v7 & Flux.1",
            "angle": "Photorealistic AI Imagery & Consistent Character Styling",
            "suggested_title": "Midjourney v7 Masterclass: How to Prompt Photorealistic Images",
            "niche": "AI Media & Design",
            "potential_rpm": "$8 - $18",
            "key_points": [
                "New parameter controls for camera optics, lighting, and textures",
                "Maintaining 100% character and facial consistency across scenes",
                "Commercial upscaling and vector trace workflows",
                "Selling digital stock assets and client branding kits"
            ],
            "reason": "Massive visual interest and click-through appeal on YouTube."
        },
        {
            "tool_name": "ElevenLabs Voice Agents",
            "angle": "Building Automated Conversational AI Calling Systems",
            "suggested_title": "Build Your First AI Voice Agent in 15 Minutes with ElevenLabs",
            "niche": "AI Media & Design",
            "potential_rpm": "$18 - $35",
            "key_points": [
                "Voice cloning ethics and low-latency websocket streaming",
                "Configuring dynamic conversational knowledge bases",
                "Connecting Twilio and webhook integrations for business calls",
                "Monetizing as an AI agency offering customer support bots"
            ],
            "reason": "High agency B2B monetization intent drives premium RPM ad rates."
        }
    ]
}

class TopicRefiner:
    """Refines arbitrary multimodal user inputs into high-retention video blueprints."""

    @classmethod
    def remodify_topic(
        cls,
        raw_input: str,
        video_format: str = "step_by_step",
        target_audience: str = "creators_and_developers",
        reference_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Takes raw user input or reference notes and structures it into a high-CTR concept."""
        clean_input = raw_input.strip() if raw_input else "AI Workflow Automation"
        
        # Clean title construction based on format
        format_prefixes = {
            "step_by_step": f"How to Use {clean_input} (Step-by-Step 2026 Masterclass)",
            "comparison": f"{clean_input}: Which Tool Actually Wins in 2026?",
            "crash_course": f"{clean_input} Full Course: Zero to Pro in 10 Minutes",
            "monetization": f"How to Monetize {clean_input}: 3 Real-World Income Blueprints",
            "deep_dive": f"{clean_input} Deep Dive: Everything You Need to Know (2026 Guide)"
        }

        suggested_title = format_prefixes.get(
            video_format,
            f"How to Master {clean_input} (Complete 2026 Guide)"
        )

        if len(suggested_title) > 68:
            suggested_title = f"{clean_input} Full Tutorial (2026 Guide)"

        # Combine any reference notes provided
        context_summary = f"Refined concept for {clean_input}"
        if reference_notes:
            context_summary += f" incorporating reference data: {reference_notes[:100]}..."

        return {
            "tool_name": clean_input,
            "video_format": video_format,
            "target_audience": target_audience,
            "suggested_title": suggested_title,
            "angle": f"Practical, high-utility masterclass focusing on hands-on workflow and real-world results",
            "value_proposition": f"Learn how to set up, prompt, automate, and monetize {clean_input} with zero friction.",
            "key_points": [
                f"Core overview and setup for {clean_input}",
                "Step-by-step hands-on workflow and prompt breakdown",
                "Power-user shortcuts, automation tricks, and mistake avoidance",
                "Commercial monetization and client deliverable strategies"
            ],
            "seo_keywords": [
                clean_input,
                f"{clean_input} tutorial",
                f"how to use {clean_input}",
                f"{clean_input} 2026",
                "ai tools tutorial",
                "step by step guide",
                "tech workflow"
            ],
            "context_summary": context_summary,
            "timestamp": datetime.now().isoformat()
        }

    @classmethod
    def get_trending_suggestions(cls, niche: str = "all") -> List[Dict[str, Any]]:
        """Returns trending AI topics filtered by niche or all niches."""
        if niche in TRENDING_NICHES:
            return TRENDING_NICHES[niche]

        # Combine all niches
        combined = []
        for n_list in TRENDING_NICHES.values():
            combined.extend(n_list)
        return combined
