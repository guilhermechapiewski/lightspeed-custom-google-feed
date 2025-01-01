from google.cloud import storage
import logging
import json
import lightspeed_client
from config import SHOP, CLOUD_STORAGE_BUCKET_NAME
from template_utils import render_template

TEMPLATE_SHOPPING_ONLINE_INVENTORY_FEED = 'TEMPLATE_gmc_shopping_online_inventory.xml'
SHOPPING_ONLINE_INVENTORY_FEED_FILENAME = 'gmc_shopping_online_inventory_feed.xml'
TEMPLATE_LOCAL_LISTINGS_FEED = 'TEMPLATE_gmc_local_listings.xml'
LOCAL_LISTINGS_FEED_FILENAME = 'gmc_local_listings_feed.xml'
_TEMPLATE_DATA = []

logger = logging.getLogger(__name__)

def create_feed_from_template(template_filename, products):
    template_products = prepare_template_data(products)
    return render_template(template_filename, template_products)

def prepare_template_data(products):
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
                
                logger.debug(f"[DEBUG] Product categories for product id {product['id']}: {product_categories} (type: {type(product_categories)})")

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
                logger.error(f"Error processing product: {product.get('id', 'unknown')}")
                logger.error(f"Product data:")
                logger.error(json.dumps(product, indent=4))
                raise e  # Re-raise the exception to see the full stack trace
        
    return _TEMPLATE_DATA

def refresh_feed_files(cloud=False):
    # Get products from Lightspeed API
    products = lightspeed_client.get_all_visible_products()
    
    # Generate shopping online inventory feed file
    shopping_online_inventory_feed_output = create_feed_from_template(TEMPLATE_SHOPPING_ONLINE_INVENTORY_FEED, products)
    logger.info("Shopping Online Inventory feed file generated successfully")
    
    # Generate local listings feed file
    local_listings_feed_output = create_feed_from_template(TEMPLATE_LOCAL_LISTINGS_FEED, products)
    logger.info("Local Listings feed file generated successfully")

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

    logger.info(f"Successfully generated feed file: {SHOPPING_ONLINE_INVENTORY_FEED_FILENAME}")
    logger.info(f"Successfully generated feed file: {LOCAL_LISTINGS_FEED_FILENAME}")

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
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s][%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    try:
        logger.info("Executing from command line; refreshing feed files")
        refresh_feed_files(cloud=False)
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise e