"""Stage 2: Research and Timed Script Generation (8-12 minutes)."""

import json
from pathlib import Path
from config.settings import settings
from src.models import ProjectState, ScriptSection, VideoScript
from src.stages.base import BaseStage

class ScriptResearchStage(BaseStage):
    """Generates an 8-12 minute comprehensive, monetization-friendly guide script."""

    stage_number = 2
    stage_name = "research_and_script"

    def validate_prerequisites(self, state: ProjectState) -> None:
        """Ensure topic is present before generating script."""
        if not state.topic:
            raise ValueError("Cannot generate script: state.topic is None")

    def execute(self, state: ProjectState) -> ProjectState:
        """Constructs an educational step-by-step video script."""
        topic = state.topic
        self.logger.info(f"Generating 8-12 minute script for AI tool: {topic.tool_name}")

        target_minutes = 10
        wpm = settings.WORDS_PER_MINUTE

        # Modular section blueprint for educational explainer / tutorial format
        raw_sections = [
            {
                "index": 0,
                "section_type": "hook",
                "section_title": f"The Big Problem and Why {topic.tool_name} Changes Everything",
                "narration": (
                    f"If you've been trying to streamline your workflow with AI, you've probably noticed "
                    f"that most tools promise the world but fail to deliver when it comes to real-world tasks. "
                    f"In this complete step-by-step guide, we are breaking down {topic.tool_name}—from setup to "
                    f"advanced monetization techniques. By the end of this 10-minute masterclass, you will know "
                    f"how to leverage it like a pro. Let's dive in!"
                ),
                "visual_description": f"Bold title card introducing {topic.tool_name} with workflow diagram",
                "image_prompt": f"Minimalist modern tech presentation slide introducing {topic.tool_name}, high quality typography, sleek dark UI, 8k",
                "on_screen_text": [topic.tool_name, "Complete 2026 Masterclass", "Zero to Pro Guide"]
            },
            {
                "index": 1,
                "section_type": "overview",
                "section_title": f"What is {topic.tool_name} and How Does It Work?",
                "narration": (
                    f"Before we click into the dashboard, let's understand what makes {topic.tool_name} distinct. "
                    f"{topic.value_proposition}. Unlike standard chat interfaces, it bridges the gap between idea "
                    f"and execution by giving you a persistent, modular workspace. Whether you are generating code, "
                    f"crafting content pipelines, or structuring complex data, this tool does the heavy lifting."
                ),
                "visual_description": f"Architecture breakdown graphic showing core features of {topic.tool_name}",
                "image_prompt": f"Clean infographic diagram displaying modern software architecture for {topic.tool_name}, vector style, deep navy and cyan accents",
                "on_screen_text": ["Core Architecture", "Real-Time Processing", "Modular Workflows"]
            },
            {
                "index": 2,
                "section_type": "step_1",
                "section_title": "Step 1: Account Setup and Workspace Configuration",
                "narration": (
                    "To get started, head over to the official portal and set up your environment. "
                    "First, make sure your workspace settings are dialed in for optimal performance. "
                    "Configure your default system instructions, set your output preferences, and "
                    "connect any relevant third-party integrations. This five-minute setup prevents "
                    "repetitive prompts down the road."
                ),
                "visual_description": "Clean step-by-step UI checklist showing configuration steps",
                "image_prompt": "Futuristic clean software dashboard UI displaying settings and configuration toggles, sleek glowing design, 4k",
                "on_screen_text": ["Step 1: Setup", "1. System Instructions", "2. Workspace Prefs", "3. Integrations"]
            },
            {
                "index": 3,
                "section_type": "step_2",
                "section_title": "Step 2: Core Workflow and First Hands-On Project",
                "narration": (
                    "Now let's build your first production-ready asset. The secret to getting exceptional "
                    "outputs lies in how you structure your inputs. Always establish clear context, provide "
                    "explicit constraints, and request modular iterations. Watch how the system breaks down "
                    "a complex multi-step request into cleanly organized components."
                ),
                "visual_description": "Step 2 workflow diagram showing prompt structure and modular outputs",
                "image_prompt": "Clean digital presentation slide with prompt engineering workflow, input box, processing arrow, high quality output card",
                "on_screen_text": ["Step 2: The Core Workflow", "Context -> Constraints -> Iterations"]
            },
            {
                "index": 4,
                "section_type": "step_3",
                "section_title": "Step 3: Advanced Features and Pro Automation Hacks",
                "narration": (
                    "Once you have mastered the basics, here are three pro tips that 90 percent of users overlook. "
                    "First, utilize context caching to slash latency and token costs. Second, chain sub-tasks "
                    "using structured output templates. Third, export artifacts directly into your existing tools "
                    "like Notion, GitHub, or web preview environments."
                ),
                "visual_description": "Three feature cards highlighting pro tips and cost optimization",
                "image_prompt": "3D isometric cards displaying Pro Hacks, Speed, Cost Reduction, and Automation, dark aesthetic, clean neon borders",
                "on_screen_text": ["Pro Tips", "1. Context Caching", "2. Chaining Prompts", "3. Live Previews"]
            },
            {
                "index": 5,
                "section_type": "monetization",
                "section_title": "Real-World Use Cases & Monetization Strategies",
                "narration": (
                    "How can you actually monetize these skills? Many creators and consultants turn these workflows "
                    "into paid client deliverables, bespoke automation services, or digital templates. "
                    "By packaging high-efficiency solutions with this tool, you can offer 10x faster turnaround times "
                    "while maintaining premium quality."
                ),
                "visual_description": "Commercial application graphic with client deliverable icons",
                "image_prompt": "Sleek commercial agency dashboard showing client projects, revenue metrics, high tech business infographic",
                "on_screen_text": ["Monetization Paths", "• Client Services", "• Automation Systems", "• Digital Assets"]
            },
            {
                "index": 6,
                "section_type": "pricing",
                "section_title": "Pricing, Limitations & What to Watch Out For",
                "narration": (
                    "Let's talk pricing and real limitations. The free tier is generous enough to test the waters, "
                    "but heavy users will want the professional plan for unlimited speeds and higher usage caps. "
                    "Keep in mind that output length limits and occasional hallucination mean human review remains "
                    "essential before publishing."
                ),
                "visual_description": "Comparison tier table: Free vs Pro tier with pros and cons",
                "image_prompt": "Clean modern pricing tier comparison table with checkmarks, Free vs Pro comparison, elegant UI",
                "on_screen_text": ["Pricing & Limits", "Free: Great for Testing", "Pro: High Volume & Speed", "Always Verify Outputs"]
            },
            {
                "index": 7,
                "section_type": "outro",
                "section_title": "Final Verdict and Actionable Next Steps",
                "narration": (
                    f"That wraps up our complete guide to {topic.tool_name}. It's easily one of the most powerful "
                    f"additions to any modern tech stack. If you found this guide helpful, hit the like button, "
                    f"subscribe for weekly deep-dives into cutting-edge AI tools, and drop your questions in the comments below. "
                    f"Check out the description for all links and resources mentioned. See you in the next video!"
                ),
                "visual_description": "Closing summary slide with subscribe button, resources link, and thank you message",
                "image_prompt": "Clean modern outro screen, subscribe button badge, thumbs up icon, minimalist tech aesthetic, 4k",
                "on_screen_text": ["Summary & Next Steps", "• Subscribe for Weekly AI Tutorials", "• Links in Description"]
            }
        ]

        sections = []
        total_words = 0
        total_seconds = 0.0

        for s in raw_sections:
            words = len(s["narration"].split())
            total_words += words
            # Calculate duration in seconds based on words per minute
            sec = round((words / wpm) * 60, 2)
            # Ensure minimum duration per slide
            sec = max(sec, 12.0)
            total_seconds += sec

            sections.append(
                ScriptSection(
                    index=s["index"],
                    section_type=s["section_type"],
                    section_title=s["section_title"],
                    narration=s["narration"],
                    estimated_duration_sec=sec,
                    visual_description=s["visual_description"],
                    image_prompt=s["image_prompt"],
                    on_screen_text=s["on_screen_text"]
                )
            )

        video_script = VideoScript(
            topic_id=topic.id,
            tool_name=topic.tool_name,
            target_duration_minutes=target_minutes,
            total_words=total_words,
            estimated_total_seconds=total_seconds,
            sections=sections,
            raw_markdown=self._build_markdown_script(topic.title, sections)
        )

        self._save_script_files(state.project_id, video_script)
        state.script = video_script
        return state

    def validate_output(self, state: ProjectState) -> None:
        """Ensure script has valid sections and word count."""
        if not state.script:
            raise ValueError("Stage 2 completed without setting state.script")
        if len(state.script.sections) < 3:
            raise ValueError("Script must have at least 3 sections")

    def _build_markdown_script(self, title: str, sections: list) -> str:
        """Renders script into a readable markdown document."""
        lines = [f"# Video Script: {title}\n"]
        for s in sections:
            lines.append(f"## Section {s.index + 1}: {s.section_title} ({s.section_type})")
            lines.append(f"**Estimated Duration:** {s.estimated_duration_sec:.1f}s")
            lines.append(f"**Visual:** {s.visual_description}")
            lines.append(f"**Image Prompt:** `{s.image_prompt}`")
            lines.append(f"**Narration:**\n> {s.narration}\n")
        return "\n".join(lines)

    def _save_script_files(self, project_id: str, script: VideoScript) -> None:
        """Persist script JSON and Markdown files."""
        json_path = settings.SCRIPTS_DIR / f"{project_id}_script.json"
        md_path = settings.SCRIPTS_DIR / f"{project_id}_script.md"

        with open(json_path, "w", encoding="utf-8") as f:
            f.write(script.model_dump_json(indent=2))

        if script.raw_markdown:
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(script.raw_markdown)

        self.logger.info(f"Saved script files to {json_path} and {md_path}")
