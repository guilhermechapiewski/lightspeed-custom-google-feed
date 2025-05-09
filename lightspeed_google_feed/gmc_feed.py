import re
import logging
import json
from . import lightspeed, storage, template_engine
from .config import SHOP, API_TYPE

class GMCFeedGenerator:
    def __init__(self, cloud=False, api_type=None):
        self.logger = logging.getLogger(__name__)
        self.TEMPLATE_SHOPPING_ONLINE_INVENTORY_FEED = 'TEMPLATE_gmc_shopping_online_inventory.xml'
        self.SHOPPING_ONLINE_INVENTORY_FEED_FILENAME = 'gmc_shopping_online_inventory_feed.xml'
        self.TEMPLATE_LOCAL_LISTINGS_FEED = 'TEMPLATE_gmc_local_listings.xml'
        self.LOCAL_LISTINGS_FEED_FILENAME = 'gmc_local_listings_feed.xml'
        self.lightspeed_api = lightspeed.LightspeedAPI(api_type=api_type)
        self.storage = storage.Storage(cloud)
        self.template_engine = template_engine.TemplateEngine()
        self.template_data = GMCFeedTemplateData(api_type=api_type)

    def refresh_feed_files(self):
        # Get products from Lightspeed API
        products = self.lightspeed_api.get_all_visible_products()

        # Prepare template data/context for feed generation
        products_for_template = self.template_data.prepare_template_data(products)
        
        # Generate (render) feeds from templates
        shopping_online_inventory_feed_output = self.template_engine.render(self.TEMPLATE_SHOPPING_ONLINE_INVENTORY_FEED, products_for_template)
        local_listings_feed_output = self.template_engine.render(self.TEMPLATE_LOCAL_LISTINGS_FEED, products_for_template)

        # Save feeds to files
        self.storage.save_file(self.SHOPPING_ONLINE_INVENTORY_FEED_FILENAME, shopping_online_inventory_feed_output)
        self.storage.save_file(self.LOCAL_LISTINGS_FEED_FILENAME, local_listings_feed_output)
    
    def read_feed_file(self, filename):
        return self.storage.read_file(filename)

class GMCFeedTemplateData:
    def __init__(self, api_type=None):
        self.logger = logging.getLogger(__name__)

        if api_type is not None:
            self.api_type = api_type
        else:
            self.api_type = API_TYPE

        if self.api_type == "LS":
            self.template_data_provider = GMCFeedTemplateDataFromLightspeed()
        elif self.api_type == "ECWID":
            self.template_data_provider = GMCFeedTemplateDataFromEcwid()
        else:
            raise ValueError(f"Invalid API type: {self.api_type} (must be 'LS' or 'ECWID')")
    
    def prepare_template_data(self, products):
        return self.template_data_provider.prepare_template_data(products)

class GMCFeedTemplateDataFromLightspeed:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def prepare_template_data(self, products):
        # Transform products data for template
        template_data = []
        
        for product in products:
            self.logger.debug(f"Product: {product['id']} has {len(product['variants'])} variants")
            for product_variant in product["variants"].values():
                try:
                    # for each combination of product and variant, create a GMCProduct object
                    gmc_product = GMCFeedProductFromLightspeed(product['id'], product_variant['id'])
                    gmc_product.set_url_slug(product['url'])
                    gmc_product.set_stock_level(product_variant.get("stockLevel"))
                    gmc_product.set_stock_tracking(product_variant.get("stockTracking"))
                    gmc_product.set_ean(product_variant.get('ean'))
                    gmc_product.set_code(product_variant.get('articleCode'))
                    gmc_product.set_weight(product_variant.get('weight'))
                    gmc_product.set_price(product_variant.get("priceIncl"))
                    gmc_product.set_old_price(product_variant.get("oldPriceIncl"))
                    gmc_product.set_description(product['description'])
                    gmc_product.set_title(product['fulltitle'])
                    gmc_product.set_variant_title(product_variant.get('title'))
                    gmc_product.set_categories(product.get('categories'))

                    if product.get('images') and len(product.get('images')) > 0:
                        gmc_product.add_images([image['src'] for image in sorted(product.get('images', {}).values(), key=lambda x: x['sortOrder'])])
                    
                    if product.get('brand'):
                        gmc_product.set_brand_title(product['brand'].get('title', ''))

                    # add the template data from the GMCProduct
                    template_data.append(gmc_product.get_template_data())
                except Exception as e:
                    self.logger.error(f"Error processing product: {product.get('id', 'unknown')}")
                    self.logger.error(f"Product data:")
                    self.logger.error(json.dumps(product, indent=4))
                    raise e  # Re-raise the exception to see the full stack trace
        
        return template_data

class GMCFeedTemplateDataFromEcwid:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def prepare_template_data(self, products):
        # Transform products data for template
        template_data = []
        
        for product in products:
            self.logger.debug(f"Product: {product.get('id')} has {len(product.get('combinations'))} variants")
            for product_variant in product.get("combinations"):
                try:
                    # for each combination of product and variant, create a GMCProduct object
                    gmc_product = GMCFeedProductFromEcwid(product.get('id'), product_variant.get('id'))
                    gmc_product.set_url_slug(product.get('autogeneratedSlug'))
                    gmc_product.set_url(product.get('url'))
                    gmc_product.set_stock_level(product_variant.get("quantity"))
                    gmc_product.set_stock_tracking(product_variant.get("outOfStockVisibilityBehaviour"))
                    gmc_product.set_ean(product_variant.get('ean', ''))
                    gmc_product.set_code(product_variant.get('sku'))
                    gmc_product.set_weight(product.get('weight'))
                    gmc_product.set_price(product_variant.get("defaultDisplayedPrice"))
                    gmc_product.set_old_price(product_variant.get("compareToPrice"))
                    gmc_product.set_description(product.get('description'))
                    gmc_product.set_title(product.get('name'))
                    gmc_product.set_variant_attributes(product_variant.get('options'))
                    gmc_product.set_categories(product.get('categories'))

                    if product.get('media') and product.get('media').get('images') and len(product.get('media').get('images')) > 0:
                        gmc_product.add_images([image['imageOriginalUrl'] for image in sorted(product.get('media').get('images'), key=lambda x: x['orderBy'])])
                    
                    if product.get('attributes'):
                        for attribute in product.get('attributes'):
                            if attribute.get('name') == 'Brand':
                                gmc_product.set_brand_title(attribute.get('value'))

                    # add the template data from the GMCProduct
                    template_data.append(gmc_product.get_template_data())
                except Exception as e:
                    self.logger.error(f"Error processing product: {product.get('id', 'unknown')}")
                    self.logger.error(f"Product data:")
                    self.logger.error(json.dumps(product, indent=4))
                    raise e  # Re-raise the exception to see the full stack trace
        
        return template_data
    
class GMCFeedProduct:
    def __init__(self, id, variant_id):
        self.id = id
        self.variant_id = variant_id
        self.images = []
        self.stock_level = 0
        self.stock_tracking = ""
        self.url_slug = ""
        self.price = 0
        self.old_price = 0
        self.title = ""
        self.brand_title = ""
        self.variant_title = ""
        self.variant_values = []
        self.variant_attributes = {}
        self.ean = ""
        self.code = ""
        self.description = ""
        self.categories = {}
        # default weight for products without weight
        # it seems that GMC expects a weight for all products and 0 is not accepted
        # 25g is ~ 0.1oz, which is the minimum weight accepted by UPS ground
        self.weight = 25

    def set_stock_level(self, stock_level):
        self.stock_level = stock_level
    
    def set_stock_tracking(self, stock_tracking):
        self.stock_tracking = stock_tracking
    
    def set_url_slug(self, url_slug):
        self.url_slug = url_slug
    
    def get_url(self):
        return f"{SHOP['domain']}{self.url_slug}.html"
    
    def get_images(self):
        return self.images
    
    def add_image(self, image):
        self.images.append(image)

    def add_images(self, images):
        self.images.extend(images)
    
    def set_price(self, price):
        self.price = price
    
    def set_old_price(self, old_price):
        self.old_price = old_price

    def set_brand_title(self, brand_title):
        self.brand_title = brand_title
    
    def get_brand(self):
        if self.brand_title:
            return {
                'title': self.brand_title
            }
        else:
            return None
    
    def set_ean(self, ean):
        self.ean = ean
    
    def set_code(self, code):
        self.code = code
    
    def set_weight(self, weight):
        if weight and weight > 0:
            self.weight = weight

    def set_title(self, title):
        self.title = title.strip()
    
    def set_description(self, description):
        self.description = description
    
    def get_fulltitle(self):
        fulltitle = self.title
        
        # convert to title case if all uppercase
        if fulltitle.isupper():
            fulltitle = fulltitle.title()
        
        # add brand title to fulltitle if not already present
        if not fulltitle.lower().startswith(self.brand_title.lower()):
            fulltitle = f"{self.brand_title} {fulltitle}".strip()
        
        # add variant values to fulltitle (which are the product specifications)
        if len(self.variant_values) > 0:
            fulltitle = f"{fulltitle} ({', '.join(self.variant_values)})"

        return fulltitle
    
    def get_color(self):
        return self.variant_attributes.get("Color", "").lower()
    
    def get_size(self):
        size = self.variant_attributes.get("Size", "").lower()
        
        # sizes are expected to be in the format XXS, XS, S, M, L, XL, 2XL, 3XL, 4XL, 5XL, 6XL
        # see https://support.google.com/merchants/answer/6324492?sjid=8143513646685484049-NC
        if size.startswith("2 xs"):
            size = "XXS"
        elif size.startswith("extra small") or size.startswith("x small"):
            size = "XS"
        elif size.startswith("small") or size.startswith("youth small"):
            size = "S"
        elif size.startswith("medium") or size.startswith("youth medium"):
            size = "M"
        elif size.startswith("large") or size.startswith("youth large"):
            size = "L"
        elif size.startswith("extra large") or size.startswith("x large") or size.startswith("youth extra large") or size.startswith("youth xl"):
            size = "XL"
        elif size.startswith("2 xl"):
            size = "2XL"
        elif size.startswith("3 xl"):
            size = "3XL"
        elif size.startswith("4 xl"):
            size = "4XL"
        elif size.startswith("5 xl"):
            size = "5XL"
        elif size.startswith("6 xl"):
            size = "6XL"
        else:
            size = self.variant_attributes.get("Size", "")
            
        return size

    def get_gender(self):
        # default gender is "Unisex" for all products
        gender = self.variant_attributes.get("Gender", "Unisex").lower()
        
        # find genders in product title and translate to attribute in the format GMC expects
        # see https://support.google.com/merchants/answer/6324479?sjid=8143513646685484049-NC
        ft = self.get_fulltitle().lower()
        if ft.find(" men ") > -1 or ft.find(" men's ") > -1 or ft.endswith(" men") or ft.endswith(" men's"):
            gender = "male"
        elif ft.find(" women ") > -1 or ft.find(" women's ") > -1 or ft.endswith(" women") or ft.endswith(" women's"):
            gender = "female"
        
        # also check description
        description_words = self.description.lower().split()
        if "men" in description_words or "men's" in description_words:
            gender = "male"
        elif "women" in description_words or "women's" in description_words:
            gender = "female"
        
        return gender
    
    def get_age_group(self):
        # default age group is "Adult" for all products
        age_group = self.variant_attributes.get("Age Group", "Adult").lower()
        
        # while products are typically denominated as "youth", GMC expects "kids"
        # see https://support.google.com/merchants/answer/6324463?sjid=8143513646685484049-NC
        title_words = self.get_fulltitle().lower().split()
        description_words = self.description.lower().split()
        if "youth" in title_words or "youth" in description_words:
            age_group = "kids"
        
        return age_group

    def set_categories(self, categories):
        if categories:
            self.categories = categories
    
    def is_available(self):
        return self.stock_level > 0
    
    def get_pickup_SLA(self):
        # pickup SLA must be in the format accepted by GMC
        # see https://support.google.com/merchants/answer/14635400?hl=en&ref_topic=15161225&sjid=7328843357097372161-NC
        if self.stock_level > 0:
            return "same_day"
        else:
            return "multi-week"

    def get_template_data(self):
        ''' Encapsulates how to create the template data from a product object '''
        return {
            'id': f"{self.id}_{self.variant_id}",
            'item_group_id': self.id,
            'ean': self.ean,
            'code': self.code,
            'weight': self.weight,
            'stock_level': self.stock_level,
            'images': self.images,
            'price': {
                'price_incl': self.price,
                'price_old_incl': self.old_price
            },
            'brand': self.get_brand(),
            'url': self.get_url(),
            'available': self.is_available(),
            'fulltitle': self.get_fulltitle(),
            'description': self.description,
            'color': self.get_color(),
            'size': self.get_size(),
            'gender': self.get_gender(),
            'age_group': self.get_age_group(),
            'categories': self.get_categories(),
            'pickup_SLA': self.get_pickup_SLA()
        }

class GMCFeedProductFromLightspeed(GMCFeedProduct):
    def __init__(self, id, variant_id):
        super().__init__(id, variant_id)
        self.logger = logging.getLogger(__name__)
    
    def set_variant_title(self, variant_title):
        self.variant_values = []
        self.variant_attributes = {}
        self.variant_title = variant_title.strip()
        if self.variant_title.lower() != "default":
            # string format is: "Color: Graphite Grey","Size: 2 XL"
            # in some cases, the variant title string is not formatted correctly (example: "Oil change kit")
            # extract values after colons, strip quotes and join with commas
            for p in self.variant_title.split(','):
                try:
                    key = p.split(':')[0].replace('"', '').strip()
                    value = p.split(':')[1].replace('"', '').strip()
                    self.variant_values.append(value)
                    self.variant_attributes[key] = value
                except IndexError:
                    # If no colon found, use the whole string
                    value = p.replace('"', '').strip()
                    self.variant_values.append(value)
    
    def is_available(self):
        return self.stock_level > 0 or self.stock_tracking == "disabled" or self.stock_tracking == "indicator"

    def get_gender(self):
        gender = super().get_gender()
        
        if gender is None or gender == "" or gender == "unisex":
            # also check if any category is "men" or "women"
            if len(self.categories) > 0:
                for category in self.categories.values():
                    if category.get('title', '').lower() == "men":
                        gender = "male"
                        break
                    elif category.get('title', '').lower() == "women":
                        gender = "female"
                        break

        return gender
    
    def get_categories(self):
        # build the list of product categories, translating from the Lightspeed 
        # category structure to what GMC expects
        product_categories = []
        # first, collect all categories by depth
        depth1_cats = []
        depth2_cats = []
        depth3_cats = []
        
        product_category_values = []
        if self.categories:
            product_category_values = self.categories.values()
        
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
        
        self.logger.debug(f"Product categories for product id {self.id}_{self.variant_id}: {product_categories} (type: {type(product_categories)})")
        return product_categories

class GMCFeedProductFromEcwid(GMCFeedProduct):
    def __init__(self, id, variant_id):
        super().__init__(id, variant_id)
        self.logger = logging.getLogger(__name__)
    
    def set_description(self, description):
        # Remove any HTML tags from description
        if description and isinstance(description, str):
            self.description = re.sub(r'<[^>]+>', '', description)
        else:
            self.description = ""
    
    def is_available(self):
        return self.stock_level > 0 or self.stock_tracking == "ALLOW_PREORDER"

    def set_url(self, url):
        self.url = url

    def get_url(self):
        return self.url
    
    def set_variant_attributes(self, variant_attributes):
        self.variant_attributes = {}
        self.variant_values = []
        for attribute in variant_attributes:
            # Gender and Age Group are not present in any of the products I've seen so far
            # but they are present in the Ecwid API documentation
            # https://docs.ecwid.com/api-reference/rest-api/products/get-product#attributes
            if attribute.get('name') in ['Color', 'Size', 'Gender', 'Age Group']:
                self.variant_attributes[attribute.get('name')] = attribute.get('value')
                self.variant_values.append(attribute.get('value'))
    
    def get_categories(self):
        # build the list of product categories, translating from the Lightspeed 
        # category structure to what GMC expects
        last_product_category = None
        for category in reversed(self.categories):
            if category.get('enabled') == True:
                last_product_category = {
                    'title': category.get('name'),
                    'subs': [last_product_category]
                }

        product_categories = [last_product_category]
        self.logger.debug(f"Product categories for product id {self.id}_{self.variant_id}: {product_categories} (type: {type(product_categories)})")
        return product_categories

    def check_gender_in_category(self, category):
        if category:
            if category.get('title', '').lower() == "men":
                return "male"
            elif category.get('title', '').lower() == "women":
                return "female"
            
            # Check subcategories recursively
            for subcat in category.get('subs', []):
                gender = self.check_gender_in_category(subcat)
                if gender is not None:
                    return gender
        return None

    def get_gender(self):
        gender = super().get_gender()
        
        if gender is None or gender == "" or gender == "unisex":
            # also check if any category is "men" or "women"
            categories = self.get_categories()
            if categories and len(categories) > 0:
                for category in categories:
                    category_gender = self.check_gender_in_category(category)
                    if category_gender is not None:
                        gender = category_gender
                        break
            
        return gender