import requests


def get_files():
    url = "https://spm.usps.com/api/extract/files"

    return requests.get(url).json()