# lightspeed-custom-google-feed

## What is this?

This is a Python script that will fetch all of your products from your Lightspeed account using the Lightspeed eCom API and save them to a RSS feed following the Google Merchant Center file format.

## Why do I need this?

Lightspeed eCom has poor support for custom feeds. For example, it's not possible to create a feed that includes product variants, or custom fields and specifications. While all the mandatory fields are available in Lightspeed feeds tool itself and this is not required to make Google Merchant Center work, this makes the feed more complete and higher quality, supposedly boosting your relevance in Google therefore improving your online presence.

## How to use (Local environment)

1. Clone the repository
2. Copy `config_TEMPLATE.py` to `config.py` and fill in the API key, secret and other configuration information
3. Run `make feed`

## How to use (Cloud environment)

This is also prepared to run as a Google App Engine application. This is useful because you will want your feed to be accessible as a data source on the web for Google Merchant Center to pick up.

1. Copy `config_TEMPLATE.py` to `config.py` and fill in the API key, secret and other configuration information, including the Google Cloud Storage bucket name
2. Run `make deploy` to push to Google Cloud
3. Hit `https://<your-project-id>.appspot.com/refresh_feed` to generate a new feed file
4. Access the latest feed at `https://<your-project-id>.appspot.com/feed`

You will need to set up a cron job in Google Cloud to run the `refresh_feed` endpoint on a regular basis.

## Useful links

- [Lightspeed eCom API documentation](https://developers.lightspeedhq.com/ecom/introduction/introduction/)
- [How to create a Lightspeed eCom API key](https://ecom-support.lightspeedhq.com/hc/en-us/articles/1260804034770-Creating-API-keys)
