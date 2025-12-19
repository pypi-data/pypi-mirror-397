import unittest
from io import StringIO
import sys
from unittest.mock import patch
from felicidad.core import Happiness


class TestHappiness(unittest.TestCase):
    def setUp(self):
        self.happiness = Happiness()

    def test_initial_level(self):
        """Test that initial happiness level is between 60 and 100"""
        self.assertTrue(60 <= self.happiness.level <= 100)

    def test_boost(self):
        """Test that boost increases happiness level but not above 100"""
        initial = self.happiness.level
        self.happiness.boost(10)
        self.assertTrue(self.happiness.level > initial or self.happiness.level == 100)
        self.assertLessEqual(self.happiness.level, 100)

    @patch("sys.stdout", new_callable=StringIO)
    def test_affirmation(self, mock_stdout):
        """Test that affirmation prints something and boosts happiness"""
        initial = self.happiness.level
        self.happiness.affirmation()
        output = mock_stdout.getvalue()
        self.assertIn("Afirmación del momento", output)
        self.assertTrue(self.happiness.level > initial or self.happiness.level == 100)

    @patch("sys.stdout", new_callable=StringIO)
    def test_joke(self, mock_stdout):
        """Test that joke prints something and boosts happiness"""
        initial = self.happiness.level
        self.happiness.joke()
        output = mock_stdout.getvalue()
        self.assertIn("Chiste del día", output)
        self.assertTrue(self.happiness.level > initial or self.happiness.level == 100)

    @patch("sys.stdout", new_callable=StringIO)
    def test_christmas(self, mock_stdout):
        """Test simple execution of christmas mode"""
        # Just ensure it runs without error and prints key messages
        self.happiness.christmas()
        output = mock_stdout.getvalue()
        self.assertIn("MODO NAVIDAD ACTIVADO", output)


if __name__ == "__main__":
    unittest.main()
