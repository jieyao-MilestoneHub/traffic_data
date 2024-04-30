import pickle
import pandas as pd

# 從 .pkl 文件中讀取數據
data_path = r"C:\Users\USER\Desktop\Develop\traffic_data\processed_data\accident_highway\accident_highway_2024_4_1.pkl"
df = pd.read_pickle(data_path)
print(df.head())
print(df.info())