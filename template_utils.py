from datetime import datetime
import logging
import pytz
from jinja2 import Environment, FileSystemLoader
from config import SHOP

logger = logging.getLogger(__name__)

def render_template(template_filename, template_products):
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
        date=_get_formatted_date()
    )
    
    return output

def _get_formatted_date():
    now_utc = datetime.now(pytz.utc)
    now_pacific = now_utc.astimezone(pytz.timezone('US/Pacific'))
    return now_pacific.strftime('%Y-%m-%d %H:%M:%S %Z')

def _jinja_cdata(value):
    if not value:
        return value
    return f"<![CDATA[ {value} ]]>"

def _jinja_url(value):
    logger.debug(f"[DEBUG] Template URL filter: Making sure this is a valid URL: {value}")
    if value:
        value = value.replace('http://', 'https://')
        if not value.startswith(SHOP['domain']):
            value = f"{SHOP['domain']}{value}"
    logger.debug(f"[DEBUG] Template URL filter: {value}")
    return value

def _jinja_url_image(value):
    logger.debug(f"[DEBUG] Template Img URL filter: Making sure this is a valid image URL: {value}")
    if value:
        value = value.replace('/file.jpg', '/image.jpg')
    logger.debug(f"[DEBUG] Template Img URL filter: {value}")
    return value

def _jinja_limit(value, limit):
    logger.debug(f"[DEBUG] Template Limit filter: {value} | {limit} | {type(value)}")
    if isinstance(value, dict):
        return dict(list(value.items())[:int(limit)])
    if isinstance(value, list):
        return value[:int(limit)]
    else:
        return value
    
def _jinja_money_float(value):
    logger.debug(f"[DEBUG] Template Money Float filter: '{value}'")
    if not value:
        return value
    value = str(float(str(value).replace('$', '').replace(',', '')))
    if value.endswith('.0'):
        value = f"{value}0"
    logger.debug(f"[DEBUG] Template Money Float filter: New value is '{value}'")
    return value
