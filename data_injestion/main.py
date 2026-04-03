from injest import download_file, extract_file, get_files



json_data = get_files()

for i in range(0, 3):
    file_path = json_data[i].get("path")
    file_size = json_data[i].get("size")
    
    downloaded_file = download_file(file_path, file_size)
    extracted_file = extract_file(downloaded_file)
    




