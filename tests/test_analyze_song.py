import os
import unittest
from ai_generation_functions import analyze_song

class TestAnalyzeSong(unittest.TestCase):
    def setUp(self):
        # Read test lyrics
        with open('tests/ly_1.txt', 'r', encoding='utf-8') as f:
            self.lyrics = f.read()

    def test_analyze_song(self):
        # Call analyze_song function
        result = analyze_song(self.lyrics)
        print(result)

        # Check if song_style is a comma-separated string
        self.assertIsInstance(result[0], str)
        self.assertTrue(',' in result[0])

        # Check if song_instruments contains Intro, Verse, and Chorus
        self.assertIn('Intro', result[1])
        self.assertIn('Verse', result[1])
        self.assertIn('Chorus', result[1])

if __name__ == '__main__':
    unittest.main()