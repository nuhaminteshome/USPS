from injest import download_file, convert_gz_to_parquet, get_files, load_completed, save_completed
from azure_connection.azure_setup import upload_file_to_blob

from concurrent.futures import ThreadPoolExecutor
from logging_config.config import get_logger


def main():
    logger = get_logger()
    completed = load_completed()
    json_data = get_files()

    files_to_process = [
        (f["path"], f["size"])
        for f in json_data
        if f["path"] not in completed
    ]

    def process_file(args):
        file_name, file_size = args
        downloaded_file = download_file(file_name, file_size)
        if not downloaded_file:
            return file_name  
        parquet_file = convert_gz_to_parquet(downloaded_file)
        if not parquet_file:
            return file_name  

        success = upload_file_to_blob(parquet_file)
        if success:
            save_completed(file_name)

        return file_name

 
    with ThreadPoolExecutor(max_workers=3) as executor:
        list(executor.map(process_file, files_to_process))


if __name__ == "__main__":
    for i in range(5):
        main()