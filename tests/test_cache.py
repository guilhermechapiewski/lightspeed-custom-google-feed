import unittest
import time
from lightspeed_google_feed.cache import SimpleCache

class TestLightspeedAPI(unittest.TestCase):

    def setUp(self):
        self.cache = SimpleCache()

    def test_simple_set_and_get(self):
        self.cache.set("test_key", "test_value")
        self.assertEqual(self.cache.get("test_key"), "test_value")
    
    def test_simple_get_none(self):
        self.assertIsNone(self.cache.get("nonexistent_key"))
    
    def test_simple_set_and_get_with_expiration(self):
        self.cache.set("test_another_key", "test_another_value", time=2)
        self.assertEqual(self.cache.get("test_another_key"), "test_another_value")
        time.sleep(1)
        self.assertEqual(self.cache.get("test_another_key"), "test_another_value")
        time.sleep(2)
        self.assertIsNone(self.cache.get("test_another_key"))

if __name__ == '__main__':
    unittest.main()