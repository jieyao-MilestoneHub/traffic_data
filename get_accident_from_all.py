import os
import pandas as pd
import re
from datetime import datetime

# https://data.gov.tw/dataset/12197

class TrafficDataTransformer:
    def __init__(self, data_path, processed_data_path):
        self.data_path = data_path
        self.processed_data_path = processed_data_path

    def transform(self):
        for data_name in os.listdir(self.data_path):
            data_name_path = os.path.join(self.data_path, data_name)
            df = pd.read_csv(data_name_path)

            column_to_check = "發生地點"
            highway_name = "國道"
            df = df[df[column_to_check].str.contains(highway_name, na=False)]

            df["發生時間"] = df["發生時間"].apply(self.formatted)
            df["死亡人數"] = df["死亡受傷人數"].apply(lambda x: self.num_hurt(x, "死亡"))
            df["受傷人數"] = df["死亡受傷人數"].apply(lambda x: self.num_hurt(x, "受傷"))
            df["事故車道"] = df["發生地點"].apply(self.driveway)

            df.drop(columns=["死亡受傷人數"], inplace=True)

            processed_data_name = self.extract_key_name(data_name) + ".pkl"
            processed_path = os.path.join(self.processed_data_path, processed_data_name)
            
            try:
                df.to_pickle(processed_path)
                print(f"success to save {processed_path}")
            except Exception as e:
                print(f"error: {e}")

    def extract_key_name(self, text):
        match = re.search(r'(\d+)年度(A\d+)', text)
        if match:
            result = f"{match.group(1)}_{match.group(2)}"
        else:
            result = "No match found"
        return result

    def formatted(self, original_date):
        match = re.search(r'(\d+)年(\d+)月(\d+)日 (\d+)時(\d+)分', original_date)
        if match:
            year, month, day, hour, minute = map(int, match.groups())
            year += 1911 # 民國年轉西元年（民國1年 = 1912年）
            date_time = datetime(year, month, day, hour, minute) # 創建 datetime 對象
            return date_time.isoformat() # 輸出標準格式的日期和時間
        else:
            print("日期格式不符合預期")

    def driveway(self, way):
        if "內側" in way:
            return 0
        elif "外側" in way:
            return 1
        else:
            return None

    def num_hurt(self, input_string, keyword):
        pattern = re.compile(rf"{re.escape(keyword)}(\d+)")
        matches = pattern.findall(input_string)
        return int(matches[0])

def main():
    data_path = r"C:\Users\USER\Desktop\Develop\traffic_comp\row_data\accident"
    processed_data_path = r"C:\Users\USER\Desktop\Develop\traffic_comp\processed_data\accident"
    
    transformer = TrafficDataTransformer(data_path, processed_data_path)
    transformer.transform()

if __name__ == "__main__":
    main()
