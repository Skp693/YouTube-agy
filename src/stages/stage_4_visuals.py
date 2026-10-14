"""Stage 4: Visuals and Slide Graphic Generation."""

from pathlib import Path
try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from config.settings import settings
from src.models import ProjectState, VisualAsset, ScriptSection
from src.stages.base import BaseStage

class VisualsStage(BaseStage):
    """Generates visual assets (AI images or high-res explainer slides) for each section."""

    stage_number = 4
    stage_name = "visuals_generation"

    def validate_prerequisites(self, state: ProjectState) -> None:
        """Verify script exists before generating visuals."""
        if not state.script or not state.script.sections:
            raise ValueError("Cannot generate visuals: state.script has no sections")

    def execute(self, state: ProjectState) -> ProjectState:
        """Generates 1920x1080 visuals for each script section."""
        project_images_dir = settings.IMAGES_DIR / state.project_id
        project_images_dir.mkdir(parents=True, exist_ok=True)

        visual_assets = []
        provider = settings.IMAGE_PROVIDER

        self.logger.info(f"Generating visuals (Provider: {provider}) for {len(state.script.sections)} sections")

        for section in state.script.sections:
            output_image_path = project_images_dir / f"slide_{section.index:02d}.png"

            # Check if using AI image provider or built-in professional slide renderer
            if provider == "openai" and settings.OPENAI_API_KEY:
                success = self._generate_ai_image_openai(section.image_prompt, output_image_path)
                if not success:
                    self._render_slide_graphic(section, output_image_path)
            else:
                self._render_slide_graphic(section, output_image_path)

            visual_assets.append(
                VisualAsset(
                    section_index=section.index,
                    file_path=str(output_image_path),
                    prompt=section.image_prompt,
                    visual_type="slide_card"
                )
            )
            self.logger.info(f"Generated visual for section {section.index} -> {output_image_path.name}")

        state.visual_assets = visual_assets
        return state

    def validate_output(self, state: ProjectState) -> None:
        """Verify all sections have corresponding visual assets."""
        if not state.visual_assets:
            raise ValueError("Stage 4 completed without generating visual_assets")
        if len(state.visual_assets) != len(state.script.sections):
            raise ValueError(f"Mismatch: {len(state.visual_assets)} visuals for {len(state.script.sections)} sections")

    def _render_slide_graphic(self, section: ScriptSection, output_path: Path) -> None:
        """Renders an aesthetic 1920x1080 dark-mode slide with typography and accents."""
        width = settings.VIDEO_RESOLUTION_WIDTH
        height = settings.VIDEO_RESOLUTION_HEIGHT

        if not HAS_PIL:
            from visuals import render_slide_native_bmp
            render_slide_native_bmp(
                section_num=section.index + 1,
                section_type=section.section_type,
                title=section.section_title[:65],
                bullets=section.on_screen_text,
                output_path=output_path,
                width=width,
                height=height
            )
            return

        # Dark sleek background
        img = Image.new("RGB", (width, height), color=(15, 23, 42))  # Slate 900
        draw = ImageDraw.Draw(img)

        # Draw subtle grid / background accents
        draw.rectangle([0, 0, width, 12], fill=(59, 130, 246))  # Blue top accent bar
        draw.rectangle([60, 60, width - 60, height - 60], outline=(30, 41, 59), width=2)

        # Header / Section Tag
        tag_text = f"SECTION {section.index + 1} • {section.section_type.upper()}"
        draw.text((100, 100), tag_text, fill=(56, 189, 248))  # Cyan

        # Main Section Title
        draw.text((100, 160), section.section_title[:65], fill=(248, 250, 252))  # White

        # Accent dividing line
        draw.line([(100, 230), (500, 230)], fill=(99, 102, 241), width=4)

        # Content bullets / On-screen text
        y_offset = 300
        for item in section.on_screen_text:
            draw.text((140, y_offset), f"✔  {item}", fill=(203, 213, 225))
            y_offset += 80

        # Footer branding
        footer_text = "AI TOOL EXPLAINER • AUTONOMOUS PIPELINE"
        draw.text((100, height - 120), footer_text, fill=(100, 116, 139))

        img.save(output_path, "PNG")

    def _generate_ai_image_openai(self, prompt: str, output_path: Path) -> bool:
        """Hook to call DALL-E 3 for slide graphics."""
        try:
            import requests
            url = "https://api.openai.com/v1/images/generations"
            headers = {
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "dall-e-3",
                "prompt": prompt,
                "n": 1,
                "size": "1792x1024",  # Landscape
                "quality": "standard"
            }
            res = requests.post(url, json=data, headers=headers, timeout=60)
            res.raise_for_status()
            image_url = res.json()["data"][0]["url"]

            # Download and save
            img_res = requests.get(image_url, timeout=30)
            img_res.raise_for_status()
            with open(output_path, "wb") as f:
                f.write(img_res.content)
            return True
        except Exception as e:
            self.logger.warning(f"OpenAI image generation failed ({e}). Reverting to slide renderer.")
            return False
