# Deploy to Google App Engine
deploy: clean check_config create_deployment_info test
	@echo "Deploying to Google App Engine..."
	@gcloud app deploy

# Configure cron job to Google App Engine
deploy_cron: clean check_config
	@gcloud app deploy cron.yaml

# Run Google App Engine application locally
run: clean check_config
	@python3 main.py

# Run tests
test: clean
	@pytest

# Run tests with coverage
coverage: test_coverage
test_coverage: clean
	@pytest --cov=./lightspeed_google_feed/

# Generate feeds locally
feed: clean check_config
	@python3 main.py --generate-feed-locally

# Refresh feeds on remote server
remote_refresh_feeds:
	@echo "Refreshing feeds on remote server..."
	@FEED_SERVER=`gcloud app describe | grep -e defaultHostname | cut -d ":" -f 2 | cut -d " " -f 2`; \
	echo "Server = $$FEED_SERVER"; \
	curl "https://$$FEED_SERVER/refresh_feeds"
	@echo "\nDone."

# Clean up generated feeds
clean:
	@rm -f gmc_*_feed.xml
	@rm -f version.py
	@rm -f test.xml

# Check if config.py file exists
check_config:
	@if [ ! -f ./lightspeed_google_feed/config.py ]; then \
		echo "Error: ./lightspeed_google_feed/config.py file is missing. Please create a config.py file (copy config_TEMPLATE.py) inside the "lightspeed_google_feed" directory with the required settings."; \
		exit 1; \
	fi

# Create/update version.py with latest git commit version and timestamp
create_deployment_info:
	@echo "Creating/updating version.py with latest git commit version and timestamp..."
	@echo "# AUTO-GENERATED file - run 'make deploy' or 'make create_deployment_info' to update" > version.py
	@echo "git_commit = '`git rev-parse HEAD`'" >> version.py
	@echo "deploy_timestamp = '`date '+%Y-%m-%d %H:%M:%S'`'" >> version.py

# Install development requirements
install_requirements:
	@pip3 install -r requirements.txt
	@pip3 install -r requirements-dev.txt