from google.cloud import storage
import logging
from config import CLOUD_STORAGE_BUCKET_NAME

logger = logging.getLogger(__name__)

def save_file(filename, content, cloud=False):
    if cloud:
        # Save to Google Cloud Storage bucket
        storage_client = storage.Client()
        bucket = storage_client.bucket(CLOUD_STORAGE_BUCKET_NAME)
        
        blob = bucket.blob(filename)
        blob.upload_from_string(content, content_type='application/xml')
        logger.info(f"File saved to Google Cloud Storage: {filename}")
    else:
        # Save to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"File saved to local filesystem: {filename}")

def read_file(filename, cloud=False):
    if cloud:
        storage_client = storage.Client()
        bucket = storage_client.bucket(CLOUD_STORAGE_BUCKET_NAME)
        blob = bucket.blob(filename)
        return blob.download_as_string()
    else:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"File not found: {filename}")
            return "<error>Feed file not found. Please generate a feed first.</error>"