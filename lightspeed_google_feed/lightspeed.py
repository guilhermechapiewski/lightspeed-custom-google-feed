import math
import requests
import logging
from .config import API_TYPE, LS_API_KEY, LS_API_SECRET, LS_BASE_URL, ECWID_API_KEY, ECWID_API_SECRET, ECWID_BASE_URL
from .cache import SimpleCache

class LightspeedEcomAPI:
    def __init__(self):
        self.BASE_URL = LS_BASE_URL
        self.AUTH = (LS_API_KEY, LS_API_SECRET)
        self.logger = logging.getLogger(__name__)
        self.cache = SimpleCache()

    def get_product_count(self):
        total_count = self.cache.get(key=f"api-product-count")
        
        if total_count is None:
            url = f"{self.BASE_URL}/catalog/count.json"
            response = requests.get(url, auth=self.AUTH)
            total_count = response.json()["count"]
            
            self.cache.set(key=f"api-product-count", value=total_count, time=30)
        
        self.logger.info(f"Total products: {total_count}")
        return total_count

    def get_all_products(self):
        products = self.cache.get(key=f"api-all-products")
        
        if products is None:
            products = []
            
            # Get total count and calculate number of pages needed
            total_count = self.get_product_count()
            per_page = 250
            total_pages = math.ceil(total_count / per_page)
            
            # Fetch each page of products
            for page in range(1, total_pages + 1):
                url = f"{self.BASE_URL}/catalog.json"
                params = {
                    "limit": per_page,
                    "page": page
                }
                
                response = requests.get(url, auth=self.AUTH, params=params)
                page_products = response.json()["products"]
                products.extend(page_products)
                
                self.logger.info(f"Fetched page {page}/{total_pages}")
            
            self.cache.set(key=f"api-all-products", value=products, time=30)
            
        self.logger.info(f"Successfully retrieved {len(products)} products")

        return products

    def get_all_visible_products(self):
        # Get all products
        products = self.get_all_products()
        
        # Filter visible products only
        visible_products = [p for p in products if p["isVisible"]]
        self.logger.info(f"Found {len(visible_products)} visible products")
        
        return visible_products

class LightspeedEcwidAPI:
    def __init__(self):
        self.BASE_URL = ECWID_BASE_URL
        self.AUTH = (ECWID_API_KEY, ECWID_API_SECRET)
        self.logger = logging.getLogger(__name__)
        self.cache = SimpleCache()
    
    def get_product_count(self):
        total_count = self.cache.get(key=f"api-product-count")
        
        if total_count is None:
            url = f"{self.BASE_URL}/products"
            params = {
                "enabled": "true",
                "visibleInStorefront": "true",
                "offset": "0",
                "limit": "1"
            }
            response = requests.get(url, params=params, headers={"Authorization": f"Bearer {self.AUTH[1]}"})
            total_count = response.json()["total"]
            
            self.cache.set(key=f"api-product-count", value=total_count, time=30)
        
        self.logger.info(f"Total products: {total_count}")
        return total_count

    def get_all_visible_products(self):
        products = self.cache.get(key=f"api-all-products")
        
        if products is None:
            products = []
            
            # Get total count and calculate number of pages needed
            total_count = self.get_product_count()
            per_page = 100
            total_pages = math.ceil(total_count / per_page)
            
            # Fetch each page of products
            for page in range(0, total_pages):
                url = f"{self.BASE_URL}/products"
                params = {
                    "enabled": "true",
                    "visibleInStorefront": "true",
                    "sortBy": "NAME_ASC",
                    "offset": str(page * per_page),
                    "limit": str(per_page)
                }
                
                response = requests.get(url, params=params, headers={"Authorization": f"Bearer {self.AUTH[1]}"})
                page_products = response.json()["items"]
                products.extend(page_products)
                
                self.logger.info(f"Fetched page {page}/{total_pages}")
            
            self.cache.set(key=f"api-all-products", value=products, time=30)
            
        self.logger.info(f"Successfully retrieved {len(products)} products")

        return products

class LightspeedAPI:
    def __init__(self, api_type=None):
        self.logger = logging.getLogger(__name__)
        if api_type is not None:
            self.api_type = api_type
        else:
            self.api_type = API_TYPE

        if self.api_type == "LS":
            self.lightspeed_api = LightspeedEcomAPI()
        elif self.api_type == "ECWID":
            self.lightspeed_api = LightspeedEcwidAPI()
        else:
            raise ValueError(f"Invalid API type: {self.api_type} (must be 'LS' or 'ECWID')")

    def get_all_visible_products(self):
        return self.lightspeed_api.get_all_visible_products()