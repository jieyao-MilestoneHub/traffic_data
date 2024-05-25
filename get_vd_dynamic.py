import requests
from bs4 import BeautifulSoup
import datetime
import re
import os
from concurrent.futures import ThreadPoolExecutor
import threading

class GCSFileDownloader:
    def __init__(self, base_url, pattern, save_root):
        self.base_url = base_url
        self.pattern = re.compile(pattern)
        self.save_root = save_root  # Root directory for saving files
        self.lock = threading.Lock()  # Lock for thread-safe file operations

    def fetch_files(self, date_list):
        with ThreadPoolExecutor(max_workers=10) as executor:  # Increase max_workers for better concurrency
            results = [executor.submit(self.process_date, date_str) for date_str in date_list]
            for future in results:
                try:
                    future.result()
                except Exception as e:
                    print(f"Error processing date: {e}")

    def process_date(self, date_str):
        url = f"{self.base_url}{date_str}/"
        print(f"Processing URL: {url}")  # Log the URL being processed
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"No data available for {date_str}: {e}")
            return

        html = BeautifulSoup(response.text, 'html.parser')
        found = False

        for link in html.find_all('a', href=self.pattern):
            if self.pattern.match(link.text):
                file_url = url + link['href']
                # Create directory by year and month
                year_month = date_str[:6]  # First six characters are the year and month
                save_directory = os.path.join(self.save_root, year_month)
                os.makedirs(save_directory, exist_ok=True)
                save_path = os.path.join(save_directory, link.text)
                with self.lock:
                    if not os.path.exists(save_path):
                        self.download_file(file_url, save_path)
                    else:
                        print(f"File already exists: {save_path}")
                found = True

        if not found:
            print(f"No matching files found on {date_str}")

    def download_file(self, file_url, file_name):
        print(f"Downloading file from {file_url} to {file_name}")  # Log file download
        try:
            response = requests.get(file_url)
            response.raise_for_status()
            with open(file_name, 'wb') as file:
                file.write(response.content)
            print(f"Successfully downloaded {file_name}")
        except requests.RequestException as e:
            print(f"Failed to download {file_name}: {e}")

if __name__ == "__main__":
    base_url = "https://tisvcloud.freeway.gov.tw/history/motc20/VD/"
    pattern = r"VDLive_\d+\.xml\.gz"
    save_root = r"C:\Users\USER\Desktop\Develop\traffic_data\raw_data\vd_dynamic"  # Root path to save files

    downloader = GCSFileDownloader(base_url, pattern, save_root)

    # Generate date list for January to October 2023
    start_date = datetime.datetime(2023, 1, 1)
    end_date = datetime.datetime(2023, 10, 31)
    date_generated = [start_date + datetime.timedelta(days=x) for x in range(0, (end_date-start_date).days + 1)]

    date_list = [date.strftime("%Y%m%d") for date in date_generated]
    downloader.fetch_files(date_list)
