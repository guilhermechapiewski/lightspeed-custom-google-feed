# Deploy to Google App Engine
deploy:
	gcloud app deploy

run:
	python3 fetch_products.py

clean:
	rm google_shopping_local_listings_feed.xml