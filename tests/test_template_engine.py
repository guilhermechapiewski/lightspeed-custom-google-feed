import unittest
from lightspeed_google_feed.template_engine import TemplateEngine

class TestTemplateEngine(unittest.TestCase):
    def setUp(self):
        self.engine = TemplateEngine()

    def test_jinja_cdata(self):
        """Test CDATA wrapping filter"""
        # Test with normal string
        self.assertEqual(self.engine._jinja_cdata("test string"), "<![CDATA[ test string ]]>")
        
        # Test with empty string
        self.assertEqual(self.engine._jinja_cdata(""), "")
        
        # Test with None
        self.assertIsNone(self.engine._jinja_cdata(None))

    def test_jinja_url(self):
        """Test URL formatting filter"""
        shop_domain = "https://myshop.com"
        self.engine.SHOP = {'domain': shop_domain}
        
        # Test http to https conversion
        self.assertEqual(self.engine._jinja_url("http://myshop.com/product"), "https://myshop.com/product")
        
        # Test adding domain to relative URL
        self.assertEqual(self.engine._jinja_url("/product"), f"{shop_domain}/product")
        
        # Test with None
        self.assertIsNone(self.engine._jinja_url(None))

    def test_jinja_url_image(self):
        """Test image URL formatting filter"""
        # Test file.jpg to image.jpg conversion
        self.assertEqual(self.engine._jinja_url_image("path/to/file.jpg"), "path/to/image.jpg")
        
        # Test with non-matching string
        self.assertEqual(self.engine._jinja_url_image("path/to/other.jpg"), "path/to/other.jpg")
        
        # Test with None
        self.assertIsNone(self.engine._jinja_url_image(None))

    def test_jinja_limit(self):
        """Test limit filter for different data types"""
        # Test with list
        test_list = [1, 2, 3, 4, 5]
        self.assertEqual(self.engine._jinja_limit(test_list, 3), [1, 2, 3])
        
        # Test with dict
        test_dict = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
        limited_dict = self.engine._jinja_limit(test_dict, 2)
        self.assertEqual(len(limited_dict), 2)
        
        # Test with non-iterable
        test_string = "test"
        self.assertEqual(self.engine._jinja_limit(test_string, 2), "test")

    def test_jinja_money_float(self):
        """Test money float formatting filter"""
        # Test dollar sign removal
        self.assertEqual(self.engine._jinja_money_float("$10.50"), "10.50")
        
        # Test comma removal
        self.assertEqual(self.engine._jinja_money_float("1,234.56"), "1234.56")
        
        # Test adding trailing zero
        self.assertEqual(self.engine._jinja_money_float("10.5"), "10.50")
        
        # Test integer conversion
        self.assertEqual(self.engine._jinja_money_float("10"), "10.00")

        # Test integer conversion
        self.assertEqual(self.engine._jinja_money_float("010"), "10.00")
