# lightspeed-custom-google-feed

## What is this?

A Python script + Google App Engine app that will fetch all of your products from your Lightspeed account/website using the Lightspeed eCom API and generate a RSS feed following the Google Merchant Center file format.

## Why do I need this?

Lightspeed eCom has poor support for custom feeds. For example, it's not possible to create a feed that includes product variants, custom fields or specifications. While all the mandatory fields are available in the Lightspeed feeds tool itself and this is not required to make Google Merchant Center work, these additional fields make the RSS feed more complete, with more specifications and higher quality, therefore supposedly boosting your relevance in Google and improving your online presence.

## How to use

### Local environment

1. Clone the repository
2. Copy `config_TEMPLATE.py` to `config.py` and fill in the API key, secret and other configuration information
3. Run `make feed`

### Cloud environment (Google App Engine))

This is also prepared to run as a Google App Engine application. This is useful because you will want your feed to be accessible as a data source on the web for Google Merchant Center to pick up.

1. In addition to all the steps above, fill in the additional configuration information (the Google Cloud Storage bucket name) in `config.py`
2. Run `make deploy` to push to Google Cloud
3. Hit `https://<your-project-id>.appspot.com/refresh_feed` to generate a new feed file
4. Access the latest feed at `https://<your-project-id>.appspot.com/feed`

You will need to set up a [cron job in Google Cloud](https://cloud.google.com/scheduler/docs/schedule-run-cron-job) to run the `refresh_feed` endpoint on a regular basis.

## Lightspeed API 101

Useful links:
- [Lightspeed eCom API documentation](https://developers.lightspeedhq.com/ecom/introduction/introduction/)
- [How to create a Lightspeed eCom API key](https://ecom-support.lightspeedhq.com/hc/en-us/articles/1260804034770-Creating-API-keys)

Two easy ways to test API calls:
1. `curl https://{cluster}/products.json -u {key}:{secret}`
2. `curl https://{key}:{secret}@{cluster}/products.json`

Example: Get the first 250 products:
`curl "https://YOUR_KEY:YOUR_SECRET@api.shoplightspeed.com/us/products.json?limit=250"`

Example: Get a specific product with ID="PRODUCT_ID":
`curl "https://YOUR_KEY:YOUR_SECRET@api.shoplightspeed.com/us/products/PRODUCT_ID.json"`

Example: Get all variants for a product with ID="PRODUCT_ID":
`curl "https://YOUR_KEY:YOUR_SECRET@api.shoplightspeed.com/us/variants.json?product=PRODUCT_ID"`

Example: Get all attributes for a product with ID="PRODUCT_ID":
`curl "https://YOUR_KEY:YOUR_SECRET@api.shoplightspeed.com/us/products/PRODUCT_ID/attributes.json"`

Example: Get all catalog items for a product with ID="PRODUCT_ID":
`curl "https://YOUR_KEY:YOUR_SECRET@api.shoplightspeed.com/us/catalog/PRODUCT_ID.json"`