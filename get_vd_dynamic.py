import requests
from bs4 import BeautifulSoup
import datetime
import re
import os

class GCSFileDownloader:
    def __init__(self, base_url, pattern):
        self.base_url = base_url
        self.pattern = re.compile(pattern)

    def fetch_files(self):
        date = datetime.datetime.now()
        while True:
            date_str = date.strftime('%Y%m%d')
            url = f"{self.base_url}{date_str}/"

            response = requests.get(url)
            if response.status_code != 200:
                print(f"No data available for {date_str}")
                break

            html = BeautifulSoup(response.text, 'html.parser')
            found = False

            for link in html.find_all('a', href=self.pattern):
                if self.pattern.match(link.text):
                    file_url = url + link['href']
                    save_path = os.path.join(r"C:\Users\USER\Desktop\Develop\traffic_data\raw_data\vd_dynamic", link.text)
                    self.download_file(file_url, save_path)
                    found = True

            if not found:
                print(f"No matching files found on {date_str}")
                break

            date -= datetime.timedelta(days=1)

    def download_file(self, file_url, file_name):
        response = requests.get(file_url)
        if response.status_code == 200:
            with open(file_name, 'wb') as file:
                file.write(response.content)
            print(f"Successfully downloaded {file_name}")
        else:
            print(f"Failed to download {file_name}")

if __name__ == "__main__":

    # Example
    base_url = "https://tisvcloud.freeway.gov.tw/history/motc20/VD/"
    pattern = r"VDLive_\d+\.xml\.gz"
    downloader = GCSFileDownloader(base_url, pattern)
    downloader.fetch_files()