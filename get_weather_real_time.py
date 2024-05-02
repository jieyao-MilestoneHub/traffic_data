# follow: https://opendata.cwa.gov.tw/dataset/observation/O-A0001-001
import requests
import pandas as pd
from dotenv import load_dotenv
import os

class WeatherDataFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"

    def fetch_data(self, dataset_id, **kwargs):
        """Fetch data from CWB Open Data API with dynamic parameters."""
        url = f"{self.base_url}/{dataset_id}"
        params = {'Authorization': self.api_key}
        params.update(kwargs)  # Update params dict with any additional keyword arguments
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch data: {response.status_code}")

    def process_data(self, data):
        """Convert nested data to pandas DataFrame."""
        # Prepare an empty list to store processed records
        records = []
        # Iterate through each station in the records
        for station in data['records']['Station']:
            # Flatten the dictionary by extracting nested data
            flattened_record = {
                'StationName': station['StationName'],
                'StationId': station['StationId'],
                'DateTime': station['ObsTime']['DateTime'],
                'StationLatitude': station['GeoInfo']['Coordinates'][0]['StationLatitude'],
                'StationLongitude': station['GeoInfo']['Coordinates'][0]['StationLongitude'],
                'StationAltitude': station['GeoInfo']['StationAltitude'],
                'CountyName': station['GeoInfo']['CountyName'],
                'TownName': station['GeoInfo']['TownName'],
                'Weather': station['WeatherElement']['Weather'],
                'Precipitation': station['WeatherElement']['Now']['Precipitation'],
                'WindDirection': station['WeatherElement']['WindDirection'],
                'WindSpeed': station['WeatherElement']['WindSpeed'],
                'AirTemperature': station['WeatherElement']['AirTemperature'],
                'RelativeHumidity': station['WeatherElement']['RelativeHumidity'],
                'AirPressure': station['WeatherElement']['AirPressure']
            }
            # Append the flattened record to the list
            records.append(flattened_record)

        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame(records)
        return df

    def save_data(self, df, filename):
        """Save DataFrame to a CSV file."""
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")

    def get_weather_data(self, dataset_id, **kwargs):
        """Fetch, process, and save weather data."""
        data = self.fetch_data(dataset_id, **kwargs)
        df = self.process_data(data)
        self.save_data(df, r'C:\Users\USER\Desktop\Develop\traffic_data\raw_data\weather\real_time\weather_real_time_data.csv')
        return df

# Usage example
if __name__ == "__main__":

    load_dotenv("./.env")
    api_key = os.getenv('API_KEY')
    dataset_id = 'O-A0001-001'
    fetcher = WeatherDataFetcher(api_key)
    weather_df = fetcher.get_weather_data(dataset_id)