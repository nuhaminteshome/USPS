from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv

from logging_config.config import get_logger

load_dotenv()



container_name = os.getenv("CONTAINER_NAME")
connection_string = os.getenv("CONNECTION_STRING")

blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service_client.get_container_client(container_name)


logger = get_logger()

def upload_file_to_blob(file_path: str) -> bool:
    file_name = os.path.basename(file_path)
    blob_client = container_client.get_blob_client(file_name)

    try: 
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
    
        os.remove(file_path)

        logger.info(f"Uploaded: {file_name}")
        return True 
    except Exception as e:
        logger.error(f"Failed to upload {file_name}: {e}")
        return False
