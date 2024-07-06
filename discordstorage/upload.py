import requests
import os

# Uploads file to gofile.io and returns the download link
def upload_to_gofile(file_path):
    url = 'https://store1.gofile.io/contents/uploadfile'

    try:
        # Get file size
        file_size = os.path.getsize(file_path)
        print(f"Uploading {file_path} (size: {get_human_readable(file_size)})")
        print("")
        print("This may take a while depending on the file size.\n")
        print("")

        # Open file and prepare for upload
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(url, files=files)

            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'ok':
                    download_link = data['data']['downloadPage']
                    print(f"Uploaded successfully: {download_link}")
                else:
                    print(f"Upload failed for {file_path}")
            else:
                print(f"Failed to upload {file_path}. Status code: {response.status_code}")

    except FileNotFoundError:
        print(f"File not found: {file_path}")

# Function to convert file size to human-readable format
def get_human_readable(size, precision=2):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
    suffix_index = 0
    while size > 1024 and suffix_index < 4:
        suffix_index += 1
        size = size / 1024.0
    return "%.*f %s" % (precision, size, suffixes[suffix_index])