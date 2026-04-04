from injest import download_file, convert_gz_to_parquet, get_files, load_completed, save_completed

import time

import polars as p

from logging_config.config import get_logger

json_data = get_files()

completed = load_completed()

logger = get_logger()

def main():
    for file_info in json_data:
        file_name = file_info["path"]
        file_size = file_info["size"]

        if file_name in completed:
            logger.info(f"Skipping completed: {file_name}")
            continue

        downloaded_file = download_file(file_name, file_size)

        if downloaded_file:
            parquet_file = convert_gz_to_parquet(downloaded_file)

            if parquet_file:
                save_completed(file_name)


if __name__ == "__main__":
    main()



