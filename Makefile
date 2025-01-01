# Deploy to Google App Engine
deploy: clean
	gcloud app deploy

feed: clean
	python3 gmc_rss_gen.py

run: clean
	python3 main.py

clean:
	rm -f gmc_*_feed.xml