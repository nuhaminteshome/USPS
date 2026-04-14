import requests
import gzip
import os

from logging_config.config import get_logger

import polars as p
import random

import time

DOWNLOAD_FOLDER = "extracted_data"
CHECKPOINT_FILE = "completed.txt"

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
def download_file(file_name: str, expected_size: int, retries: int = 5) -> str | None:
    base_url = "https://spm.usps.com/api/extract/download/"
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_FOLDER, file_name)

    if os.path.exists(file_path):
        logger.info(f"File exists, validating: {file_name}")
        actual_size = os.path.getsize(file_path)
        if actual_size == expected_size:
            return file_path
        else:
            logger.warning(
                f"Existing file invalid, deleting: {file_name} "
                f"(expected {expected_size}, got {actual_size})"
            )
            os.remove(file_path)

    delay = 1

    for attempt in range(1, retries + 1):
        try:
            with requests.get(base_url + file_name, stream=True, timeout=30) as r:
                r.raise_for_status()

      
                with open(file_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=65536):
                        if chunk:
                            f.write(chunk)

            actual_size = os.path.getsize(file_path)
            if actual_size != expected_size:
                logger.error(
                    f"Size validation failed: {file_name} "
                    f"(expected {expected_size}, got {actual_size})"
                )
                os.remove(file_path)
                raise Exception("File size mismatch")

            logger.info(f"Downloaded successfully: {file_path}")
            return file_path

        except Exception as e:
            logger.warning(f"Attempt {attempt} failed for {file_name}: {e}")
            if attempt < retries:
                sleep_time = delay + random.uniform(0, 1)
                logger.info(f"Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                delay *= 2
            else:
                logger.error(f"Failed to download {file_name} after {retries} attempts")
                return None

def convert_gz_to_parquet(file_path: str) -> str | None:
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    output_file = os.path.basename(file_path).replace(".gz", ".parquet")
    output_path = os.path.join(DOWNLOAD_FOLDER, output_file)

    try:
        with gzip.open(file_path, "rt") as f:
            df = p.read_csv(f)

        df.write_parquet(output_path)

        logger.info(f"Converted to parquet: {output_path}")

        os.remove(file_path)  
        return output_path

    except Exception as e:
        logger.error(f"Failed to convert {file_path}: {e}")
        return None
    
def load_completed():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            return set(f.read().splitlines())
    return set()

def save_completed(file_name: str):
    with open(CHECKPOINT_FILE, "a") as f:
        f.write(file_name + "\n")