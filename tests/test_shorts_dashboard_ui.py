"""Dashboard must visibly separate review-only Shorts from long-video generation."""
import unittest
from pathlib import Path


ROOT=Path(__file__).resolve().parent.parent


class ShortsDashboardUI(unittest.TestCase):
    def test_shorts_review_form_is_present(self):
        html=(ROOT/"static"/"index.html").read_text(encoding="utf-8")
        for required_id in (
            "shorts-review-manifest", "shorts-review-btn",
            "shorts-review-status", "shorts-review-video",
            "shorts-review-link"
        ):
            with self.subTest(element=required_id):
                self.assertIn(f'id="{required_id}"', html)
        self.assertIn("review only", html.lower())
        self.assertNotIn("Safe for YouTube Monetization", html)
        self.assertNotIn("Takes about 1–2 minutes. Runs completely offline", html)

    def test_shorts_review_action_uses_local_endpoint(self):
        js=(ROOT/"static"/"app.js").read_text(encoding="utf-8")
        self.assertIn('fetch("/api/shorts/start"', js)
        self.assertIn('setupShortsReview();', js)
        self.assertIn('shortsReviewVideo.src =', js)
        self.assertIn('shortsReviewStatus.textContent =', js)


if __name__ == "__main__":
    unittest.main()
