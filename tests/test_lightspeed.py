import unittest
from unittest.mock import patch, Mock
from lightspeed_google_feed.lightspeed import LightspeedEcomAPI

class TestLightspeedEcomAPI(unittest.TestCase):

    def setUp(self):
        self.api = LightspeedEcomAPI()

    @patch('lightspeed_google_feed.lightspeed.requests')
    def test_get_product_count(self, mock_requests):
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {"count": 123}
        mock_requests.get.return_value = mock_response

        # Call method and verify result
        count = self.api.get_product_count()
        self.assertEqual(count, 123)

        # Verify request was made correctly
        mock_requests.get.assert_called_once_with(
            f"{self.api.BASE_URL}/catalog/count.json",
            auth=self.api.AUTH
        )

    @patch('lightspeed_google_feed.lightspeed.requests')
    def test_get_all_products(self, mock_requests):
        # Setup mock responses
        count_response = Mock()
        count_response.json.return_value = {"count": 300}

        products_response = Mock()
        products_response.json.return_value = {
            "products": [{"id": 1}, {"id": 2}]
        }

        mock_requests.get.side_effect = [count_response] + [products_response] * 2

        # Call method
        products = self.api.get_all_products()

        # Verify results
        self.assertEqual(len(products), 4)  # 2 products per page * 2 pages
        self.assertEqual(mock_requests.get.call_count, 3)  # 1 count call + 2 product page calls

    @patch('lightspeed_google_feed.lightspeed.requests')
    def test_get_all_visible_products(self, mock_requests):
        # Setup mock responses
        count_response = Mock()
        count_response.json.return_value = {"count": 250}

        products_response = Mock()
        products_response.json.return_value = {
            "products": [
                {"id": 1, "isVisible": True},
                {"id": 2, "isVisible": False},
                {"id": 3, "isVisible": True}
            ]
        }

        mock_requests.get.side_effect = [count_response, products_response]

        # Call method
        visible_products = self.api.get_all_visible_products()

        # Verify results
        self.assertEqual(len(visible_products), 2)
        self.assertTrue(all(p["isVisible"] for p in visible_products))

if __name__ == '__main__':
    unittest.main()