import sys
import logging
import os
import flask
from lightspeed_google_feed.gmc_feed import GMCFeedGenerator

try:
    import version #auto-generated by "make deploy"
except ImportError:
    version = type('Version', (), {'git_commit': '', 'deploy_timestamp': 'N/A'})()

IS_RUNNING_ON_CLOUD = False
if os.getenv('GAE_ENV', '').startswith('standard') or os.getenv('GAE_ENV', '').startswith('flex'):
    IS_RUNNING_ON_CLOUD = True

app = flask.Flask(__name__)
feed_gen = GMCFeedGenerator(cloud=IS_RUNNING_ON_CLOUD)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

@app.route("/")
def root():
    return f'''
Google Merchant Center Feed Generator for Lightspeed<br>
<a href="https://github.com/guilhermechapiewski/lightspeed-custom-google-feed#lightspeed-custom-google-feed">Documentation</a> | 
<a href="/shopping_online_inventory_feed">Shopping Online Inventory Feed</a> | 
<a href="/local_listings_feed">Local Listings Feed</a> | 
<a href="/refresh_feeds">Refresh feeds</a><br><br>
<small><i>version [<a href="https://github.com/guilhermechapiewski/lightspeed-custom-google-feed/commit/{version.git_commit}">{version.git_commit}</a>] deployed on [{version.deploy_timestamp}]</i></small>
'''

@app.route("/refresh_feeds")
def refresh_feeds():
    feed_gen.refresh_feed_files()
    return "New RSS feed files are ready.<br><a href='/'>Back to home</a>"

@app.route("/shopping_online_inventory_feed")
def shopping_online_inventory_feed():
    return feed_gen.read_feed_file(feed_gen.SHOPPING_ONLINE_INVENTORY_FEED_FILENAME), {'Content-Type': 'application/xml'}

@app.route("/local_listings_feed")
def local_listings_feed():
    return feed_gen.read_feed_file(feed_gen.LOCAL_LISTINGS_FEED_FILENAME), {'Content-Type': 'application/xml'}      

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--generate-feed-locally":
        try:
            logger.info("Executing from command line; refreshing feed files")
            feed_gen.refresh_feed_files()
        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            raise e
    else:
        # Run AppEngine server locally when script is invoked directly without --generate-feed-locally
        logger.info("Running AppEngine server locally")
        app.run(host="127.0.0.1", port=8080, debug=True)