"""
tests/test_moderation.py
-------------------------
Basic unit tests for the moderation logic, using Python's built-in
'unittest' framework (no extra install needed).

Run with:
    python -m unittest discover tests
"""

import sys
import os
import unittest

# Allow importing from the project root when running tests directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from moderation.text_moderator import analyze_text


class TestTextModerator(unittest.TestCase):
    def test_clean_text_is_approved(self):
        result = analyze_text("Hello, I really enjoyed this article, thank you!")
        self.assertEqual(result["decision"], "approved")

    def test_profanity_is_flagged_or_rejected(self):
        result = analyze_text("This is such a fucking stupid idiot post")
        self.assertIn(result["decision"], ["flagged", "rejected"])
        self.assertIn("profanity", result["categories"])

    def test_toxic_keywords_detected(self):
        result = analyze_text("I hate you, you should just die")
        self.assertIn("toxicity", result["categories"])

    def test_spam_link_detected(self):
        result = analyze_text("Check this out http://a.com http://b.com http://c.com")
        self.assertEqual(result["decision"], "rejected")
        self.assertIn("spam", result["categories"])

    def test_excessive_caps_detected(self):
        result = analyze_text("WHY IS EVERYONE SO SLOW TODAY HELLO")
        self.assertIn("excessive_caps", result["categories"])


if __name__ == "__main__":
    unittest.main()
