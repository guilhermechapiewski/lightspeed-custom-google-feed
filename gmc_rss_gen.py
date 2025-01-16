import logging
import json
from lightspeed_google_feed import lightspeed, storage, template_engine
from config import SHOP

TEMPLATE_SHOPPING_ONLINE_INVENTORY_FEED = 'TEMPLATE_gmc_shopping_online_inventory.xml'
SHOPPING_ONLINE_INVENTORY_FEED_FILENAME = 'gmc_shopping_online_inventory_feed.xml'
TEMPLATE_LOCAL_LISTINGS_FEED = 'TEMPLATE_gmc_local_listings.xml'
LOCAL_LISTINGS_FEED_FILENAME = 'gmc_local_listings_feed.xml'

_TEMPLATE_DATA = [] # Global variable to store template data avoiding multiple API calls for different feeds

logger = logging.getLogger(__name__)

def refresh_feed_files(cloud=False):
    # Get products from Lightspeed API
    products = lightspeed.get_all_visible_products()

    # Prepare template data/context for feed generation
    products_for_template = prepare_template_data(products)
    
    # Generate (render) feeds from templates
    shopping_online_inventory_feed_output = template_engine.render(TEMPLATE_SHOPPING_ONLINE_INVENTORY_FEED, products_for_template)
    local_listings_feed_output = template_engine.render(TEMPLATE_LOCAL_LISTINGS_FEED, products_for_template)

    # Save feeds to files or Google Cloud Storage depending on running environment
    storage.save_file(SHOPPING_ONLINE_INVENTORY_FEED_FILENAME, shopping_online_inventory_feed_output, cloud)
    storage.save_file(LOCAL_LISTINGS_FEED_FILENAME, local_listings_feed_output, cloud)

def read_feed_file(filename, cloud=False):
    return storage.read_file(filename, cloud)

def prepare_template_data(products):
    # Transform products data for template
    if len(_TEMPLATE_DATA) == 0:
        for product in products:
            try:
                product_variant = min(product["variants"].values(), key=lambda x: x['sortOrder'])
                product_stock_level = product_variant["stockLevel"]
                product_available = product_stock_level > 0 or product_variant["stockTracking"] == "disabled"
                product_url = f"{SHOP['domain']}{product['url']}.html"
                              
                product_images = None
                if product.get('images') and len(product.get('images')) > 0:
                    product_images = [image['src'] for image in sorted(product.get('images', {}).values(), key=lambda x: x['sortOrder'])]
                
                product_price = {}
                product_price['price_incl'] = product_variant["priceIncl"]
                product_price['price_old_incl'] = product_variant["oldPriceIncl"]

                product_brand = {}
                if product.get('brand'):
                    product_brand['title'] = product['brand'].get('title', '')
                else:
                    product_brand['title'] = ''

                product_fulltitle = product['fulltitle'].strip()
                if not product_fulltitle.lower().startswith(product_brand['title'].lower()):
                    product_fulltitle = f"{product_brand['title']} {product['fulltitle']}".strip()

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
                    'fulltitle': product_fulltitle,
                    'description': product['description'],
                    'url': product_url,
                    'available': product_available
                }

                if product_images and len(product_images) > 0:
                    template_data['images'] = product_images
                
                if product_categories and len(product_categories) > 0:
                    template_data['categories'] = product_categories
                
                if product_price:
                    template_data['price'] = product_price
                
                if product_brand and product_brand.get('title') and len(product_brand.get('title')) > 0:
                    template_data['brand'] = product_brand
                
                if product_variant.get('ean') and len(product_variant.get('ean')) > 0:
                    template_data['ean'] = product_variant['ean']
                
                if product_variant.get('articleCode') and len(product_variant.get('articleCode')) > 0:
                    template_data['code'] = product_variant['articleCode']
                
                if product_variant.get('weight'):
                    template_data['weight'] = product_variant['weight']
                else:
                    template_data['weight'] = 0

                _TEMPLATE_DATA.append(template_data)
            except Exception as e:
                logger.error(f"Error processing product: {product.get('id', 'unknown')}")
                logger.error(f"Product data:")
                logger.error(json.dumps(product, indent=4))
                raise e  # Re-raise the exception to see the full stack trace
        
    return _TEMPLATE_DATA

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    try:
        logger.info("Executing from command line; refreshing feed files")
        refresh_feed_files(cloud=False)
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise e