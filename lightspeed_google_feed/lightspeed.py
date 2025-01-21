import math
import requests
import logging
from config import API_KEY, API_SECRET, BASE_URL

class LightspeedAPI:
    
    def __init__(self):
        self.BASE_URL = BASE_URL
        self.AUTH = (API_KEY, API_SECRET)
        self.logger = logging.getLogger(__name__)

    def get_product_count(self):
        url = f"{BASE_URL}/catalog/count.json"
        response = requests.get(url, auth=self.AUTH)
        total_count = response.json()["count"]
        self.logger.info(f"Total products: {total_count}")
        return total_count

    def get_all_products(self):
        products = []
        
        # Get total count and calculate number of pages needed
        total_count = self.get_product_count()
        per_page = 250
        total_pages = math.ceil(total_count / per_page)
        
        # Fetch each page of products
        for page in range(1, total_pages + 1):
            url = f"{BASE_URL}/catalog.json"
            params = {
                "limit": per_page,
                "page": page
            }
            
            response = requests.get(url, auth=self.AUTH, params=params)
            page_products = response.json()["products"]
            products.extend(page_products)
            
            self.logger.info(f"Fetched page {page}/{total_pages}")
            
        self.logger.info(f"Successfully retrieved {len(products)} products")

        return products

    def get_all_visible_products(self):
        # Get all products
        products = self.get_all_products()
        
        # Filter visible products only
        visible_products = [p for p in products if p["isVisible"]]
        self.logger.info(f"Found {len(visible_products)} visible products")
        
        return visible_products