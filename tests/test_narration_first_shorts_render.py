"""Offline render smoke: the generated tone is ONLY a test fixture, never a voiceover."""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from scripts.narration_first_shorts import render


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"),
                     "FFmpeg and FFprobe required")
class NarrationFirstRenderSmoke(unittest.TestCase):
    def test_single_master_audio_with_presenter_and_still(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            video=root/"source.mp4"
            portrait=root/"portrait.jpg"
            output=root/"short.mp4"
            subprocess.run([
                "ffmpeg","-v","error","-y","-f","lavfi","-i",
                "color=c=0x283d51:s=360x640:r=30",
                "-f","lavfi","-i","aevalsrc=0.2*sin(2*PI*440*t)*(0.35+0.65*sin(2*PI*0.7*t)^2):s=48000",
                "-t","8","-c:v","libx264","-preset","ultrafast",
                "-pix_fmt","yuv420p","-c:a","aac","-shortest",str(video)
            ],check=True)
            subprocess.run([
                "ffmpeg","-v","error","-y","-f","lavfi","-i",
                "color=c=0x6c7f91:s=640x360",
                "-frames:v","1",str(portrait)
            ],check=True)
            manifest=root/"manifest.json"
            manifest.write_text(json.dumps({
                "topic":"Offline technical fixture only",
                "narration_source_video":str(video),
                "brand":"QUADDIS",
                "scenes":[
                    {"start":0,"end":3,"media":str(video),
                     "mode":"presenter_native","label":"Source matched"},
                    {"start":3,"end":8,"media":str(portrait),
                     "mode":"pip_still","label":"No moving lips"}
                ],
                "captions":[]
            }),encoding="utf-8")
            result=render(manifest,output)
            self.assertEqual(result["status"],"REVIEW_ONLY")
            self.assertEqual(result["audio_continuity"]["decision"], "CONTINUITY_PASS")
            self.assertEqual(result["size"],"720x1280")
            self.assertTrue(output.is_file())
            self.assertGreater(output.stat().st_size,50000)
            self.assertLess(abs(result["duration"]-8),0.5)


if __name__=="__main__":
    unittest.main()
