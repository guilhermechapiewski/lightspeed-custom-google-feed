# Deploy to Google App Engine
deploy: clean check_config create_deployment_info
	@echo "Deploying to Google App Engine..."
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

# Check if config.py file exists
check_config:
	@if [ ! -f config.py ]; then \
		echo "Error: config.py file is missing. Please create a config.py file (copy config_TEMPLATE.py) with required settings."; \
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

# Run tests
test:
	@nose2

# Run tests with coverage
test_coverage:
	@nose2 --with-coverage