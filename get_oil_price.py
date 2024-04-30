import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

def calculate_middle_date(date1, date2):
    """計算兩個日期之間的中間日期"""
    return date1 + (date2 - date1) / 2

def fill_date(df, date_name="調價日期"):

    # 試著解析日期時間字串為日期，忽略時間
    df[date_name] = pd.to_datetime(df[date_name], format='%Y/%m/%d', errors='coerce')

    # 填入無效的日期
    valid_indices = df[df[date_name].notna()].index
    for i in df[df[date_name].isna()].index:
        previous_valid_index = valid_indices[valid_indices < i].max()
        next_valid_index = valid_indices[valid_indices > i].min()
        
        # 如果存在前後有效日期，則計算中間日期
        if pd.notna(previous_valid_index) and pd.notna(next_valid_index):
            previous_date = df.loc[previous_valid_index, date_name]
            next_date = df.loc[next_valid_index, date_name]
            df.at[i, date_name] = calculate_middle_date(previous_date, next_date)
        else:
            # 如果沒有有效的前後日期，可以選擇填入固定日期或其他邏輯
            df.at[i, date_name] = pd.NaT # 或 pd.Timestamp('some_date')

    return df

def get_raw_data(file_path):
    
    iframe_recent = "https://vipmbr.cpc.com.tw/mbwebs/ShowHistoryPrice_oil.aspx"
    iframe_far = "https://vipmbr.cpc.com.tw/mbwebs/ShowHistoryPrice_oil2019.aspx"
    iframes = [iframe_recent, iframe_far]

    df = pd.DataFrame()
    
    for iframe_src in iframes:

        iframe_response = requests.get(iframe_src)
        iframe_soup = BeautifulSoup(iframe_response.text, 'html.parser')

        # 找到表格
        table = iframe_soup.find('table', {'id': 'MyGridView'})

        # 讀取所有行
        rows = table.find_all('tr')

        # 取得表頭
        headers = [header.get_text() for header in rows[0].find_all('th')]

        data = []

        # 遍歷表格的每一行，除了表頭
        for row in rows[1:]:
            cols = row.find_all('td')
            cols = [ele.text.strip() if ele.text.strip() else '' for ele in cols]
            data.append(cols)

        temp_df = pd.DataFrame(data, columns=headers)

        if df.empty:
            df = temp_df
        else:
            df = pd.concat([df, temp_df])

    df = fill_date(df)
    df.to_csv(file_path, index=False)




def transform_data(input_file, output_file):
    df = pd.read_csv(input_file, parse_dates=["調價日期"], index_col=["調價日期"])
    df = df.iloc[:, :3]
    full_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')
    df_filled = df.reindex(full_range).ffill()
    df_filled.to_csv(output_file, index_label="調價日期")


if __name__ == "__main__":

    folder_path = r"C:\Users\USER\Desktop\Develop\traffic_data\raw_data\oil"
    csv_name = "gasoline_diesel_fuel.csv"
    file_path = os.path.join(folder_path, csv_name)
    
    get_raw_data(file_path)
    

    input_file = r"C:\Users\USER\Desktop\Develop\traffic_data\raw_data\oil\gasoline_diesel_fuel.csv"
    folder_path = r"C:\Users\USER\Desktop\Develop\traffic_data\processed_data\oil"
    csv_name = "gasoline_diesel_fuel.pkl"
    output_file = os.path.join(folder_path, csv_name)

    transform_data(input_file, output_file)