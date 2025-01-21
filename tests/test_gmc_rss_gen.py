import unittest
from unittest.mock import patch, Mock
from gmc_rss_gen import GMCRSSGenerator

class TestGMCRSSGenerator(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.rss_gen = GMCRSSGenerator()
        self.count_response = Mock()
        self.count_response.json.return_value =  eval('{"count": 1}')
        self.catalog_response = Mock()
        with open('tests/mock_api_responses/catalog_65626325_fox-ranger-glove.json') as f:
            self.catalog_response.json.return_value = eval(f.read().replace('true', 'True').replace('false', 'False').replace('null', 'None'))
        
    def tearDown(self):
        """Clean up after each test method."""
        pass
    
    @patch('lightspeed_google_feed.lightspeed.requests')
    def test_refresh_feed_files(self, mock_requests):
        mock_requests.get.side_effect = [self.count_response, self.catalog_response]

        # Execute and check mock requests were called only twice
        self.rss_gen.refresh_feed_files()
        self.assertEqual(mock_requests.get.call_count, 2)
        
        # Read and verify shopping online inventory feed file
        shopping_online_feed = self.rss_gen.read_feed_file(self.rss_gen.SHOPPING_ONLINE_INVENTORY_FEED_FILENAME)
        # Count number of <item> tags in the feed
        shopping_item_count = shopping_online_feed.count('<item>')
        self.assertEqual(shopping_item_count, 7, "Expected 7 items in shopping online inventory feed")

        # Read and verify local listings feed file
        local_listings_feed = self.rss_gen.read_feed_file(self.rss_gen.LOCAL_LISTINGS_FEED_FILENAME)
        # Count number of <item> tags in the feed
        item_count = local_listings_feed.count('<item>')
        self.assertEqual(item_count, 7, "Expected 7 items in local listings feed")
    
    @patch('lightspeed_google_feed.lightspeed.requests')
    def test_prepare_template_data_basic(self, mock_requests):
        mock_requests.get.side_effect = [self.count_response, self.catalog_response]

        products = self.rss_gen.lightspeed_api.get_all_visible_products()
        products_for_template = self.rss_gen.prepare_template_data(products)
        
        self.assertEqual(len(products_for_template), 7, "Expected 7 items in template data")

        # Check if the products contains the expected keys
        product_expected_keys = ['id', 'stock_level', 'fulltitle', 'description', 'price', 'available', 
                                 'ean', 'code', 'weight', 'url', 'images', 'categories', 'brand', 'age_group', 
                                 'color', 'gender', 'size']
        for product in products_for_template:
            for key in product_expected_keys:
                self.assertIn(key, product)
    
    @patch('lightspeed_google_feed.lightspeed.requests')
    def test_prepare_template_data_title_and_size_conversions(self, mock_requests):
        mock_requests.get.side_effect = [self.count_response, self.catalog_response]
        products = self.rss_gen.lightspeed_api.get_all_visible_products()
        products_for_template = self.rss_gen.prepare_template_data(products)

        for product in products_for_template:
            self.assertTrue(product['fulltitle'].startswith('Fox Ranger Glove'))

            if product['id'] == "65626325_110095793":
                self.assertEqual("2XL", product['size'])
                self.assertEqual("graphite grey", product['color'])
            elif product['id'] == "65626325_110095787":
                self.assertEqual("XL", product['size'])
                self.assertEqual("graphite grey", product['color'])
            elif product['id'] == "65626325_110095787":
                self.assertEqual("L", product['size'])
                self.assertEqual("graphite grey", product['color'])
            elif product['id'] == "65626325_110095783":
                self.assertEqual("M", product['size'])
                self.assertEqual("graphite grey", product['color'])
            elif product['id'] == "65626325_110095779":
                self.assertEqual("S", product['size'])
                self.assertEqual("graphite grey", product['color'])
            elif product['id'] == "65626325_110095773":
                self.assertEqual("2XL", product['size'])
                self.assertEqual("hunter green", product['color'])
            elif product['id'] == "65626325_110095763":
                self.assertEqual("XL", product['size'])
                self.assertEqual("hunter green", product['color'])
    
if __name__ == '__main__':
    unittest.main() 