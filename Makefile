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

clean:
	@rm -f gmc_*_feed.xml

check_config:
	@if [ ! -f config.py ]; then \
		echo "Error: config.py file is missing. Please create a config.py file (copy config_TEMPLATE.py) with required settings."; \
		exit 1; \
	fi

create_deployment_info:
	@echo "Creating/updating version.py with latest git commit version and timestamp..."
	@echo "# AUTO-GENERATED file - run 'make deploy' or 'make create_deployment_info' to update" > version.py
	@echo "git_commit = '`git rev-parse HEAD`'" >> version.py
	@echo "deploy_timestamp = '`date '+%Y-%m-%d %H:%M:%S'`'" >> version.py