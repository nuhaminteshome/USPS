from injest_utils import *

import requests
import gzip


def download_data(file_path):
    base_url = "https://spm.usps.com/api/extract/download/"

    with open(requests.get(base_url + file_path, stream=True)) as r:
        r.raise_for_status()

        with open(file_path, "wb") as file:
            for chunk in r.iter_content(chunk_size=65536):
                if chunk:
                    file.write(chunk)


        


download_data("extract0.gz")
