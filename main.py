import os
import flask
import gmc_rss_gen

app = flask.Flask(__name__)

RUNNING_ON_CLOUD = False
if os.getenv('GAE_ENV', '').startswith('standard'):
    RUNNING_ON_CLOUD = True
elif os.getenv('GAE_ENV', '').startswith('flex'):
    RUNNING_ON_CLOUD = True

@app.route("/")
def root():
    return '''
Google Merchant Center Feed Generator for Lightspeed eCom<br>
<a href="https://github.com/guilhermechapiewski/lightspeed-custom-google-feed#lightspeed-custom-google-feed">Documentation</a> | 
<a href="/shopping_online_inventory_feed">Shopping Online Inventory Feed</a> | 
<a href="/local_listings_feed">Local Listings Feed</a> | 
<a href="/refresh_feeds">Refresh feeds</a>
'''

@app.route("/refresh_feeds")
def refresh_feeds():
    gmc_rss_gen.refresh_feed_files(cloud=RUNNING_ON_CLOUD)
    return "New RSS feed files are ready.<br><a href='/'>Back to home</a>"

@app.route("/shopping_online_inventory_feed")
def shopping_online_inventory_feed():
    return gmc_rss_gen.read_feed_file(gmc_rss_gen.SHOPPING_ONLINE_INVENTORY_FEED_FILENAME, cloud=RUNNING_ON_CLOUD), {'Content-Type': 'application/xml'}

@app.route("/local_listings_feed")
def local_listings_feed():
    return gmc_rss_gen.read_feed_file(gmc_rss_gen.LOCAL_LISTINGS_FEED_FILENAME, cloud=RUNNING_ON_CLOUD), {'Content-Type': 'application/xml'}

if __name__ == "__main__":
    # Run locally if the script is invoked directly
    app.run(host="127.0.0.1", port=8080, debug=True)