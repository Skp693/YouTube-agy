"""Behavioral and smoke tests for the fail-closed Shorts composer."""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from shorts_pipeline import ShortSpecError, load_manifest, render_short


class ShortsPipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def make_manifest(self, scenes):
        p = self.dir / "short.json"
        p.write_text(json.dumps({"title":"Short test", "output":"short.mp4", "scenes":scenes}), encoding="utf-8")
        return p

    def test_refuses_missing_narration_in_broll(self):
        path = self.make_manifest([{"type":"broll", "video":"broll.mp4", "seconds":4}])
        with self.assertRaisesRegex(ShortSpecError, "narration"):
            load_manifest(path)

    def test_refuses_missing_presenter_clip(self):
        path = self.make_manifest([{"type":"presenter_full", "video":"not_found.mp4", "seconds":3}])
        with self.assertRaisesRegex(ShortSpecError, "not found"):
            load_manifest(path)

    def test_refuses_video_over_one_minute(self):
        path = self.make_manifest([{"type":"broll", "video":"x.mp4", "narration":"x.wav", "seconds":61}])
        with self.assertRaisesRegex(ShortSpecError, "60"):
            load_manifest(path)

    def test_refuses_missing_audio_in_avatar_and_does_not_invent_speech(self):
        if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
            self.skipTest('ffmpeg missing')
        muted = self.dir / 'mute.mp4'
        subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=blue:s=320x568:r=30:d=2','-t','2','-pix_fmt','yuv420p','-y',str(muted)], check=True)
        path = self.make_manifest([{"type":"presenter_full", "video":"mute.mp4", "seconds":1}])
        with self.assertRaisesRegex(ShortSpecError, "audio"):
            render_short(path)
        self.assertFalse((self.dir / 'short.mp4').exists())

    def test_renders_vertical_short_with_original_presenter_audio_and_broll_voice(self):
        if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
            self.skipTest('ffmpeg missing')
        presenter = self.dir / 'presenter.mp4'
        broll = self.dir / 'broll.mp4'
        narration = self.dir / 'narration.wav'
        subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=green:s=320x568:r=30:d=2', '-f','lavfi','-i','sine=frequency=600:duration=2', '-t','2','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-y',str(presenter)],check=True)
        subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=blue:s=320x568:r=30:d=2', '-t','2','-pix_fmt','yuv420p','-y',str(broll)],check=True)
        subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','sine=frequency=440:duration=1.5', '-y',str(narration)],check=True)
        path=self.make_manifest([
            {"type":"presenter_pip","video":"presenter.mp4", "background":"broll.mp4", "seconds":1},
            {"type":"broll", "video":"broll.mp4", "narration":"narration.wav", "seconds":1}
        ])
        result=render_short(path)
        out=Path(result['output'])
        self.assertTrue(out.exists())
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out)]))
        video=next(s for s in probe['streams'] if s['codec_type']=='video')
        self.assertEqual((video['width'],video['height']),(1080,1920))
        self.assertTrue(any(s['codec_type']=='audio' for s in probe['streams']))
        self.assertGreater(float(probe['format']['duration']),1.8)
        self.assertLess(float(probe['format']['duration']),2.25)
        self.assertFalse(result['published'])


if __name__=='__main__':
    unittest.main()
