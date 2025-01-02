# Deploy to Google App Engine
deploy: clean check_config
	@gcloud app deploy

# Configure cron job to Google App Engine
deploy_cron: clean check_config
	@gcloud app deploy cron.yaml

# Run Google App Engine application locally
run: clean check_config
	@python3 main.py

# Generate feeds locally
feed: clean check_config
	@python3 gmc_rss_gen.py

clean:
	@rm -f gmc_*_feed.xml

check_config:
	@if [ ! -f config.py ]; then \
		echo "Error: config.py file is missing. Please create a config.py file (copy config_TEMPLATE.py) with required settings."; \
		exit 1; \
	fi