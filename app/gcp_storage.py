from google.cloud import storage
from typing import Optional
import os
from datetime import datetime

class GCPStorageHandler:
    def __init__(self, bucket_name: str):
        """Initialize GCP storage handler."""
        self.bucket_name = bucket_name
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    def upload_file(self, file_path: str, destination_blob_name: Optional[str] = None) -> str:
        """Upload a file to GCP storage."""
        if destination_blob_name is None:
            destination_blob_name = os.path.basename(file_path)
        
        # Add timestamp to avoid filename conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destination_blob_name = f"{timestamp}_{destination_blob_name}"
        
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_filename(file_path)
        
        return blob.public_url

    def download_file(self, source_blob_name: str, destination_file_name: str):
        """Download a file from GCP storage."""
        blob = self.bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)

    def delete_file(self, blob_name: str):
        """Delete a file from GCP storage."""
        blob = self.bucket.blob(blob_name)
        blob.delete()

    def list_files(self, prefix: str = "") -> list:
        """List files in the bucket with optional prefix."""
        blobs = self.bucket.list_blobs(prefix=prefix)
        return [blob.name for blob in blobs]

if __name__ == "__main__":
    # Initialize your storage handler with your existing bucket name
    storage_handler = GCPStorageHandler(bucket_name="rag-practice-storage")

    # Example: Upload a file
    local_file_path = "/Users/tringuyen1803/Documents/RAG/model/meta.pdf"
    public_url = storage_handler.upload_file(local_file_path)
    print(f"File uploaded to {public_url}")

    # List files in the bucket
    files = storage_handler.list_files()
    print("Files in bucket:", files)

    # Download a file from bucket
    storage_handler.download_file(files[0], "downloaded_" + files[0])
    print(f"Downloaded {files[0]} as downloaded_{files[0]}")
