from datetime import datetime
import logging
import pytz
from jinja2 import Environment, FileSystemLoader
from .config import SHOP

class TemplateEngine:

    def __init__(self):
        self.TEMPLATES_DIR = 'templates'
        self.SHOP = SHOP
        self.logger = logging.getLogger(__name__)
    
    def render(self, template_filename, template_products):
        # Setup Jinja environment
        env = Environment(loader=FileSystemLoader('.'))
        env.filters['cdata'] = self._jinja_cdata
        env.filters['url'] = self._jinja_url
        env.filters['url_image'] = self._jinja_url_image
        env.filters['limit'] = self._jinja_limit
        env.filters['money_float'] = self._jinja_money_float
        template = env.get_template(f"./{self.TEMPLATES_DIR}/{template_filename}")

        # Render template
        output = template.render(
            shop=self.SHOP,
            products=template_products,
            date=self._get_formatted_date()
        )
        
        return output
    
    def _get_formatted_date(self):
        now_utc = datetime.now(pytz.utc)
        now_pacific = now_utc.astimezone(pytz.timezone('US/Pacific'))
        return now_pacific.strftime('%Y-%m-%d %H:%M:%S %Z')

    def _jinja_cdata(self, value):
        if not value:
            return value
        return f"<![CDATA[ {value} ]]>"

    def _jinja_url(self, value):
        #self.logger.debug(f"Template URL filter: Making sure this is a valid URL: {value}")
        if value:
            value = value.replace('http://', 'https://')
            if not value.startswith(self.SHOP['domain']) and not value.startswith(self.SHOP['domain'].replace('://www.', '://')):
                value = f"{self.SHOP['domain']}{value}"
        #self.logger.debug(f"Template URL filter: {value}")
        return value

    def _jinja_url_image(self, value):
        #self.logger.debug(f"Template Img URL filter: Making sure this is a valid image URL: {value}")
        if value:
            value = value.replace('/file.jpg', '/image.jpg')
        #self.logger.debug(f"Template Img URL filter: {value}")
        return value

    def _jinja_limit(self, value, limit):
        #self.logger.debug(f"Template Limit filter: {value} | {limit} | {type(value)}")
        if isinstance(value, dict):
            return dict(list(value.items())[:int(limit)])
        if isinstance(value, list):
            return value[:int(limit)]
        else:
            return value
    
    def _jinja_money_float(self, value):
        #self.logger.debug(f"Template Money Float filter: '{value}'")
        value = str(float(str(value).replace('$', '').replace(',', '')))
        if "." in value and len(value.split(".")[1]) == 1:
            value = f"{value}0"
        #self.logger.debug(f"Template Money Float filter: New value is '{value}'")
        return value
