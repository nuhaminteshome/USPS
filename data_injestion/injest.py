import requests
import gzip
import shutil
import os

from logging_config.config import get_logger

DOWNLOAD_FOLDER = "extracted_data"

logger = get_logger()


'''
Gets the list of all the files from the USPS API in JSON format

Return:
The JSON of files as a list
'''
def get_files() -> list[dict]:
    url = "https://spm.usps.com/api/extract/files"

    response = requests.get(url)

    response.raise_for_status()

    return response.json()

def validate_file_size(file_path: str, expected_size: int) -> bool:
    actual_size = os.path.getsize(file_path)
    if actual_size != expected_size:
        logger.warning(f"File size mismatch: {file_path} (expected {expected_size}, got {actual_size})")
        return False
    return True
'''
Downloads a .gz file of a given file_path into a folder based on DOWNLOAD_FOLDER

Parameters:
file_name: a "extractn.gz" file, where n is represented by a number corresponding to the file number

Returns:
None
'''

def download_file(file_name: str, expected_size: int) -> str | None:
    base_url = "https://spm.usps.com/api/extract/download/"
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    file_path = os.path.join(DOWNLOAD_FOLDER, file_name)

    if os.path.exists(file_path):
        logger.info(f"File already exists, checking validity: {file_name}")

        if validate_file_size(file_path, expected_size):
            return file_path
        else:
            logger.warning(f"Existing file invalid, redownloading: {file_name}")
            os.remove(file_path)

    try:
        with requests.get(base_url + file_name, stream=True) as r:
            r.raise_for_status()

            with open(file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)

        if not validate_file_size(file_path, expected_size):
            logger.error(f"Downloaded file failed size validation: {file_name}")
            os.remove(file_path)
            return None

        logger.info(f"Downloaded successfully: {file_path}")
        return file_path

    except Exception as e:
        logger.error(f"Failed to download {file_name}: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)

        return None


def extract_file(file_path: str) -> str:
    output_file = file_path.replace(".gz", "")

    try:
        with gzip.open(file_path, "rb") as file_in:
            with open(output_file, "wb") as file_out:
                shutil.copyfileobj(file_in, file_out)

        
        if not os.path.exists(output_file):
            raise Exception("Extraction failed: output file not created")
        
        os.remove(file_path)
        logger.info(f"Successfully extracted and deleted: {file_path}")

        return output_file

    except Exception as e:
        logger.error(f"Failed to extract {file_path}: {e}")
        return None