# Set API_TYPE to "LS" for Lightspeed C-Series or "ECWID" for Ecwid/E-Series
API_TYPE = "LS"
#API_TYPE = "ECWID"

# Lightspeed API config
LS_BASE_URL = "https://api.shoplightspeed.com/us"
LS_API_KEY = "your_api_key_here"
LS_API_SECRET = "your_api_secret_here"

# Ecwid API config
ECWID_BASE_URL = "https://app.ecwid.com/api/v3/YOUR_ECWID_STORE_ID"
ECWID_API_KEY = "your_ecwid_api_key_here"
ECWID_API_SECRET = "your_ecwid_api_secret_here"

# Google Cloud Storage config
CLOUD_STORAGE_BUCKET_NAME = 'your_bucket_name_here'

# Shop info (for RSS feed metadata)
SHOP = {
    'title': 'Your Store Name',
    'domain': 'https://yourstore.com',
    'description': 'Your Store Description',
    'store_code': 'your_store_code_here',
    'country': 'US',
    'currency': 'USD'
}