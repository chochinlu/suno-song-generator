import unittest
from ai_generation_functions import generate_lyrics
from lyrics_annotations import bark_tags, chirp_tags

class TestGenerateLyrics(unittest.TestCase):

    def test_generate_lyrics(self):
        # Test function
        instruments = "Guitar, Piano"
        language = "English"
        thought = "A song about love"
        result = generate_lyrics(instruments, language, thought)

        # Validate results
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

        # Check for annotations
        lines = result.split('\n')
        annotation_count = 0
        for line in lines:
            line_annotations = [ann for ann in bark_tags.keys() if ann in line] + [ann for ann in chirp_tags.keys() if ann in line]
            if line_annotations:
                annotation_count += len(line_annotations)
                # Check if the annotation is at the start of the line
                self.assertTrue(any(line.strip().startswith(ann) for ann in line_annotations))

        # Check if the lyrics contain the specified instruments and language
        self.assertTrue(any(instrument.lower() in result.lower() for instrument in instruments.split(', ')))

        print(f"Generated lyrics:\n{result}")

if __name__ == '__main__':
    unittest.main()