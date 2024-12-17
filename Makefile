# Deploy to Google App Engine
deploy:
	gcloud app deploy

run:
	python3 gmc_rss_gen.py

clean:
	rm google_shopping_local_listings_feed.xml