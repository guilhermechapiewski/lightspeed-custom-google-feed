import unittest
from unittest.mock import patch, Mock
from lightspeed_google_feed.gmc_feed import GMCFeedGenerator, GMCFeedProduct

class TestGMCFeedGenerator(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.feed_gen = GMCFeedGenerator()
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
        self.feed_gen.refresh_feed_files()
        self.assertEqual(mock_requests.get.call_count, 2)
        
        # Read and verify shopping online inventory feed file
        shopping_online_feed = self.feed_gen.read_feed_file(self.feed_gen.SHOPPING_ONLINE_INVENTORY_FEED_FILENAME)
        # Count number of <item> tags in the feed
        shopping_item_count = shopping_online_feed.count('<item>')
        self.assertEqual(shopping_item_count, 7, "Expected 7 items in shopping online inventory feed")

        # Read and verify local listings feed file
        local_listings_feed = self.feed_gen.read_feed_file(self.feed_gen.LOCAL_LISTINGS_FEED_FILENAME)
        # Count number of <item> tags in the feed
        item_count = local_listings_feed.count('<item>')
        self.assertEqual(item_count, 7, "Expected 7 items in local listings feed")
    
    @patch('lightspeed_google_feed.lightspeed.requests')
    def test_prepare_template_data_basic(self, mock_requests):
        mock_requests.get.side_effect = [self.count_response, self.catalog_response]

        products = self.feed_gen.lightspeed_api.get_all_visible_products()
        products_for_template = self.feed_gen.template_data.prepare_template_data(products)
        
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
        products = self.feed_gen.lightspeed_api.get_all_visible_products()
        products_for_template = self.feed_gen.template_data.prepare_template_data(products)

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

class TestGMCFeedProduct(unittest.TestCase):

    def test_default_weight(self):
        product = GMCFeedProduct(id="123", variant_id="456")
        self.assertEqual(product.weight, 25, "Expected default weight to be 25")

        product.set_weight(None)
        self.assertEqual(product.weight, 25, "Expected weight to be 25")

        product.set_weight(0)
        self.assertEqual(product.weight, 25, "Expected weight to be 25")

        product.set_weight(500)
        self.assertEqual(product.weight, 500, "Expected weight to be 500")
    
    def test_size_conversion(self):
        product = GMCFeedProduct(id="123", variant_id="456")
        
        product.set_variant_title('"Color: Graphite Grey","Size: 2 XL"')
        self.assertEqual(product.get_size(), "2XL", "Expected size to be 2XL")

        product.set_variant_title('"Color: Graphite Grey","Size: 3 XL"')
        self.assertEqual(product.get_size(), "3XL", "Expected size to be 2XL")

        product.set_variant_title('"Color: Graphite Grey","Size: Extra large"')
        self.assertEqual(product.get_size(), "XL", "Expected size to be XL")

        product.set_variant_title('"Color: Graphite Grey","Size: Large"')
        self.assertEqual(product.get_size(), "L", "Expected size to be L")

        product.set_variant_title('"Color: Graphite Grey","Size: Small"')
        self.assertEqual(product.get_size(), "S", "Expected size to be S")

        product.set_variant_title('"Color: Graphite Grey","Size: X Small"')
        self.assertEqual(product.get_size(), "XS", "Expected size to be XS")

        product.set_variant_title('"Color: Graphite Grey","Size: 2 XS"')
        self.assertEqual(product.get_size(), "XXS", "Expected size to be 2XL")
    
    def test_size_conversion_for_youth_products(self):
        product = GMCFeedProduct(id="123", variant_id="456")
        product.set_title("Fox Ranger Glove Youth")
        product.set_variant_title('"Color: Graphite Grey","Size: 2 XL"')
        self.assertEqual(product.get_size(), "2XL", "Expected size to be 2XL")

        product.set_variant_title('"Color: Graphite Grey","Size: Youth Small"')
        self.assertEqual(product.get_size(), "S", "Expected size to be S")

        product.set_variant_title('"Color: Graphite Grey","Size: Youth Medium"')
        self.assertEqual(product.get_size(), "M", "Expected size to be M")

        product.set_variant_title('"Color: Graphite Grey","Size: Youth Large"')
        self.assertEqual(product.get_size(), "L", "Expected size to be L")

        product.set_variant_title('"Color: Graphite Grey","Size: Youth Extra Large"')
        self.assertEqual(product.get_size(), "XL", "Expected size to be XL")

        product.set_variant_title('"Color: Graphite Grey","Size: Youth XL"')
        self.assertEqual(product.get_size(), "XL", "Expected size to be XL")

    def test_gender_conversion_from_variant_title(self):
        product = GMCFeedProduct(id="123", variant_id="456")
        
        product.set_variant_title('"Color: Graphite Grey","Size: 2 XL"')
        self.assertEqual(product.get_gender(), "unisex", "Expected gender to be unisex")

        product.set_variant_title('"Color: Graphite Grey","Size: 2 XL","Gender: Male"')
        self.assertEqual(product.get_gender(), "male", "Expected gender to be male")

        product.set_variant_title('"Color: Graphite Grey","Size: 2 XL","Gender: Female"')
        self.assertEqual(product.get_gender(), "female", "Expected gender to be female")

        product.set_variant_title('default')
        self.assertEqual(product.get_gender(), "unisex", "Expected gender to be unisex")

        product.set_variant_title('"Color: Graphite Grey"')
        self.assertEqual(product.get_gender(), "unisex", "Expected gender to be unisex")
    
    def test_gender_conversion_from_title(self):
        product = GMCFeedProduct(id="123", variant_id="456")

        product.set_title("Fox Ranger Glove")
        self.assertEqual(product.get_gender(), "unisex", "Expected gender to be unisex")

        product.set_title("Fox Ranger Glove Men")
        self.assertEqual(product.get_gender(), "male", "Expected gender to be male")

        product.set_title("Fox Ranger Glove Women")
        self.assertEqual(product.get_gender(), "female", "Expected gender to be female")

        product.set_title("Fox Ranger Glove Men's")
        self.assertEqual(product.get_gender(), "male", "Expected gender to be male")

        product.set_title("Fox Ranger Glove Women's")
        self.assertEqual(product.get_gender(), "female", "Expected gender to be female")

    def test_gender_conversion_from_categories(self):
        product = GMCFeedProduct(id="123", variant_id="456")

        product.set_title("Fox Ranger Glove")
        product.set_variant_title('"Color: Graphite Grey"')
        product.set_categories({"4568213": { "id": 4568213, "isVisible": True, "depth": 2, "sortOrder": 1, "title": "MTB gear" }})
        self.assertEqual(product.get_gender(), "unisex", "Expected gender to be unisex")

        product.set_categories({"4568213": { "id": 4568213, "isVisible": True, "depth": 2, "sortOrder": 1, "title": "Men" }})
        self.assertEqual(product.get_gender(), "male", "Expected gender to be male")

        product.set_categories({"4568213": { "id": 4568213, "isVisible": True, "depth": 2, "sortOrder": 1, "title": "Women" }})
        self.assertEqual(product.get_gender(), "female", "Expected gender to be female")
    
    def test_age_group_conversion_from_categories(self):
        product = GMCFeedProduct(id="123", variant_id="456")

        product.set_title("Fox Ranger Glove")
        self.assertEqual(product.get_age_group(), "adult", "Expected age group to be adult")

        product.set_title("Fox Ranger Glove Youth")
        self.assertEqual(product.get_age_group(), "kids", "Expected age group to be kids")

    def test_availability(self):
        product = GMCFeedProduct(id="123", variant_id="456")
        
        product.set_stock_level(0)
        self.assertFalse(product.is_available(), "Expected product to be unavailable")

        product.set_stock_level(1)
        self.assertTrue(product.is_available(), "Expected product to be available")

        product.set_stock_level(0)
        product.set_stock_tracking("disabled")
        self.assertTrue(product.is_available(), "Expected product to be available")
    
    def test_categories(self):
        product = GMCFeedProduct(id="123", variant_id="456")

        api_categories = {
            "4701200": {
                "id": 4701200,
                "createdAt": "2025-01-14T15:54:15+00:00",
                "updatedAt": "2025-01-15T00:02:43+00:00",
                "isVisible": True,
                "depth": 3,
                    "sortOrder": 6,
                    "image": False,
                    "url": "men/mtb-gear/gloves",
                    "title": "Gloves"
                },
            "4568213": {
                "id": 4568213,
                "createdAt": "2024-06-26T23:59:10+00:00",
                "updatedAt": "2025-01-16T01:43:13+00:00",
                "isVisible": True,
                "depth": 2,
                "sortOrder": 1,
                "image": {
                    "id": 66837754,
                    "thumb": "https://cdn.shoplightspeed.com/shops/669439/files/66837754/50x50x2/file.jpg",
                    "src": "https://cdn.shoplightspeed.com/shops/669439/files/66837754/file.jpg"
                },
                "url": "men/mtb-gear",
                "title": "MTB gear"
            },
            "4701199": {
                "id": 4701199,
                "createdAt": "2025-01-14T15:53:13+00:00",
                "updatedAt": "2025-01-16T01:59:31+00:00",
                "isVisible": True,
                "depth": 1,
                "sortOrder": 2,
                "image": {
                    "id": 67976284,
                    "thumb": "https://cdn.shoplightspeed.com/shops/669439/files/67976284/50x50x2/file.jpg",
                    "src": "https://cdn.shoplightspeed.com/shops/669439/files/67976284/file.jpg"
                },
                "url": "men",
                "title": "Men"
            }
        }

        product.set_categories(api_categories)
        
        template_categories = product.get_categories()
        self.assertEqual(template_categories[0]["title"], "Men", "Expected first category to be Men")
        self.assertEqual(template_categories[0]["subs"][0]["title"], "MTB gear", "Expected first subcategory to be MTB gear")
        self.assertEqual(template_categories[0]["subs"][0]["subs"][0]["title"], "Gloves", "Expected subcategory's subcategory to be Gloves")
if __name__ == '__main__':
    unittest.main() 