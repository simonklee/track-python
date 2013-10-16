import track
import unittest

class TrackTestCase(unittest.TestCase):
    def test_version(self):
        self.assertEqual(track.__version__, '0.1.0')
