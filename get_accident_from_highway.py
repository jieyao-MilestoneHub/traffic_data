import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import pandas as pd

class TrafficIncidentScraper:
    def __init__(self, inc_name, inc_area):
        '''
        param
        inc_name: 事故名稱
        inc_area: 事故地區 
        '''
        self.inc_name = inc_name
        self.inc_area = inc_area
        self.validate_inputs()
    
    def validate_inputs(self):
        if self.inc_name not in ["全部", "車禍事故", "故障車", "機車誤闖", "車輛火災", "邊坡起火", "行人誤闖"]:
            raise ValueError("查無此事件名稱")
        if self.inc_area not in ["全台", "北部", "中部", "南部", "東部"]:
            raise ValueError("查無此地區")
        print(f"您選擇查找的事件為: {self.inc_name}")
        print(f"您選擇查找的地區為: {self.inc_area}")

        url_area_dict = {"全台": "A", "北部": "N", "中部": "C", "南部": "S", "東部": "P"}
        self.inc_area = url_area_dict[self.inc_area]

    def get_specific_html(self, year, month, day):
        if not all(isinstance(x, int) and x > 0 for x in [year, month, day]):
            return "Invalid date provided."
        params = {'inc_name': self.inc_name, 'inc_area': self.inc_area, 'submit': 'submit'}
        query_string = urlencode(params)

        if month < 10:
            month = f"0{month}"
        if day < 10:
            day = f"0{day}"

        url = f"https://www.1968services.tw/history-incident/{year}-{month}-{day}?{query_string}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            return f"An error occurred: {e}"

    def scrape_data(self, years, months, days):
        '''
        param: 整數組成的 list - 抓取x年x月x日的事故歷史資訊
        '''
        for year in years:
            for month in months:
                for day in days:
                    try:
                        df = pd.DataFrame(columns=["time", "type", "location", "remarks", "latitude", "longitude"])
                        html = self.get_specific_html(year, month, day)
                        if isinstance(html, str) and html.startswith("Error"):
                            print(html)
                            continue
                        soup = BeautifulSoup(html, 'html.parser')
                        div_elements = soup.select('div.w3-card-4.w3-container.w3-white')

                        print(f"Processed {year}-{month}-{day}: Found {len(div_elements)} elements")
                        if len(div_elements) == 0:
                            continue

                        for div in div_elements:
                            data = self.get_accident_detail(div)
                            new_row = pd.DataFrame([data], columns=df.columns)
                            df = pd.concat([df, new_row], ignore_index=True)

                        df.to_pickle(f"C:/Users/USER/Desktop/Develop/traffic_comp/processed_data/accident_highway/accident_highway_{year}_{month}_{day}.pkl")

                    except Exception as e:
                        print(f"Error processing {year}-{month}-{day}: {str(e)}")

    def get_accident_detail(self, div):
        time_ = div.find(string="時間").find_next('td').text
        type_ = div.find(string="類型").find_next('td').text
        location = div.find(string="地區").find_next('td').text
        remarks = div.find(string="備註").find_next('td').text
        remarks = remarks.split(" ")[0]
        coordinates = div.find(string="座標").find_next('td').contents[0].strip()
        lat, lon = coordinates.split(', ')
        return time_, type_, location, remarks, lat, lon

if __name__ == "__main__":
    # Example usage
    scraper = TrafficIncidentScraper("全部", "全台")
    scraper.scrape_data([2024-i for i in range(20)], [i for i in range(1,13)], [i for i in range(1,32)])