# lightspeed-custom-google-feed

## What is this?

This is a Python script that will fetch all of your products from your Lightspeed account using the Lightspeed eCom API and save them to a RSS feed following the Google Merchant Center file format.

## Why do I need this?

Lightspeed eCom has poor support for custom feeds. For example, it's not possible to create a feed that includes product variants, or custom fields and specifications. While all the mandatory fields are available in Lightspeed feeds tool itself and this is not required to make Google Merchant Center work, this makes the feed more complete and higher quality, supposedly boosting your relevance in Google therefore your online presence.

## How to use

1. Clone the repository
2. Create a `config.py` file with the following variables:
    - `API_KEY`
    - `API_SECRET`
3. Run `python fetch_products.py`

## Useful links

- [Lightspeed eCom API documentation](https://developers.lightspeedhq.com/ecom/introduction/introduction/)
- [How to create a Lightspeed eCom API key](https://ecom-support.lightspeedhq.com/hc/en-us/articles/1260804034770-Creating-API-keys)
