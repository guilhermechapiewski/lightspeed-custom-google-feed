import os
import flask
import gmc_rss_gen

app = flask.Flask(__name__)

cloud = False
if os.environ.get("RUNNING_ON_CLOUD"):
    cloud = True

@app.route("/")
def root():
    return "It's working!"

@app.route("/refresh_feed")
def refresh_feed():
    gmc_rss_gen.refresh_feed_file(cloud)
    return "RSS feed generated."

@app.route("/feed")
def feed():
    return gmc_rss_gen.read_feed_file(cloud), {'Content-Type': 'application/xml'}

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)