import requests
import json
import math

# API credentials and base URL
# Import API credentials from config file that is gitignored
from config import API_KEY, API_SECRET
BASE_URL = "https://api.shoplightspeed.com/us"

# Authentication for requests
auth = (API_KEY, API_SECRET)

def get_product_count():
    """Get total number of products"""
    url = f"{BASE_URL}/products/count.json"
    response = requests.get(url, auth=auth)
    return response.json()["count"]

def get_all_products():
    """Get all products across all pages"""
    products = []
    
    # Get total count and calculate number of pages needed
    total_count = get_product_count()
    per_page = 250
    total_pages = math.ceil(total_count / per_page)
    
    # Fetch each page of products
    for page in range(1, total_pages + 1):
        url = f"{BASE_URL}/products.json"
        params = {
            "limit": per_page,
            "page": page
        }
        
        response = requests.get(url, auth=auth, params=params)
        page_products = response.json()["products"]
        products.extend(page_products)
        
        print(f"Fetched page {page}/{total_pages}")
        
    return products

def main():
    try:
        # Get total count
        total_count = get_product_count()
        print(f"Total products: {total_count}")
        
        # Get all products
        products = get_all_products()
        print(f"Successfully retrieved {len(products)} products")
        
        # Save to file
        with open("products.json", "w") as f:
            json.dump({"products": products}, f, indent=4)
            
        print("Products saved to products.json")
        # Filter visible products
        visible_products = [p for p in products if p["isVisible"]]
        print(f"Found {len(visible_products)} visible products")
        
        # Save filtered products
        with open("visible_products.json", "w") as f:
            json.dump({"products": visible_products}, f, indent=4)
            
        print("Visible products saved to visible_products.json")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main()
