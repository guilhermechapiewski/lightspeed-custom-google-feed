import requests
import math
from datetime import datetime
from google.cloud import storage
from jinja2 import Environment, FileSystemLoader
import pytz
from config import API_KEY, API_SECRET, BASE_URL, SHOP, CLOUD_STORAGE_BUCKET_NAME

# Authentication for requests
AUTH = (API_KEY, API_SECRET)

TEMPLATE_LOCAL_LISTINGS_FEED = 'TEMPLATE_gmc_local_listings.xml'
LOCAL_LISTINGS_FEED_FILENAME = 'gmc_local_listings_feed.xml'

def get_formatted_date():
    now_utc = datetime.now(pytz.utc)
    now_pacific = now_utc.astimezone(pytz.timezone('US/Pacific'))
    return now_pacific.strftime('%Y-%m-%d %H:%M:%S %Z')
    
def get_product_count():
    """Get total number of products"""
    url = f"{BASE_URL}/catalog/count.json"
    response = requests.get(url, auth=AUTH)
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
        
        response = requests.get(url, auth=AUTH, params=params)
        page_products = response.json()["products"]
        products.extend(page_products)
        
        print(f"Fetched page {page}/{total_pages}")
        
    return products

def create_feed_from_template(products):
    # Transform products data for template
    template_products = []
    for product in products:
        stock_level = next(iter(product["variants"].values()))["stockLevel"]
        template_products.append({
            'id': product['id'],
            'stock_level': stock_level,
            'available': stock_level > 0
        })
    
    # Setup Jinja environment
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(TEMPLATE_LOCAL_LISTINGS_FEED)

    # Render template
    output = template.render(
        shop=SHOP,
        products=template_products,
        date=get_formatted_date()
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
        bucket = storage_client.bucket(CLOUD_STORAGE_BUCKET_NAME)
        blob = bucket.blob(LOCAL_LISTINGS_FEED_FILENAME)
        blob.upload_from_string(feed_output, content_type='application/xml')
    else:
        with open(LOCAL_LISTINGS_FEED_FILENAME, 'w', encoding='utf-8') as f:
            f.write(feed_output)

    print(f"Successfully generated feed file: {LOCAL_LISTINGS_FEED_FILENAME}")

def read_feed_file(cloud=False):
    if cloud:
        storage_client = storage.Client()
        bucket = storage_client.bucket(CLOUD_STORAGE_BUCKET_NAME)
        blob = bucket.blob(LOCAL_LISTINGS_FEED_FILENAME)
        return blob.download_as_string()
    else:
        try:
            with open(LOCAL_LISTINGS_FEED_FILENAME, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return "<error>Feed file not found. Please generate a feed first.</error>"

if __name__ == "__main__":
    try:
        refresh_feed_file(cloud=False)
    except Exception as e:
        print(f"Error occurred: {str(e)}")