# lightspeed-custom-google-feed

## What is this?

A Python script + Google App Engine app that fetches all products from your Lightspeed eCommerce (C-Series) instance using the [Lightspeed eCom API](https://developers.lightspeedhq.com/ecom/introduction/introduction/) and generates RSS feeds following the [Google Merchant Center Local Listings](https://support.google.com/merchants/answer/14779112?hl=en) and [Google Merchant Center Online Inventory](https://support.google.com/merchants/answer/7052112?hl=en) specifications.

Two feeds are generated/supported:
1. *Google Shopping online inventory*: all products available for sale in your ecommerce website/catalog.
2. *Google Local Listings and Ads*: all products available in the physical "store shelf".

## Why do I need this?

These feeds are required to make Google Merchant Center work properly for both your online store and your physical store/local listings in Google Shopping.

While Lightspeed eCom has a custom feeds tool, it has limited functionality. For example, it's not possible to create a feed that includes product variants, custom fields or specifications. While all the minimum necessary fields are available in the Lightspeed custom feeds tool, the additional fields make the RSS feed more complete, with more specifications and higher quality, boosting your relevance in Google Ads/Search results and Shopping, and improving your online presence.

As much as possible the templates used by this app are compatible with Lightspeed eCom - if desired, you should be able to copy and paste any custom feeds of your liking from there to here (although it's not necessary).

## How to use

### Command line usage

1. Clone the repository
2. Copy `lightspeed_google_feed/config_TEMPLATE.py` to `lightspeed_google_feed/config.py` and fill in the API key, secret and other configuration information
3. Run `make install_requirements` to install the required dependencies
4. Finally, run `make feed` to generate the feed files in the project root directory

### Web application (run locally or in the cloud/Google App Engine)

This project is also prepared to run as a [Google App Engine](https://cloud.google.com/appengine) application. This is useful because you will want your feed to be accessible as a data source on the web for Google Merchant Center to pick it up (although you can also run the command line tool above to generate the feed files and then upload them to Google Merchant Center manually). To set it up:

1. In addition to all the steps above, fill in the additional configuration information required for cloud usage(the Google Cloud Storage bucket name) in `config.py`
2. Run `make run` to execute the App Engine application locally or `make deploy` to push it to Google Cloud
3. Go to `http://localhost:8080/` or `https://<your-project-id>.appspot.com/`
4. From there you will find the URLs to access both feeds and refresh (regenerate) the feeds (which will update and override the latest feed file)

#### Setup a Google App Engine cron job to refresh feeds periodically

To refresh the feeds periodically, set up a [cron job in Google Cloud](https://cloud.google.com/scheduler/docs/schedule-run-cron-job) to call the `https://<your-project-id>.appspot.com/refresh_feeds` endpoint on a regular basis:

1. Configure the provided `cron.yaml` file following the instructions in the [Google Cloud Scheduler documentation](https://cloud.google.com/scheduler/docs/schedule-run-cron-job) (or, if you make no changes, it will run daily at 00:00 Pacific time)
2. Run `make deploy_cron`
3. Visit the [Google Cloud Scheduler](https://console.cloud.google.com/cloudscheduler) to see the configured cron job
4. You can also run `make remote_refresh_feeds` to refresh the feeds on the remote server from your local command line

## Lightspeed API 101

Useful links:
- [Lightspeed eCom API documentation](https://developers.lightspeedhq.com/ecom/introduction/resources/)
- [How to create a Lightspeed eCom API key](https://ecom-support.lightspeedhq.com/hc/en-us/articles/1260804034770-Creating-API-keys)

Two easy ways to test API calls:
1. `curl https://{cluster}/products.json -u {key}:{secret}`
2. `curl https://{key}:{secret}@{cluster}/products.json`

Example: Get the first 250 products:
* `curl "https://YOUR_KEY:YOUR_SECRET@api.shoplightspeed.com/us/products.json?limit=250"`

Example: Get a specific product with ID=`PRODUCT_ID`:
* `curl "https://YOUR_KEY:YOUR_SECRET@api.shoplightspeed.com/us/products/PRODUCT_ID.json"`

Example: Get all variants for a product with ID=`PRODUCT_ID`:
* `curl "https://YOUR_KEY:YOUR_SECRET@api.shoplightspeed.com/us/variants.json?product=PRODUCT_ID"`

Example: Get all attributes for a product with ID=`PRODUCT_ID`:
* `curl "https://YOUR_KEY:YOUR_SECRET@api.shoplightspeed.com/us/products/PRODUCT_ID/attributes.json"`

Example: Get all catalog items for a product with ID=`PRODUCT_ID`:
* `curl "https://YOUR_KEY:YOUR_SECRET@api.shoplightspeed.com/us/catalog/PRODUCT_ID.json"`