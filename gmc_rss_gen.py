import requests
import math
from google.cloud import storage
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from config import API_KEY, API_SECRET, BASE_URL, SHOP
# Authentication for requests
auth = (API_KEY, API_SECRET)
feed_filename = 'google_shopping_local_listings_feed.xml'

def get_product_count():
    """Get total number of products"""
    url = f"{BASE_URL}/catalog/count.json"
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
        url = f"{BASE_URL}/catalog.json"
        params = {
            "limit": per_page,
            "page": page
        }
        
        response = requests.get(url, auth=auth, params=params)
        page_products = response.json()["products"]
        products.extend(page_products)
        
        print(f"Fetched page {page}/{total_pages}")
        
    return products

def create_feed_from_template(products):
    """Generate and save the Google Shopping feed file from visible products"""
    # Setup Jinja environment
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('google_shopping_local_listings_TEMPLATE.xml')
    
    # Transform products data for template
    template_products = []
    for product in products:
        stock_level = next(iter(product["variants"].values()))["stockLevel"]
        template_products.append({
            'id': product['id'],
            'stock_level': stock_level,
            'available': stock_level > 0
        })
    
    # Render template
    output = template.render(
        shop=SHOP,
        products=template_products,
        date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    return output

def refresh_feed_file(cloud=False):
    # Get total count
    total_count = get_product_count()
    print(f"Total products: {total_count}")
    
    # Get all products
    products = get_all_products()
    print(f"Successfully retrieved {len(products)} products")
    
    # Filter visible products
    visible_products = [p for p in products if p["isVisible"]]
    print(f"Found {len(visible_products)} visible products")

    # Generate feed
    feed_output = create_feed_from_template(visible_products)
    print("Feed file generated successfully")

    # Save to file
    
    if cloud:
        # Save to Google Cloud Storage bucket
        storage_client = storage.Client()
        bucket = storage_client.bucket('peaksbikes-gmc-feeds.appspot.com')
        blob = bucket.blob(feed_filename)
        blob.upload_from_string(feed_output, content_type='application/xml')
    else:
        with open(feed_filename, 'w', encoding='utf-8') as f:
            f.write(feed_output)

    print(f"Successfully generated feed file: {feed_filename}")

def read_feed_file():
    """Read feed file from Google Cloud Storage"""
    storage_client = storage.Client()
    bucket = storage_client.bucket('peaksbikes-gmc-feeds.appspot.com')
    blob = bucket.blob(feed_filename)
    return blob.download_as_string()

def main():
    try:
        refresh_feed_file(cloud=False)
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main()
