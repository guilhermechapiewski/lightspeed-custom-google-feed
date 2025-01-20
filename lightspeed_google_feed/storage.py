from google.cloud import storage
import logging
from config import CLOUD_STORAGE_BUCKET_NAME

class Storage:

    def __init__(self, cloud=False):
        self.logger = logging.getLogger(__name__)
        self.cloud = cloud

    def save_file(self, filename, content):
        if self.cloud:
            # Save to Google Cloud Storage bucket
            self.storage_client = storage.Client()
            bucket = self.storage_client.bucket(CLOUD_STORAGE_BUCKET_NAME)
            
            blob = bucket.blob(filename)
            blob.upload_from_string(content, content_type='application/xml')
            self.logger.info(f"File saved to Google Cloud Storage: {filename}")
        else:
            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.info(f"File saved to local filesystem: {filename}")

    def read_file(self, filename):
        if self.cloud:
            try:
                storage_client = storage.Client()
                bucket = storage_client.bucket(CLOUD_STORAGE_BUCKET_NAME)
                blob = bucket.blob(filename)
                return blob.download_as_string()
            except Exception as e:
                self.logger.error(f"Error reading file [{filename}] from Google Cloud Storage: {e}")
                return "<error>Feed file not found. Please generate a feed first.</error>"
        else:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    return f.read()
            except FileNotFoundError:
                self.logger.error(f"File not found: {filename}")
            return "<error>Feed file not found. Please generate a feed first.</error>"