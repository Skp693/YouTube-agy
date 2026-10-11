"""Stage 3: Voiceover / AI Speech Synthesis."""

from pathlib import Path
import wave
import struct
import math
from config.settings import settings
from src.models import ProjectState, AudioAsset
from src.stages.base import BaseStage

class VoiceoverStage(BaseStage):
    """Generates audio voiceover for each section using AI TTS services."""

    stage_number = 3
    stage_name = "voiceover_synthesis"

    def validate_prerequisites(self, state: ProjectState) -> None:
        """Verify script exists before synthesizing voiceover."""
        if not state.script or not state.script.sections:
            raise ValueError("Cannot synthesize audio: state.script has no sections")

    def execute(self, state: ProjectState) -> ProjectState:
        """Synthesizes speech audio for each script section."""
        project_audio_dir = settings.AUDIO_DIR / state.project_id
        project_audio_dir.mkdir(parents=True, exist_ok=True)

        audio_assets = []
        provider = settings.TTS_PROVIDER

        self.logger.info(f"Generating voiceover using provider '{provider}' for {len(state.script.sections)} sections")

        for section in state.script.sections:
            output_audio_path = project_audio_dir / f"section_{section.index:02d}.wav"
            
            # Synthesize or fallback
            duration = self._synthesize_section(
                text=section.narration,
                output_path=output_audio_path,
                provider=provider,
                target_duration=section.estimated_duration_sec
            )

            # Update section duration with actual audio duration
            section.estimated_duration_sec = duration

            audio_assets.append(
                AudioAsset(
                    section_index=section.index,
                    file_path=str(output_audio_path),
                    duration_sec=duration
                )
            )
            self.logger.info(f"Generated section {section.index} voiceover ({duration:.2f}s) -> {output_audio_path.name}")

        state.audio_assets = audio_assets
        return state

    def validate_output(self, state: ProjectState) -> None:
        """Verify all sections have corresponding audio assets."""
        if not state.audio_assets:
            raise ValueError("Stage 3 completed without generating audio_assets")
        if len(state.audio_assets) != len(state.script.sections):
            raise ValueError(f"Mismatch: {len(state.audio_assets)} audio assets for {len(state.script.sections)} sections")

    def _synthesize_section(
        self,
        text: str,
        output_path: Path,
        provider: str,
        target_duration: float
    ) -> float:
        """Synthesizes speech to audio file. Fallbacks to clean synthetic audio if no API key."""
        if provider == "elevenlabs" and settings.ELEVENLABS_API_KEY:
            try:
                return self._call_elevenlabs(text, output_path)
            except Exception as e:
                self.logger.warning(f"ElevenLabs TTS call failed ({e}). Falling back to local placeholder.")
        
        elif provider == "openai" and settings.OPENAI_API_KEY:
            try:
                return self._call_openai_tts(text, output_path)
            except Exception as e:
                self.logger.warning(f"OpenAI TTS call failed ({e}). Falling back to local placeholder.")

        # Fallback generator: creates a clean, silent-padded test wave file matching target duration
        return self._generate_placeholder_audio(output_path, target_duration)

    def _call_elevenlabs(self, text: str, output_path: Path) -> float:
        """ElevenLabs REST or SDK synthesis call."""
        # Skeleton hook for ElevenLabs API
        import requests
        voice_id = settings.ELEVENLABS_VOICE_ID
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": settings.ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }
        response = requests.post(url, json=data, headers=headers, timeout=60)
        response.raise_for_status()

        # Save mp3 file
        mp3_path = output_path.with_suffix(".mp3")
        with open(mp3_path, "wb") as f:
            f.write(response.content)

        # Estimate duration roughly based on word count
        words = len(text.split())
        return round((words / settings.WORDS_PER_MINUTE) * 60, 2)

    def _call_openai_tts(self, text: str, output_path: Path) -> float:
        """OpenAI TTS synthesis call."""
        import requests
        url = "https://api.openai.com/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "tts-1",
            "input": text,
            "voice": settings.OPENAI_TTS_VOICE
        }
        response = requests.post(url, json=data, headers=headers, timeout=60)
        response.raise_for_status()

        mp3_path = output_path.with_suffix(".mp3")
        with open(mp3_path, "wb") as f:
            f.write(response.content)

        words = len(text.split())
        return round((words / settings.WORDS_PER_MINUTE) * 60, 2)

    def _generate_placeholder_audio(self, output_path: Path, duration_sec: float) -> float:
        """Generates a clean valid WAV file for offline testing and pipeline dry-runs."""
        sample_rate = 22050
        num_samples = int(sample_rate * duration_sec)
        
        # Produce a very soft 440Hz tone with fade-in/out to simulate speech track
        with wave.open(str(output_path), "w") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            
            raw_data = bytearray()
            for i in range(num_samples):
                # Gentle ambient tone at very low amplitude (0.01) to verify playback
                val = int(327.0 * math.sin(2.0 * math.pi * 440.0 * (i / sample_rate)))
                raw_data.extend(struct.pack("<h", val))
            
            wav_file.writeframes(raw_data)

        return duration_sec
