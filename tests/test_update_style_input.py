import unittest
from ai_generation_functions import update_style_input
from music_categories import music_categories

class TestUpdateStyleInput(unittest.TestCase):

    def test_update_style_input(self):
        # Test function
        song_style = "Pop"
        thought = "Add some electronic elements"
        result = update_style_input(song_style, thought)

        # Validate results
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        
        # Check if the result contains words related to the original style or thought
        self.assertTrue(any(word.lower() in result.lower() for word in ["pop", "electronic"]))

        # Check if the result contains at least one word from music_categories
        all_categories = set(music_categories['Styles'] + music_categories['Genres'] + music_categories['Types'])
        self.assertTrue(any(category.lower() in result.lower() for category in all_categories))

        print(f"Generated style: {result}")

    def test_update_style_input_empty_thought(self):
        # Test case without additional thought
        song_style = "Rock"
        result = update_style_input(song_style)

        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        self.assertIn("rock", result.lower())

        # Check if the result contains at least one word from music_categories
        all_categories = set(music_categories['Styles'] + music_categories['Genres'] + music_categories['Types'])
        self.assertTrue(any(category.lower() in result.lower() for category in all_categories))

        print(f"Generated style without additional thought: {result}")

if __name__ == '__main__':
    unittest.main()