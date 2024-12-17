import flask
import gmc_rss_gen

app = flask.Flask(__name__)

@app.route("/")
def root():
    return "It's working!"

@app.route("/refresh_feed")
def refresh_feed():
    gmc_rss_gen.main()
    return "RSS feed generated."

@app.route("/feed")
def feed():
    return flask.send_file("google_shopping_local_listings_feed.xml", mimetype="application/xml")

if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host="127.0.0.1", port=8080, debug=True)