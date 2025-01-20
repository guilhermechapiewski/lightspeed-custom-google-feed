import unittest
from unittest.mock import patch, Mock
from gmc_rss_gen import GMCRSSGenerator

class TestGMCRSSGenerator(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.generator = GMCRSSGenerator()
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

        # Call method and verify result
        result = self.generator.refresh_feed_files()
        self.assertEqual(mock_requests.get.call_count, 2)
        
        # Read and verify shopping online inventory feed file
        shopping_online_feed = self.generator.read_feed_file(self.generator.SHOPPING_ONLINE_INVENTORY_FEED_FILENAME)
        
        # Count number of <item> tags in the feed
        shopping_item_count = shopping_online_feed.count('<item>')
        self.assertEqual(shopping_item_count, 7, "Expected 7 items in shopping online inventory feed")

        # Read and verify local listings feed file
        local_listings_feed = self.generator.read_feed_file(self.generator.LOCAL_LISTINGS_FEED_FILENAME)
        
        # Count number of <item> tags in the feed
        item_count = local_listings_feed.count('<item>')
        self.assertEqual(item_count, 7, "Expected 7 items in local listings feed")

if __name__ == '__main__':
    unittest.main() 