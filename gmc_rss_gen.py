import requests
import math
from datetime import datetime
from google.cloud import storage
from jinja2 import Environment, FileSystemLoader
import pytz
import json
from config import API_KEY, API_SECRET, BASE_URL, SHOP, CLOUD_STORAGE_BUCKET_NAME

# Authentication for requests
AUTH = (API_KEY, API_SECRET)

TEMPLATE_SHOPPING_ONLINE_INVENTORY_FEED = 'TEMPLATE_gmc_shopping_online_inventory.xml'
SHOPPING_ONLINE_INVENTORY_FEED_FILENAME = 'gmc_shopping_online_inventory_feed.xml'

TEMPLATE_LOCAL_LISTINGS_FEED = 'TEMPLATE_gmc_local_listings.xml'
LOCAL_LISTINGS_FEED_FILENAME = 'gmc_local_listings_feed.xml'

_TEMPLATE_DATA = []

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
    total_pages = 1#math.ceil(total_count / per_page)
    print("### ^^^^ REMOVE THIS ^^^^^")
    
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

def create_feed_from_template(template_filename, products):
    template_products = _prepare_template_data(products)
    return _render_template(template_filename, template_products)

def _prepare_template_data(products):
    # Transform products data for template
    if len(_TEMPLATE_DATA) == 0:
        for product in products:
            try:
                product_variant = next(iter(product["variants"].values()))

                product_stock_level = product_variant["stockLevel"]
                product_url = f"{SHOP['domain']}{product['url']}.html"
                product_images = [image['src'] for image in product.get('images', {}).values()]
                
                product_price = {}
                product_price['price_incl'] = product_variant["priceIncl"]
                product_price['price_old_incl'] = product_variant["oldPriceIncl"]

                product_brand = {}
                if product.get('brand'):
                    product_brand['title'] = product['brand'].get('title', '')
                else:
                    product_brand['title'] = ''

                product_categories = []
                # First collect all categories by depth
                depth1_cats = []
                depth2_cats = []
                depth3_cats = []
                
                product_category_values = []
                if product.get('categories'):
                    product_category_values = product.get('categories').values()
                
                for category in product_category_values:
                    if category['depth'] == 1:
                        depth1_cats.append(category)
                    elif category['depth'] == 2:
                        depth2_cats.append(category)
                    elif category['depth'] == 3:
                        depth3_cats.append(category)
                        
                # Sort each level by sortOrder
                depth1_cats.sort(key=lambda x: x['sortOrder'])
                depth2_cats.sort(key=lambda x: x['sortOrder']) 
                depth3_cats.sort(key=lambda x: x['sortOrder'])
                
                # Build hierarchical structure
                for d1 in depth1_cats:
                    d1_cat = {
                        'title': d1['title'],
                        'subs': []
                    }
                    
                    # Find depth 2 categories under this depth 1
                    for d2 in depth2_cats:
                        # Check if this d2 belongs under d1 by checking if d1's URL is a prefix
                        if d2['url'].startswith(d1['url'] + '/'):
                            d2_cat = {
                                'title': d2['title'],
                                'subs': []
                            }
                            
                            # Find depth 3 categories under this depth 2
                            for d3 in depth3_cats:
                                if d3['url'].startswith(d2['url'] + '/'):
                                    d3_cat = {
                                        'title': d3['title'],
                                        'subs': []
                                    }
                                    d2_cat['subs'].append(d3_cat)
                                break
                            
                            d1_cat['subs'].append(d2_cat)
                    
                    product_categories.append(d1_cat)
                
                print(f"[DEBUG] Product categories for product id {product['id']}: {product_categories} (type: {type(product_categories)})")

                template_data = {
                    'id': product['id'],
                    'stock_level': product_stock_level,
                    'fulltitle': product['fulltitle'],
                    'description': product['description'],
                    'url': product_url,
                    'available': product_stock_level > 0
                }

                if product_images:
                    template_data['images'] = product_images
                
                if product_categories:
                    template_data['categories'] = product_categories
                
                if product_price:
                    template_data['price'] = product_price
                
                if product_brand and product_brand.get('title'):
                    template_data['brand'] = product_brand
                
                if product_variant.get('ean'):
                    template_data['ean'] = product_variant['ean']
                
                if product_variant.get('articleCode'):
                    template_data['code'] = product_variant['articleCode']
                
                if product_variant.get('weight'):
                    template_data['weight'] = product_variant['weight']

                _TEMPLATE_DATA.append(template_data)
            except Exception as e:
                print(f"Error processing product: {product.get('id', 'unknown')}")
                print(f"Product data:")
                print(json.dumps(product, indent=4))
                raise e  # Re-raise the exception to see the full stack trace
        
    return _TEMPLATE_DATA

def _render_template(template_filename, template_products):
    # Setup Jinja environment
    env = Environment(loader=FileSystemLoader('.'))
    env.filters['cdata'] = _jinja_cdata
    env.filters['url'] = _jinja_url
    env.filters['url_image'] = _jinja_url_image
    env.filters['limit'] = _jinja_limit
    env.filters['money_float'] = _jinja_money_float
    template = env.get_template(template_filename)

    # Render template
    output = template.render(
        shop=SHOP,
        products=template_products,
        date=get_formatted_date()
    )
    
    return output

def _jinja_cdata(value):
    if not value:
        return value
    return f"<![CDATA[ {value} ]]>"

def _jinja_url(value):
    #print(f"[DEBUG] Template URL filter: Making sure this is a valid URL: {value}")
    if value:
        value = value.replace('http://', 'https://')
        if not value.startswith(SHOP['domain']):
            value = f"{SHOP['domain']}{value}"
    #print(f"[DEBUG] Template URL filter: {value}")
    return value

def _jinja_url_image(value):
    #print(f"[DEBUG] Template Img URL filter: Making sure this is a valid image URL: {value}")
    if value:
        value = value.replace('/file.jpg', '/image.jpg')
    #print(f"[DEBUG] Template Img URL filter: {value}")
    return value

def _jinja_limit(value, limit):
    print(f"[DEBUG] Template Limit filter: {value} | {limit} | {type(value)}")
    if isinstance(value, dict):
        return dict(list(value.items())[:int(limit)])
    if isinstance(value, list):
        return value[:int(limit)]
    else:
        return value
    
def _jinja_money_float(value):
    #print(f"[DEBUG] Template Money Float filter: '{value}'")
    if not value:
        return value
    value = str(float(str(value).replace('$', '').replace(',', '')))
    if value.endswith('.0'):
        value = f"{value}0"
    #print(f"[DEBUG] Template Money Float filter: New value is '{value}'")
    return value

def refresh_feed_files(cloud=False):
    # Get total products count
    total_count = get_product_count()
    print(f"Total products: {total_count}")
    
    # Get all products page by page
    products = get_all_products()
    print(f"Successfully retrieved {len(products)} products")
    
    # Filter visible products only
    visible_products = [p for p in products if p["isVisible"]]
    print(f"Found {len(visible_products)} visible products")

    # Generate shopping online inventory feed file
    shopping_online_inventory_feed_output = create_feed_from_template(TEMPLATE_SHOPPING_ONLINE_INVENTORY_FEED, visible_products)
    print("Shopping Online Inventory feed file generated successfully")
    
    # Generate local listings feed file
    local_listings_feed_output = create_feed_from_template(TEMPLATE_LOCAL_LISTINGS_FEED, visible_products)
    print("Local Listings feed file generated successfully")

    if cloud:
        # Save to Google Cloud Storage bucket
        storage_client = storage.Client()
        bucket = storage_client.bucket(CLOUD_STORAGE_BUCKET_NAME)
        
        blob = bucket.blob(SHOPPING_ONLINE_INVENTORY_FEED_FILENAME)
        blob.upload_from_string(shopping_online_inventory_feed_output, content_type='application/xml')
        
        blob = bucket.blob(LOCAL_LISTINGS_FEED_FILENAME)
        blob.upload_from_string(local_listings_feed_output, content_type='application/xml')
    else:
        # Save to file
        with open(SHOPPING_ONLINE_INVENTORY_FEED_FILENAME, 'w', encoding='utf-8') as f:
            f.write(shopping_online_inventory_feed_output)
        with open(LOCAL_LISTINGS_FEED_FILENAME, 'w', encoding='utf-8') as f:
            f.write(local_listings_feed_output)

    print(f"Successfully generated feed file: {SHOPPING_ONLINE_INVENTORY_FEED_FILENAME}")
    print(f"Successfully generated feed file: {LOCAL_LISTINGS_FEED_FILENAME}")

def read_feed_file(filename, cloud=False):
    if cloud:
        storage_client = storage.Client()
        bucket = storage_client.bucket(CLOUD_STORAGE_BUCKET_NAME)
        blob = bucket.blob(filename)
        return blob.download_as_string()
    else:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return "<error>Feed file not found. Please generate a feed first.</error>"

if __name__ == "__main__":
    try:
        print("Executing from command line; refreshing feed files")
        refresh_feed_files(cloud=False)
    except Exception as e:
        print(f"Error occurred: {str(e)}")