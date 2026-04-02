import requests
import gzip
import shutil
import os

from logging_config.config import get_logger

DOWNLOAD_FOLDER = "extracted_data"

logger = get_logger()


def get_files():
    url = "https://spm.usps.com/api/extract/files"

    return requests.get(url).json()



'''
Downloads a .gz file of a given file_path into a folder based on EXTRACTED_FOLDER

Parameters:
file_name: a "extractn.gz" file, where n is represented by a number corresponding to the file number

Returns:
None
'''
def download_file(file_name: str) -> str:
    base_url = "https://spm.usps.com/api/extract/download/"
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_FOLDER, file_name)

    if os.path.exists(file_path):
        logger.info(f"File already exists, skipping: {file_name}")
        return file_path 
    try:
        with requests.get(base_url + file_name, stream=True) as r:
            r.raise_for_status()

            with open(file_path, "wb") as file:
                for chunk in r.iter_content(chunk_size=65536):
                    if chunk:
                        file.write(chunk)
        
        logger.info(f"Downloaded: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Failed to download {file_name}: {e}")
        return None

def extract_file(file_path: str) -> None:
    output_file = file_path.replace(".gz", "")

    with gzip.open(file_path, "rb") as file_in:
        with open(output_file, 'wb') as file_out:
            shutil.copyfileobj(file_in, file_out)   
    try:
        os.remove(file_path)
        logger.info(f"Sucessfully deleted{file_path}")
    except FileNotFoundError:
        print(f"The file {file_path} does not exist")
    
    return output_file
